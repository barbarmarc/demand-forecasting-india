import pandas as pd
import numpy as np
import random
import datetime
import itertools
import ast
import os
from scipy import stats
import matplotlib.pyplot as plt
from metrics import clean_states

def results():
    states = clean_states(pd.read_excel("data/state.xlsx"))

    if not os.path.exists('results/rapid/work/baseline/region'):
        os.makedirs('results/rapid/work/baseline/region')
    if not os.path.exists('results/rapid/work/baseline/state'):
        os.makedirs('results/rapid/work/baseline/state')
    if not os.path.exists('results/rapid/work/iea/region'):
        os.makedirs('results/rapid/work/iea/region')
    if not os.path.exists('results/rapid/work/iea/state'):
        os.makedirs('results/rapid/work/iea/state')
    if not os.path.exists('results/rapid/home/baseline/region'):
        os.makedirs('results/rapid/home/baseline/region')
    if not os.path.exists('results/rapid/home/baseline/state'):
        os.makedirs('results/rapid/home/baseline/state')
    if not os.path.exists('results/rapid/home/iea/region'):
        os.makedirs('results/rapid/home/iea/region')
    if not os.path.exists('results/rapid/home/iea/state'):
        os.makedirs('results/rapid/home/iea/state')
    if not os.path.exists('results/rapid/public/baseline/region'):
        os.makedirs('results/rapid/public/baseline/region')
    if not os.path.exists('results/rapid/public/baseline/state'):
        os.makedirs('results/rapid/public/baseline/state')
    if not os.path.exists('results/rapid/public/iea/region'):
        os.makedirs('results/rapid/public/iea/region')
    if not os.path.exists('results/rapid/public/iea/state'):
        os.makedirs('results/rapid/public/iea/state')     
    if not os.path.exists('results/stable/work/baseline/region'):
        os.makedirs('results/stable/work/baseline/region')
    if not os.path.exists('results/stable/work/baseline/state'):
        os.makedirs('results/stable/work/baseline/state')
    if not os.path.exists('results/stable/work/iea/region'):
        os.makedirs('results/stable/work/iea/region')
    if not os.path.exists('results/stable/work/iea/state'):
        os.makedirs('results/stable/work/iea/state')
    if not os.path.exists('results/stable/home/baseline/region'):
        os.makedirs('results/stable/home/baseline/region')
    if not os.path.exists('results/stable/home/baseline/state'):
        os.makedirs('results/stable/home/baseline/state')
    if not os.path.exists('results/stable/home/iea/region'):
        os.makedirs('results/stable/home/iea/region')
    if not os.path.exists('results/stable/home/iea/state'):
        os.makedirs('results/stable/home/iea/state')
    if not os.path.exists('results/stable/public/baseline/region'):
        os.makedirs('results/stable/public/baseline/region')
    if not os.path.exists('results/stable/public/baseline/state'):
        os.makedirs('results/stable/public/baseline/state')
    if not os.path.exists('results/stable/public/iea/region'):
        os.makedirs('results/stable/public/iea/region')
    if not os.path.exists('results/stable/public/iea/state'):
        os.makedirs('results/stable/public/iea/state')     
    if not os.path.exists('results/slow/work/baseline/region'):
        os.makedirs('results/slow/work/baseline/region')
    if not os.path.exists('results/slow/work/baseline/state'):
        os.makedirs('results/slow/work/baseline/state')
    if not os.path.exists('results/slow/work/iea/region'):
        os.makedirs('results/slow/work/iea/region')
    if not os.path.exists('results/slow/work/iea/state'):
        os.makedirs('results/slow/work/iea/state')
    if not os.path.exists('results/slow/home/baseline/region'):
        os.makedirs('results/slow/home/baseline/region')
    if not os.path.exists('results/slow/home/baseline/state'):
        os.makedirs('results/slow/home/baseline/state')
    if not os.path.exists('results/slow/home/iea/region'):
        os.makedirs('results/slow/home/iea/region')
    if not os.path.exists('results/slow/home/iea/state'):
        os.makedirs('results/slow/home/iea/state')
    if not os.path.exists('results/slow/public/baseline/region'):
        os.makedirs('results/slow/public/baseline/region')
    if not os.path.exists('results/slow/public/baseline/state'):
        os.makedirs('results/slow/public/baseline/state')
    if not os.path.exists('results/slow/public/iea/region'):
        os.makedirs('results/slow/public/iea/region')
    if not os.path.exists('results/slow/public/iea/state'):
        os.makedirs('results/slow/public/iea/state')
    if not os.path.exists('results/slow/public/iea/national'):
        os.makedirs('results/slow/public/iea/national')
    if not os.path.exists('results/slow/public/baseline/national'):
        os.makedirs('results/slow/public/baseline/national')
    if not os.path.exists('results/slow/home/iea/national'):
        os.makedirs('results/slow/home/iea/national')
    if not os.path.exists('results/slow/home/baseline/national'):
        os.makedirs('results/slow/home/baseline/national')
    if not os.path.exists('results/slow/work/iea/national'):
        os.makedirs('results/slow/work/iea/national')
    if not os.path.exists('results/slow/work/baseline/national'):
        os.makedirs('results/slow/work/baseline/national')
    if not os.path.exists('results/rapid/public/iea/national'):
        os.makedirs('results/rapid/public/iea/national')
    if not os.path.exists('results/rapid/public/baseline/national'):
        os.makedirs('results/rapid/public/baseline/national')
    if not os.path.exists('results/rapid/home/iea/national'):
        os.makedirs('results/rapid/home/iea/national')
    if not os.path.exists('results/rapid/home/baseline/national'):
        os.makedirs('results/rapid/home/baseline/national')
    if not os.path.exists('results/rapid/work/iea/national'):
        os.makedirs('results/rapid/work/iea/national')
    if not os.path.exists('results/rapid/work/baseline/national'):
        os.makedirs('results/rapid/work/baseline/national')
    if not os.path.exists('results/stable/public/iea/national'):
        os.makedirs('results/stable/public/iea/national')
    if not os.path.exists('results/stable/public/baseline/national'):
        os.makedirs('results/stable/public/baseline/national')
    if not os.path.exists('results/stable/home/iea/national'):
        os.makedirs('results/stable/home/iea/national')
    if not os.path.exists('results/stable/home/baseline/national'):
        os.makedirs('results/stable/home/baseline/national')
    if not os.path.exists('results/stable/work/iea/national'):
        os.makedirs('results/stable/work/iea/national')
    if not os.path.exists('results/stable/work/baseline/national'):
        os.makedirs('results/stable/work/baseline/national')

    for growth in ['stable', 'rapid', 'slow']:
        for efficiency in ['baseline', 'iea']:
            for charging in ['home', 'public', 'work']:
                for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
                    bau_profile = pd.read_csv('input/bau/bau_'+growth+'_'+str(year)+'.csv')
                    res_ac = pd.read_csv('input/ac/res_'+efficiency+'_'+str(year)+'.csv')
                    com_ac = pd.read_csv('input/ac/com_'+efficiency+'_'+str(year)+'.csv')
                    e2w = pd.read_csv('input/e2w/e2w_'+growth+'_'+charging+'_'+str(year)+'.csv')
                    e3w = pd.read_csv('input/e3w/e3w_'+growth+'_'+charging+'_'+str(year)+'.csv')
                    e4w = pd.read_csv('input/e4w/e4w_'+growth+'_'+charging+'_'+str(year)+'.csv')

                    print(growth, efficiency, charging, year)
                    
                    for state in states.index.tolist()[:-1]:
                        state_df = pd.DataFrame()
                        state_df['Base'] = bau_profile[state]
                        state_df['Com AC'] = com_ac[state]
                        state_df['Res AC'] = res_ac[state]
                        state_df['E2W'] = e2w[state]
                        state_df['E3W'] = e3w[state]
                        state_df['E4W'] = e4w[state]
                        state_df.index = bau_profile.DateTime

                        state_df.to_csv('results/'+growth+'/'+charging+'/'+efficiency+'/state/'+state+'_'+str(year)+'.csv')

                    for region in states.Region.unique().tolist()[:-1]:
                        regional_states = states[states.Region == region].index.tolist()

                        region_df = pd.DataFrame()
                        region_df['Base'] = bau_profile[regional_states].sum(axis=1)
                        region_df['Com AC'] = com_ac[regional_states].sum(axis=1)
                        region_df['Res AC'] = res_ac[regional_states].sum(axis=1)
                        region_df['E2W'] = e2w[regional_states].sum(axis=1)
                        region_df['E3W'] = e3w[regional_states].sum(axis=1)
                        region_df['E4W'] = e4w[regional_states].sum(axis=1)
                        region_df.index = bau_profile.DateTime

                        region_df.to_csv('results/'+growth+'/'+charging+'/'+efficiency+'/region/'+region+'_'+str(year)+'.csv')

                    all_states = states.index.tolist()[:-1]
                    national_df = pd.DataFrame()
                    national_df['Base'] = bau_profile[all_states].sum(axis=1)
                    national_df['Com AC'] = com_ac[all_states].sum(axis=1)
                    national_df['Res AC'] = res_ac[all_states].sum(axis=1)
                    national_df['E2W'] = e2w[all_states].sum(axis=1)
                    national_df['E3W'] = e3w[all_states].sum(axis=1)
                    national_df['E4W'] = e4w[all_states].sum(axis=1)
                    national_df.index = bau_profile.DateTime

                    national_df.to_csv('results/'+growth+'/'+charging+'/'+efficiency+'/national/India_'+str(year)+'.csv')

