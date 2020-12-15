import pandas as pd
import numpy as np
import random
import datetime
import itertools
import ast
import os
from scipy import stats
import matplotlib.pyplot as plt
from collections import deque
from copy import deepcopy

def state_share(states, year):
    domestic_share_list, commercial_share_list = [], []
    for state in states.index.tolist()[:-1]:

        energy = pd.read_excel("data/category/consumption/"+state+".xlsx", index_col='Year')
        energy_india = pd.read_excel("data/category/consumption/India.xlsx", index_col='Year')
        
        domestic_share = energy.Domestic[2015]/energy_india.Domestic[2015]
        commercial_share = energy.Commercial[2015]/energy_india.Commercial[2015]

        domestic_share_list.append(domestic_share)
        commercial_share_list.append(commercial_share)

    df = pd.DataFrame(zip(domestic_share_list, commercial_share_list), index=states.index.tolist()[:-1], columns=['domestic', 'commercial'])

    df.domestic = df.domestic/df.domestic.sum()
    df.commercial = df.commercial/df.commercial.sum()

    return df

def normalize(ac):
    return [float(i)/sum(ac) for i in ac]

def randomize(day_profile, states, state):

    l1 = day_profile

    for _ in range(int(round((states.Population/1000000)[state]))):
        items = deque(day_profile)
        items.rotate(random.randint(-3,3))
        l2 = list(items)
        l1 = [a+b for a, b in zip(l1, l2)]
        l1_norm = normalize(l1)

    return [i*sum(day_profile) for i in l1_norm]

def norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day):   
    for i in range(6):
        if i == 4:
            R_S_HI = R_S_HI.append(R_S_HI_day*0.8*random.uniform(0.5,1.5), ignore_index=True)
            R_W_HI = R_W_HI.append(R_W_HI_day*0.8*random.uniform(0.5,1.5), ignore_index=True)
            C_S_HI = C_S_HI.append(C_S_HI_day*0.8*random.uniform(0.5,1.5), ignore_index=True)
            C_W_HI = C_W_HI.append(C_W_HI_day*0.8*random.uniform(0.5,1.5), ignore_index=True)
        elif i == 5:
            R_S_HI = R_S_HI.append(R_S_HI_day*0.6*random.uniform(0.5,1.5), ignore_index=True)
            R_W_HI = R_W_HI.append(R_W_HI_day*0.6*random.uniform(0.5,1.5), ignore_index=True)
            C_S_HI = C_S_HI.append(C_S_HI_day*0.4*random.uniform(0.5,1.5), ignore_index=True)
            C_W_HI = C_W_HI.append(C_W_HI_day*0.4*random.uniform(0.5,1.5), ignore_index=True)
        else:
            R_S_HI = R_S_HI.append(R_S_HI_day*random.uniform(0.5,1.5), ignore_index=True)
            R_W_HI = R_W_HI.append(R_W_HI_day*random.uniform(0.5,1.25), ignore_index=True)
            C_S_HI = C_S_HI.append(C_S_HI_day*random.uniform(0.5,1.5), ignore_index=True)
            C_W_HI = C_W_HI.append(C_W_HI_day*random.uniform(0.5,1.5), ignore_index=True)
    
    norm_r_s_ac = normalize(R_S_HI.AC.tolist())
    norm_r_w_ac = normalize(R_W_HI.AC.tolist())
    norm_c_s_ac = normalize(C_S_HI.AC.tolist())
    norm_c_w_ac = normalize(C_W_HI.AC.tolist())

    return norm_r_s_ac, norm_r_w_ac, norm_c_s_ac, norm_c_w_ac

