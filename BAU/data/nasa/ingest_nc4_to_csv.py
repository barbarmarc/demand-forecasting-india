import os
from multiprocessing import Pool

import netCDF4 as nc4
import numpy as np
import pandas as pd

import config

NUM_THREADS = 10

output = open('missing_files.txt', "a")


def get_mean(arr):
    tot = 0
    for row in arr:
        for col in row:
            tot += col
    return tot/(len(arr)*len(arr[0]))


def process(params):
    """
    process nc4 for particular city for particular data field into pandas df
    """
    city, region, = params
    data = {}
    for nasa_name, field in config.fields.items():
        data[field] = []
    files = [f"test/{city}/{f}" for f in os.listdir(f"test/{city}/") if f.endswith(".nc4")]
    print(f'processing {len(files)} files for city {city}')
    for f in files:
        try:
            nc = nc4.Dataset(f)
            time_var = nc.variables['time']
            dtime = nc4.num2date(time_var[:], time_var.units)
            for i in range(24):
                for nasa_name, field in config.fields.items():
                    data[field].append(pd.Series(
                        get_mean(nc.variables[nasa_name][i]),
                        index=[dtime[i]])
                    )
        except OSError:
            output.write(f)
            
    for field, res_list in data.items():
        res = pd.concat(res_list, axis=0)
        res.sort_index(inplace=True)
        outdir = f'test/{region}'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        res.to_csv(f'{outdir}/{city}_{field}.csv', index=True, header=False)


datafields = config.fields.values()

params = []
for region, city_list in config.cities.items():
    for city in city_list:
        params.append((city, region))


with Pool(NUM_THREADS) as p:
    p.map(process, params)