def result_summary():

    states = clean_states(pd.read_excel("data/state.xlsx"))

    if not os.path.exists('results/rapid/work/baseline/summary'):
        os.makedirs('results/rapid/work/baseline/summary')
    if not os.path.exists('results/rapid/work/iea/summary'):
        os.makedirs('results/rapid/work/iea/summary')
    if not os.path.exists('results/rapid/home/baseline/summary'):
        os.makedirs('results/rapid/home/baseline/summary')
    if not os.path.exists('results/rapid/home/iea/summary'):
        os.makedirs('results/rapid/home/iea/summary')
    if not os.path.exists('results/rapid/public/baseline/summary'):
        os.makedirs('results/rapid/public/baseline/summary')
    if not os.path.exists('results/rapid/public/iea/summary'):
        os.makedirs('results/rapid/public/iea/summary')    
    if not os.path.exists('results/stable/work/baseline/summary'):
        os.makedirs('results/stable/work/baseline/summary')
    if not os.path.exists('results/stable/work/iea/summary'):
        os.makedirs('results/stable/work/iea/summary')
    if not os.path.exists('results/stable/home/baseline/summary'):
        os.makedirs('results/stable/home/baseline/summary')
    if not os.path.exists('results/stable/home/iea/summary'):
        os.makedirs('results/stable/home/iea/summary')
    if not os.path.exists('results/stable/public/baseline/summary'):
        os.makedirs('results/stable/public/baseline/summary')
    if not os.path.exists('results/stable/public/iea/summary'):
        os.makedirs('results/stable/public/iea/summary')    
    if not os.path.exists('results/slow/work/baseline/summary'):
        os.makedirs('results/slow/work/baseline/summary')
    if not os.path.exists('results/slow/work/iea/summary'):
        os.makedirs('results/slow/work/iea/summary')
    if not os.path.exists('results/slow/home/baseline/summary'):
        os.makedirs('results/slow/home/baseline/summary')
    if not os.path.exists('results/slow/home/iea/summary'):
        os.makedirs('results/slow/home/iea/summary')
    if not os.path.exists('results/slow/public/baseline/summary'):
        os.makedirs('results/slow/public/baseline/summary')
    if not os.path.exists('results/slow/public/iea/summary'):
        os.makedirs('results/slow/public/iea/summary')
    
    for growth in ['stable', 'slow', 'rapid']:
        for charging in ['home', 'work', 'public']:
            for efficiency in ['baseline', 'iea']:   
                base, com_ac, res_ac, e2w, e3w, e4w = [], [], [], [], [], []
                for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:


                    df = pd.read_csv('results/'+growth+'/'+charging+'/'+efficiency+'/national/India_'+str(year)+'.csv')
                    base.append(df.Base.sum())
                    com_ac.append(df['Com AC'].sum())
                    res_ac.append(df['Res AC'].sum())
                    e2w.append(df['E2W'].sum())
                    e3w.append(df['E3W'].sum())
                    e4w.append(df['E4W'].sum())
                df = pd.DataFrame(zip(base, com_ac, res_ac, e2w, e3w, e4w), index=[2020, 2025, 2030, 2035, 2040, 2045, 2050], columns=['Base', 'Com AC', 'Res AC', 'E2W', 'E3W', 'E4W'])
                df.to_csv('results/'+growth+'/'+charging+'/'+efficiency+'/summary/India.csv')
                
                for region in ['NR', 'ER', 'SR', 'WR', 'NER']:
                    base, com_ac, res_ac, e2w, e3w, e4w = [], [], [], [], [], []
                    for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
                        df = pd.read_csv('results/'+growth+'/'+charging+'/'+efficiency+'/region/'+region+'_'+str(year)+'.csv')
                        base.append(df.Base.sum())
                        com_ac.append(df['Com AC'].sum())
                        res_ac.append(df['Res AC'].sum())
                        e2w.append(df['E2W'].sum())
                        e3w.append(df['E3W'].sum())
                        e4w.append(df['E4W'].sum())
                    df = pd.DataFrame(zip(base, com_ac, res_ac, e2w, e3w, e4w), index=[2020, 2025, 2030, 2035, 2040, 2045, 2050], columns=['Base', 'Com AC', 'Res AC', 'E2W', 'E3W', 'E4W'])
                    df.to_csv('results/'+growth+'/'+charging+'/'+efficiency+'/summary/'+region+'.csv')
                
                for state in states.index.tolist()[:-1]:
                    base, com_ac, res_ac, e2w, e3w, e4w = [], [], [], [], [], []
                    for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
                        df = pd.read_csv('results/'+growth+'/'+charging+'/'+efficiency+'/state/'+state+'_'+str(year)+'.csv')
                        base.append(df.Base.sum())
                        com_ac.append(df['Com AC'].sum())
                        res_ac.append(df['Res AC'].sum())
                        e2w.append(df['E2W'].sum())
                        e3w.append(df['E3W'].sum())
                        e4w.append(df['E4W'].sum())
                    df = pd.DataFrame(zip(base, com_ac, res_ac, e2w, e3w, e4w), index=[2020, 2025, 2030, 2035, 2040, 2045, 2050], columns=['Base', 'Com AC', 'Res AC', 'E2W', 'E3W', 'E4W'])
                    df.to_csv('results/'+growth+'/'+charging+'/'+efficiency+'/summary/'+state+'.csv')