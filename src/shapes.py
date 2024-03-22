import geopandas as gpdpip

from genericpath import exists
import os
import glob
import doit
import glob
import os
import numpy as np
from doit import create_after
import numpy as np
import geopandas as gp
import pandas as pd
from pathlib import Path
import shutil

from shapely.geometry import MultiPoint


def convert_wgs_to_utm(lon, lat):
    utm_band = str(int((np.floor((lon + 180) / 6 ) % 60) + 1))
    if len(utm_band) == 1:
        utm_band = '0'+utm_band
    if lat >= 0:
        epsg_code = '326' + utm_band
    else:
        epsg_code = '327' + utm_band
    return epsg_code


        
  
def task_make_overlaps():
    def process_overlap(dependencies, targets,gridsize=10):
        gdfs = [gp.read_file(shapefile) for shapefile in dependencies]
        intersection = gdfs[0]  # Initialize with the first GeoDataFrame
        for gdf in gdfs[1:]:
            intersection = gp.overlay(intersection, gdf, how='intersection')
        
        intersection.to_file(targets[0], driver="GPKG")     



    file_dep = Path('/media/mor582/My Passport/Work/Projects/Seagrasslossdrone/').rglob('*_footprint.gpkg')
    df = pd.DataFrame(file_dep,columns=['FileName'])
    df['Site']=df.FileName.apply(lambda x: x.parts[-3])
    df['Year']=df.FileName.apply(lambda x: x.parts[-2])
    for index,group in df.groupby('Site'):
        tar =group['FileName'].iloc[0]
        target = (tar.parent.parent / (tar.parent.parent.name+'_overlap')).with_suffix('.gpkg')
        yield {
            'name':target,
            'actions':[(process_overlap,[],{'gridsize':5})],
            'file_dep':group.FileName.to_list(),
            'targets':[target],
            'clean':True,
        }      


@create_after(executed='make_overlaps')         
def task_make_grids():
    def process_grid(dependencies, targets,gridsize=10):
        area = gp.read_file(dependencies[0])
        utmcode = convert_wgs_to_utm(area.iloc[0].geometry.convex_hull.exterior.coords.xy[0][0],area.iloc[0].geometry.convex_hull.exterior.coords.xy[1][0])
        crs = f'epsg:{utmcode}' 
        polygon = area.to_crs(crs).iloc[0].geometry.convex_hull
        eastings =polygon.exterior.coords.xy[0]
        northings =polygon.exterior.coords.xy[1]
        easting =np.arange(np.min(eastings) -np.min(eastings) % gridsize,np.max(eastings) -np.max(eastings) % gridsize,gridsize)
        northing=np.arange(np.min(northings) -np.min(northings) % gridsize,np.max(northings) -np.max(northings) % gridsize,gridsize)
        xi,yi = np.meshgrid(easting,northing)
        points =  MultiPoint(list(zip(xi.ravel(),yi.ravel())))
        p =points.intersection(area.to_crs(crs).iloc[0].geometry)
        aoi = gp.read_file('/media/mor582/My Passport/Work/Projects/Seagrasslossdrone/area_of_interest.gpkg')
        result = list(filter(lambda x: not x.is_empty,p.intersection(aoi.geometry.to_list())))
        output = []
        for i in result:
            for point in i.geoms:
                output.append(point.buffer(5, cap_style = 3))
        df =gp.GeoDataFrame(geometry=output, crs=crs).sample(30)
        df['Habitat'] = ''
        df['Species'] = ''
        df['Density'] = ''
        df['Coverage'] = -999.0
        df['Note'] =''
        df.to_file(targets[0])        
      



    file_dep = Path('/media/mor582/My Passport/Work/Projects/Seagrasslossdrone/').rglob('*overlap.gpkg')
    gridsize=25
    for file in file_dep:
        target = file.parent / (file.stem + f'_{gridsize}_grid.gpkg')
        yield {
            'name':target,
            'actions':[(process_grid,[],{'gridsize':gridsize})],
            'file_dep':[file],
            'targets':[target],
            'clean':True,
        }           

@create_after(executed='make_grids')         
def task_make_years():
    def process_year(dependencies, targets,gridsize=10):
          for dest in targets:
            shutil.copy(dependencies[0],dest)  



    file_dep = Path('/media/mor582/My Passport/Work/Projects/Seagrasslossdrone/').rglob('*_grid.gpkg')
    for file in file_dep:
        dirs = list(filter(lambda x: x.is_dir(),file.parent.glob('*')))
        target = list(map(lambda x:(file.parent / (file.stem +'_'+x.parts[-1] + '.gpkg') ),dirs))
        yield {
            'name':file,
            'actions':[(process_year)],
            'file_dep':[file],
            'targets':target,
            'clean':True,
        }     

if __name__ == '__main__':
    import doit
    DOIT_CONFIG = {'check_file_uptodate': 'timestamp'}
    #print(globals())
    doit.run(globals())           