def add_ac(efficiency, year, states, ac_stock, ac_stock_base, ac_demand, ac_capacity):

    R_S_HI = pd.read_excel("data/profiles/R_S.xlsx", index_col='Hour')
    R_W_HI = pd.read_excel("data/profiles/R_W.xlsx", index_col='Hour')
    C_S_HI = pd.read_excel("data/profiles/C_S.xlsx", index_col='Hour')
    C_W_HI = pd.read_excel("data/profiles/C_W.xlsx", index_col='Hour')
    
    R_S_HI_day = pd.read_excel("data/profiles/R_S.xlsx", index_col='Hour')
    R_W_HI_day = pd.read_excel("data/profiles/R_W.xlsx", index_col='Hour')
    C_S_HI_day = pd.read_excel("data/profiles/C_S.xlsx", index_col='Hour')
    C_W_HI_day = pd.read_excel("data/profiles/C_W.xlsx", index_col='Hour')

    if efficiency == 'baseline':
        res_ac_demand = ac_demand['Residential India Baseline scenario (TWh)'][year]
        com_ac_demand = ac_demand['Commercial India Baseline scenario (TWh)'][year]
    elif efficiency == 'iea':
        res_ac_demand = ac_demand['Residential India Efficient Cooling scenario (TWh)'][year]
        com_ac_demand = ac_demand['Commercial India Efficient Cooling scenario (TWh)'][year]  
    
    hours = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
    
    high_hour = []
    for i in states.High_Months[:-1]:
        foo = []
        for j in i:
            if j != 0:
                foo.append(hours[j-1])
            else:
                foo.append(0)
        high_hour.append(sum(foo))
    
    summer_hours = pd.DataFrame(zip(states.index.tolist()[:-1], high_hour), columns=['State', 'Summer Hours'])
    summer_hours = summer_hours.set_index('State')
    
    state_shares = state_share(states, year)
    res_list, com_list = [], []
    res_index_profiles, com_index_profiles = [], []
    for state in states.index.tolist()[:-1]:

        res_ac = res_ac_demand*state_shares.domestic[state]
        com_ac = com_ac_demand*state_shares.commercial[state]

        res_list.append(res_ac)
        com_list.append(com_ac)
        
        high_months = states.High_Months[state]
        res_index_profile = []
        for i in range(1,13):
            if i in high_months:
                if i in [1,3,5,7,8,10,12]:
                    for j in range(1,32):
                        if j<= 7:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_r_s_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        res_index_profile.append([i*rv for i in day_profile])
                elif i in [4,6,9,11]:
                    for j in range(1,31):
                        if j<= 7:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_r_s_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        res_index_profile.append([i*rv for i in day_profile])
                else:
                    for j in range(1,29):
                        if j<= 7:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            norm_r_s_ac, _, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_r_s_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        res_index_profile.append([i*rv for i in day_profile])
            else:
                if i in [1,3,5,7,8,10,12]:
                    for j in range(1,32):
                        if j<= 7:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_r_w_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        res_index_profile.append([i*rv for i in day_profile])
                elif i in [4,6,9,11]:
                    for j in range(1,31):
                        if j<= 7:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_r_w_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        res_index_profile.append([i*rv for i in day_profile])
                else:
                    for j in range(1,29):
                        if j<= 7:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            _, norm_r_w_ac, _, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_r_w_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        res_index_profile.append([i*rv for i in day_profile])
        res_index_profile = list(itertools.chain(*res_index_profile))
        res_index_profiles.append(res_index_profile)
    
        com_index_profile = []
        for i in range(1,13):
            if i in high_months:
                if i in [1,3,5,7,8,10,12]:
                    for j in range(1,32):
                        if j<= 7:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_c_s_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        com_index_profile.append([i*rv for i in day_profile])
                elif i in [4,6,9,11]:
                    for j in range(1,31):
                        if j<= 7:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_c_s_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        com_index_profile.append([i*rv for i in day_profile])
                else:
                    for j in range(1,29):
                        if j<= 7:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                            _, _, norm_c_s_ac, _ = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_c_s_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        com_index_profile.append([i*rv for i in day_profile])
            else:
                if i in [1,3,5,7,8,10,12]:
                    for j in range(1,32):
                        if j<= 7:
                            _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_c_w_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        com_index_profile.append([i*rv for i in day_profile])
                elif i in [4,6,9,11]:
                    for j in range(1,31):
                        if j<= 7:
                            _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_c_w_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        com_index_profile.append([i*rv for i in day_profile])
                else:
                    for j in range(1,29):
                        if j<= 7:
                            _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>7 and j <= 14:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        elif j>14 and j <= 21:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        else:
                             _, _, _, norm_c_w_ac = norm_profiles(R_S_HI, R_W_HI, C_S_HI, C_W_HI, R_S_HI_day, R_W_HI_day, C_S_HI_day, C_W_HI_day)
                        day = datetime.datetime(year, i, j).weekday()
                        rv = random.uniform(0.6, 1.0)
                        day_profile = norm_c_w_ac[day*24:24+(day*24)]
                        day_profile = randomize(day_profile, states, state)
                        com_index_profile.append([i*rv for i in day_profile])
        com_index_profile = list(itertools.chain(*com_index_profile))
        com_index_profiles.append(com_index_profile)
        
    res_index_profiles = pd.DataFrame(res_index_profiles, index=states.index.tolist()[:-1])
    com_index_profiles = pd.DataFrame(com_index_profiles, index=states.index.tolist()[:-1])
    
    result = pd.DataFrame(zip(states.index.tolist()[:-1], res_list, com_list), columns=['State', 'res_ac', 'com_ac'])
    result = result.set_index('State')
    
    res_scaling, com_scaling = [], []
    for index, row in result.iterrows():
        res_scaling.append((row.res_ac*1000000)/res_index_profiles.loc[index].sum())
        com_scaling.append((row.com_ac*1000000)/com_index_profiles.loc[index].sum())
    
    scaling = pd.DataFrame(zip(states.index.tolist(), res_scaling, com_scaling), columns=['State', 'Res_Scaling', 'Com_Scaling'])
    scaling = scaling.set_index('State')
    
    res_index_profiles = res_index_profiles.mul(scaling['Res_Scaling'].tolist(), axis=0)/1000
    com_index_profiles = com_index_profiles.mul(scaling['Com_Scaling'].tolist(), axis=0)/1000
    
    return res_index_profiles.T, com_index_profiles.T
