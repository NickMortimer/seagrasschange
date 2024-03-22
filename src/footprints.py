from osgeo import gdal
from pathlib import Path
from tqdm import tqdm
from pathlib import Path


def footprint(filename,output):
    data =gdal.Open(filename)
    #gdal.SetConfigOption("GTIFF_SRS_SOURCE", "EPSG")
    options =gdal.FootprintOptions(dstSRS='EPSG:4326',format="GPKG")
    gdal.Footprint(output, data, options=options)


if __name__ == '__main__':
    files = Path('/media/mor582/My Passport/Work/Projects/Seagrasslossdrone/').rglob('*.tif')
    for file in tqdm(files):
        pgfile = file.parent / (file.stem + '_footprint.gpkg')
        if not pgfile.exists():
            print(file)
            footprint(file,pgfile)


#export PROJ_LIB=/home/mor582/mambaforge-pypy3/envs/gdal/share/proj