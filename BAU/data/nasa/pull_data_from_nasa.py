import os, sys, urllib, requests, site, base64
from multiprocessing import Pool
from urllib.error import HTTPError
import pandas as pd

import config

NUM_THREADS = 12
MIN_SIZE = 100000 # min size of file to skip pull
outpath = 'test/'

##########
### INPUTS

#dates = pd.date_range('2014-01-01','2014-01-15',freq='D')[::-1]
dates = pd.date_range('2014-01-01','2019-12-31',freq='D')[::-1]

coords = {}
for region, city_list in config.cities.items():
    for city, city_coords in city_list.items():
        lat, lon = city_coords
        coords[city] = (int((lat+90.0)/.5), int((lon+180)/.625))

for city in coords:
    dir_ = f"{outpath}{city}"
    if not os.path.exists(dir_):
        os.mkdir(dir_)

query_params = []

for city, coord in coords.items():
    for date in dates:
        query_params.append((date, coord[0], coord[1], city))


def get_lat_lon_in_query(latitude, longitude):
    return f"[{latitude}:{latitude+1}][{longitude}:{longitude+1}]"

def get_query(date, latitude, longitude):
    query = (
        f"https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2I1NXASM."
        f"5.12.4/{date.year}/{date.month:02}/MERRA2_400.inst1_2d_asm_Nx."
        f"{date.strftime('%Y%m%d')}.nc4.nc4?"
    )
    fields = [f"{field}[0:23]{get_lat_lon_in_query(latitude, longitude)}"
              for field in config.fields]
    query += ",".join(fields)
        
    query += (
        f',time,'
        f'lat[{latitude}:{latitude+1}],'
        f'lon[{longitude}:{longitude+1}]'
    )
    return query


def process(args):
    date, lat, lon, city = args

    dir_ = f"{outpath}{city}"
    savename = f"{dir_}/{date.strftime('%Y%m%d')}.nc4"
    if os.path.exists(savename) and os.stat(savename).st_size > MIN_SIZE:
        return

    ### Generate new query
    query = get_query(date, lat, lon)
    
    attempts = 0
    while attempts < 10:
        try:
            r = requests.get(query)
            with open(savename, 'wb') as f:
                f.write(r.content)
            break
        except HTTPError as err:
            print(
                'Rebuffed on attempt # {} at {} by "{}".'
                'Will retry in 60 seconds.'.format(
                    attempts, nowtime(), err))
            attempts += 1
            time.sleep(60)

with Pool(NUM_THREADS) as p:
    p.map(process, query_params)

