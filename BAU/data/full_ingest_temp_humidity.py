import netCDF4
import numpy as np
import pandas as pd
import os


def get_mean(arr):
    tot = 0
    for row in arr:
        for col in row:
            tot += col
    return tot/(len(arr)*len(arr[0]))


files = [f for f in os.listdir(".") if f.endswith(".nc4")]

temp_10 = []
temp_2 = []
hum_10 = []
hum_2 = []


for f in files:
    nc = netCDF4.Dataset(f)
    time_var = nc.variables['time']
    dtime = netCDF4.num2date(time_var[:], time_var.units)
    for i in range(24):
        temp_10.append(pd.Series(
            get_mean(nc.variables['T10M'][i]),
            index=[dtime[i]])
        )
        temp_2.append(pd.Series(
            get_mean(nc.variables['T2M'][i]),
            index=[dtime[i]])
        )
        hum_10.append(pd.Series(
            get_mean(nc.variables['QV10M'][i]),
            index=[dtime[i]])
        )
        hum_2.append(pd.Series(
            get_mean(nc.variables['QV2M'][i]),
            index=[dtime[i]])
        )

print(temp_10)

# a pandas.Series designed for time series of a 2D lat,lon grid
t10 = pd.concat(temp_10, axis=0)
t10.sort_index(inplace=True)
t2 = pd.concat(temp_2, axis=0)
t2.sort_index(inplace=True)
h10 = pd.concat(hum_10, axis=0)
h10.sort_index(inplace=True)
h2 = pd.concat(hum_2, axis=0)
h2.sort_index(inplace=True)

t10.to_csv('t10m.csv', index=True, header=False)
t2.to_csv('t2m.csv',index=True, header=False)
h10.to_csv('h10m.csv',index=True, header=False)
h2.to_csv('h2m.csv',index=True, header=False)



