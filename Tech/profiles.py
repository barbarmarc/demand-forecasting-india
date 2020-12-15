import pandas as pd
import numpy as np
import random
import datetime
import itertools
import ast
import os
from scipy import stats
import matplotlib.pyplot as plt

def read_profiles(year, growth):
    if growth == 'stable':
        base_profile = pd.read_csv("data/base_profile.csv")
        base_profile['DateTime'] = pd.date_range(pd.to_datetime(base_profile.Date.iloc[-1]) - pd.Timedelta(days=364), periods=8760, freq='H')
        del base_profile['Date']
        del base_profile['Time']
        base_profile = base_profile.set_index('DateTime')
        
        base_consumption = pd.read_csv("data/base_consumption.csv")
        base_consumption['DateTime'] = pd.to_datetime(base_consumption['Date'])
        del base_consumption['Date']
        base_consumption = base_consumption.set_index('DateTime')
        
        base_peak = pd.read_csv("data/base_peak.csv")
        base_peak['DateTime'] = pd.to_datetime(base_peak['Date'])
        del base_peak['Date']
        base_peak = base_peak.set_index('DateTime')
        
        consumption = pd.read_csv("input/linear_predictions_with_noise/"+str(year)+"_consumption.csv")
        consumption.columns = ['Date', 'NR', 'WR', 'ER', 'SR', 'NER'] 
        consumption['DateTime'] = pd.to_datetime(consumption['Date'])
        del consumption['Date']
        consumption = consumption.set_index('DateTime')
        consumption = consumption*1000
        
        peak = pd.read_csv("input/linear_predictions_with_noise/"+str(year)+"_peak.csv")
        peak.columns = ['Date', 'NR', 'WR', 'ER', 'SR', 'NER'] 
        peak['DateTime'] = pd.to_datetime(peak['Date'])
        del peak['Date']
        peak = peak.set_index('DateTime')
        
    elif growth == 'rapid':
        base_profile = pd.read_csv("data/base_profile.csv")
        base_profile['DateTime'] = pd.date_range(pd.to_datetime(base_profile.Date.iloc[-1]) - pd.Timedelta(days=364), periods=8760, freq='H')
        del base_profile['Date']
        del base_profile['Time']
        base_profile = base_profile.set_index('DateTime')
        
        base_consumption = pd.read_csv("data/base_consumption.csv")
        base_consumption['DateTime'] = pd.to_datetime(base_consumption['Date'])
        del base_consumption['Date']
        base_consumption = base_consumption.set_index('DateTime')
        
        base_peak = pd.read_csv("data/base_peak.csv")
        base_peak['DateTime'] = pd.to_datetime(base_peak['Date'])
        del base_peak['Date']
        base_peak = base_peak.set_index('DateTime')
        
        consumption = pd.read_csv("input/exp_predictions_with_noise/"+str(year)+"_consumption.csv")
        consumption.columns = ['Date', 'NR', 'WR', 'ER', 'SR', 'NER'] 
        consumption['DateTime'] = pd.to_datetime(consumption['Date'])
        del consumption['Date']
        consumption = consumption.set_index('DateTime')
        consumption = consumption*1000
        
        peak = pd.read_csv("input/exp_predictions_with_noise/"+str(year)+"_peak.csv")
        peak.columns = ['Date', 'NR', 'WR', 'ER', 'SR', 'NER'] 
        peak['DateTime'] = pd.to_datetime(peak['Date'])
        del peak['Date']
        peak = peak.set_index('DateTime')
        
    elif growth == 'slow':
        base_profile = pd.read_csv("data/base_profile.csv")
        base_profile['DateTime'] = pd.date_range(pd.to_datetime(base_profile.Date.iloc[-1]) - pd.Timedelta(days=364), periods=8760, freq='H')
        del base_profile['Date']
        del base_profile['Time']
        base_profile = base_profile.set_index('DateTime')
        
        base_consumption = pd.read_csv("data/base_consumption.csv")
        base_consumption['DateTime'] = pd.to_datetime(base_consumption['Date'])
        del base_consumption['Date']
        base_consumption = base_consumption.set_index('DateTime')
        
        base_peak = pd.read_csv("data/base_peak.csv")
        base_peak['DateTime'] = pd.to_datetime(base_peak['Date'])
        del base_peak['Date']
        base_peak = base_peak.set_index('DateTime')
        
        consumption = pd.read_csv("input/log_predictions_with_noise/"+str(year)+"_consumption.csv")
        consumption.columns = ['Date', 'NR', 'WR', 'ER', 'SR', 'NER'] 
        consumption['DateTime'] = pd.to_datetime(consumption['Date'])
        del consumption['Date']
        consumption = consumption.set_index('DateTime')
        consumption = consumption*1000
        
        peak = pd.read_csv("input/log_predictions_with_noise/"+str(year)+"_peak.csv")
        peak.columns = ['Date', 'NR', 'WR', 'ER', 'SR', 'NER'] 
        peak['DateTime'] = pd.to_datetime(peak['Date'])
        del peak['Date']
        peak = peak.set_index('DateTime')
    
    consumption = consumption[consumption.index != str(year)+'-02-29']
    
    return base_profile, base_consumption, consumption


def add_profile(year, states, base_profile, base_consumption, consumption):
    growth = pd.DataFrame()
    for region in consumption.columns:
        growth[region] = consumption[region].to_numpy()/base_consumption[region].to_numpy()
    growth['India'] = growth.mean(axis=1)
    profile = pd.DataFrame()
    for index, row in states.iterrows():
        lst = []
        for i, r in growth.iterrows():
            a = base_profile[index][i*24:i*24+24]*r[row.Region]
            lst.append(a.to_list())
        profile[index] = [item for sublist in lst for item in sublist]

    daterange = pd.date_range(start='1/1/'+str(year), end='1/1/'+str(year+1), freq='H')
    leap = []
    for each in daterange:
        if each.month==2 and each.day ==29:
            leap.append(each)
    daterange = daterange.drop(leap)
    daterange = daterange[:-1]

    profile.index = daterange

    del profile['India']
    
    return profile
