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
from metrics import get_scenarios
import math

def randomize(day_profile, sales):
    
    l1 = [i*100 for i in day_profile]

    for _ in range(int(sales/100)-1):
        items = deque(day_profile)
        items.rotate(random.randint(-2,2))
        l2 = [i*100 for i in list(items)]
        l1 = [a+b for a, b in zip(l1, l2)]

    return l1

def charging_scheme(charging, ev_profiles, ev_sales):
    wd_charging = pd.DataFrame(columns=range(0,24))
    we_charging = pd.DataFrame(columns=range(0,24))
    wd_simultaneity_factor = 0.8
    we_simultaneity_factor = 0.4
    
    if charging == 'home':
        home_scenario = ev_profiles.home*0.6+ev_profiles.work*0.2+ev_profiles.public*0.2
        scenario = home_scenario/home_scenario.sum()
        p = scenario.tolist()
    elif charging == 'work':
        work_scenario = ev_profiles.work*0.6+ev_profiles.home*0.2+ev_profiles.public*0.2
        scenario = work_scenario/work_scenario.sum()
        p = scenario.tolist()
    elif charging == 'public':
        public_scenario = ev_profiles.public*0.6+ev_profiles.home*0.2+ev_profiles.work*0.2
        scenario = public_scenario/public_scenario.sum()
        p = scenario.tolist()

    for _, row in ev_sales.iterrows():

        series = pd.Series(randomize(p, row.Sales*wd_simultaneity_factor), index = wd_charging.columns)
        wd_charging = wd_charging.append(series, ignore_index=True)

        
        series = pd.Series(randomize(p, row.Sales*we_simultaneity_factor), index = we_charging.columns)
        we_charging = we_charging.append(series, ignore_index=True)
    
    wd_charging.index = ev_sales.index
    we_charging.index = ev_sales.index

    return wd_charging, we_charging

def add_e2w(states, ev_profiles, ev, car_registration, car_sales, year, growth, charging, plotting=False):
    scenarios = get_scenarios()
    scenario = scenarios[growth]

    city_projection, two_wheeler_projection = [], []
    for city in car_registration.columns.tolist():
        city_projection.append(city)
        car_projections = []
        for index, item in scenario.iteritems():
            if index == 2020:
                car_projections.append(car_registration[city]['Two-Wheelers_2015'] * (1+item))
            else:
                car_projections.append(car_projections[-1]*(1+item))

        car_projections = pd.DataFrame(car_projections, index=scenario.index, columns=[growth])

        two_wheeler_projection.append(car_projections[growth][year])
            
    two_wheeler_registration_projection = car_registration.loc[['Two-Wheelers_2014', 'Two-Wheelers_2015', 'Two-Wheelers_2016']].T.drop('Total')
    two_wheeler_registration_projection['Two-Wheelers_'+str(year)] = two_wheeler_projection[:-1]
    
    tw_city, two_wheelers_share = [], []
    total = two_wheeler_registration_projection['Two-Wheelers_'+str(year)].sum() - two_wheeler_registration_projection['Two-Wheelers_2015'].sum()
    for city in two_wheeler_registration_projection.index.tolist():
        two_wheelers_share.append((two_wheeler_registration_projection['Two-Wheelers_'+str(year)][city] - two_wheeler_registration_projection['Two-Wheelers_2015'][city])/total)
        tw_city.append(city)
    
    two_wheelers_share = pd.DataFrame(two_wheelers_share, index=tw_city, columns=['Share'])
    
    car_sales_2015 = car_sales[2015]['Two Wheelers']
    car_sales_projections = []
    for index, item in scenario.iteritems():
        if index == 2020:
            car_sales_projections.append(car_sales_2015 * (1+item))
        else:
            car_sales_projections.append(car_sales_projections[-1]*(1+item))
    car_sales_projections = pd.DataFrame(car_sales_projections, index=scenario.index, columns=[growth])

    car_sales_statewise = two_wheelers_share.Share*car_sales_projections[growth][year]
    car_sales_statewise = car_sales_statewise.to_frame()
    car_sales_statewise.columns = ['Sales']
    
    # EV Penetration
    if growth == 'stable':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.4
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.6
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.8
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
    elif growth == 'slow':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.25
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.5
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.75
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        elif year == 2040:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
    elif growth == 'rapid':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.5
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.75
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
            
    poverty = states.Poverty / states.Poverty['India']
    poverty_norm = (poverty - poverty.mean()) / (poverty.max() - poverty.min())
    ppp = states.PPP_PC / states.PPP_PC['India']
    ppp_norm = (ppp - ppp.mean()) / (ppp.max() - ppp.min())
    
    ev_demographics = pd.DataFrame([poverty_norm, ppp_norm]).T
    sr_e2w, lr_e2w = [], []
    
    # INPUT
    dominant = 60
    dominated = 40
    
    for index, row in ev_demographics.iterrows():
        if row.Poverty <= 0 and row.PPP_PC >= 0:
            lr_e2w.append(dominant)
            sr_e2w.append(dominated)
        elif row.Poverty >= 0 and row.PPP_PC <= 0:
            lr_e2w.append(dominated)
            sr_e2w.append(dominant)    
        elif row.Poverty >= 0 and row.PPP_PC >= 0 or row.Poverty <= 0 and row.PPP_PC <= 0:
            if row.PPP_PC >= row.Poverty:
                lr_e2w.append(dominated)
                sr_e2w.append(dominant) 
            else:
                lr_e2w.append(dominant)
                sr_e2w.append(dominated) 
    
    ev_e2w = pd.DataFrame(zip(sr_e2w, lr_e2w), index=ev_demographics.index, columns=['Short_Range', 'Long_Range'])
    
    hourly_profile = []
    for _ in range(0,52): 
        wd_charging, we_charging = charging_scheme(charging, ev_profiles, ev_sales)
        week_profile = []
        for _ in range(0, 5):
            wd_profile = pd.DataFrame()
            for index, row in wd_charging.iterrows():
                sr = ev_e2w.loc[index]['Short_Range']
                lr = ev_e2w.loc[index]['Long_Range']
                entry = (row*(sr/100)*ev.Power_kW['Short Range E2W'] + row*(lr/100)*ev.Power_kW['Long Range E2W'])*random.uniform(0.8, 1.2)
                wd_profile = wd_profile.append(entry)
            week_profile.append(wd_profile)
        
        for _ in range(0, 2):
            we_profile = pd.DataFrame()
            for index, row in we_charging.iterrows():
                sr = ev_e2w.loc[index]['Short_Range']
                lr = ev_e2w.loc[index]['Long_Range']
        
                entry = (row*(sr/100)*ev.Power_kW['Short Range E2W'] + row*(lr/100)*ev.Power_kW['Long Range E2W'])*random.uniform(0.6, 1.4)
                we_profile = we_profile.append(entry)
            week_profile.append(we_profile)
        
        week = pd.concat(week_profile, axis=1)
        
        hourly_profile.append(week)
    
    ev_profile = pd.concat(hourly_profile, axis=1)
        
    wd_profile = pd.DataFrame()
    for index, row in wd_charging.iterrows():
        sr = ev_e2w.loc[index]['Short_Range']
        lr = ev_e2w.loc[index]['Long_Range']
        entry = (row*(sr/100)*ev.Power_kW['Short Range E2W'] + row*(lr/100)*ev.Power_kW['Long Range E2W'])*random.uniform(0.8, 1.2)
        wd_profile = wd_profile.append(entry)
    
    ev_profile = pd.concat([ev_profile, wd_profile], axis=1)
    
    ev_profile = ev_profile.T
    ev_profile = ev_profile/1000
    
    return ev_profile


def add_light(states, ev_profiles, ev, car_registration, car_sales, year, growth, charging, plotting=False):
    scenarios = get_scenarios()
    scenario = scenarios[growth]

    city_projection, two_wheeler_projection = [], []
    for city in car_registration.columns.tolist():
        city_projection.append(city)
        car_projections = []
        for index, item in scenario.iteritems():
            if index == 2020:
                car_projections.append(car_registration[city]['Light_Vehicles_2015'] * (1+item))
            else:
                car_projections.append(car_projections[-1]*(1+item))

        car_projections = pd.DataFrame(car_projections, index=scenario.index, columns=[growth])

        two_wheeler_projection.append(car_projections[growth][year])
            
    two_wheeler_registration_projection = car_registration.loc[['Light_Vehicles_2014', 'Light_Vehicles_2015', 'Light_Vehicles_2016']].T.drop('Total')
    two_wheeler_registration_projection['Light_Vehicles_'+str(year)] = two_wheeler_projection[:-1]


    tw_city, two_wheelers_share = [], []
    total = two_wheeler_registration_projection['Light_Vehicles_'+str(year)].sum() - two_wheeler_registration_projection['Light_Vehicles_2015'].sum()
    for city in two_wheeler_registration_projection.index.tolist():
        two_wheelers_share.append((two_wheeler_registration_projection['Light_Vehicles_'+str(year)][city] - two_wheeler_registration_projection['Light_Vehicles_2015'][city])/total)
        tw_city.append(city)
    
    two_wheelers_share = pd.DataFrame(two_wheelers_share, index=tw_city, columns=['Share'])
    
    car_sales_2015 = car_sales[2015]['Three Wheelers']
    car_sales_projections = []
    for index, item in scenario.iteritems():
        if index == 2020:
            car_sales_projections.append(car_sales_2015 * (1+item))
        else:
            car_sales_projections.append(car_sales_projections[-1]*(1+item))
    car_sales_projections = pd.DataFrame(car_sales_projections, index=scenario.index, columns=[growth])

    car_sales_statewise = two_wheelers_share.Share*car_sales_projections[growth][year]
    car_sales_statewise = car_sales_statewise.to_frame()
    car_sales_statewise.columns = ['Sales']
    
    # EV Penetration
    if growth == 'stable':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.4
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.6
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.8
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
    elif growth == 'slow':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.25
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.5
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.75
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        elif year == 2040:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
    elif growth == 'rapid':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.5
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.75
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
            
    poverty = states.Poverty / states.Poverty['India']
    poverty_norm = (poverty - poverty.mean()) / (poverty.max() - poverty.min())
    ppp = states.PPP_PC / states.PPP_PC['India']
    ppp_norm = (ppp - ppp.mean()) / (ppp.max() - ppp.min())
    
    ev_demographics = pd.DataFrame([poverty_norm, ppp_norm]).T
    sr_e2w, lr_e2w = [], []
    
    # INPUT
    dominant = 60
    dominated = 40
    
    for index, row in ev_demographics.iterrows():
        if row.Poverty <= 0 and row.PPP_PC >= 0:
            lr_e2w.append(dominant)
            sr_e2w.append(dominated)
        elif row.Poverty >= 0 and row.PPP_PC <= 0:
            lr_e2w.append(dominated)
            sr_e2w.append(dominant)    
        elif row.Poverty >= 0 and row.PPP_PC >= 0 or row.Poverty <= 0 and row.PPP_PC <= 0:
            if row.PPP_PC >= row.Poverty:
                lr_e2w.append(dominated)
                sr_e2w.append(dominant) 
            else:
                lr_e2w.append(dominant)
                sr_e2w.append(dominated) 
    
    ev_e2w = pd.DataFrame(zip(sr_e2w, lr_e2w), index=ev_demographics.index, columns=['Short_Range', 'Long_Range'])

    hourly_profile = []
    for _ in range(0,52): 
        wd_charging, we_charging = charging_scheme(charging, ev_profiles, ev_sales)
        week_profile = []
        for _ in range(0, 5):
            wd_profile = pd.DataFrame()
            for index, row in wd_charging.iterrows():
                sr = ev_e2w.loc[index]['Short_Range']
                lr = ev_e2w.loc[index]['Long_Range']
                entry = (row*(sr/100)*ev.Power_kW['Short Range E3W'] + row*(lr/100)*ev.Power_kW['Long Range E3W'])*random.uniform(0.8, 1.2)
                wd_profile = wd_profile.append(entry)
            week_profile.append(wd_profile)
        
        for _ in range(0, 2):
            we_profile = pd.DataFrame()
            for index, row in we_charging.iterrows():
                sr = ev_e2w.loc[index]['Short_Range']
                lr = ev_e2w.loc[index]['Long_Range']
        
                entry = (row*(sr/100)*ev.Power_kW['Short Range E3W'] + row*(lr/100)*ev.Power_kW['Long Range E3W'])*random.uniform(0.6, 1.4)
                we_profile = we_profile.append(entry)
            week_profile.append(we_profile)
        
        week = pd.concat(week_profile, axis=1)
        
        hourly_profile.append(week)
    
    ev_profile = pd.concat(hourly_profile, axis=1)
        
    wd_profile = pd.DataFrame()
    for index, row in wd_charging.iterrows():
        sr = ev_e2w.loc[index]['Short_Range']
        lr = ev_e2w.loc[index]['Long_Range']
        entry = (row*(sr/100)*ev.Power_kW['Short Range E3W'] + row*(lr/100)*ev.Power_kW['Long Range E3W'])*random.uniform(0.8, 1.2)
        wd_profile = wd_profile.append(entry)
    
    ev_profile = pd.concat([ev_profile, wd_profile], axis=1)
    
    ev_profile = ev_profile.T
    ev_profile = ev_profile/1000
    
    return ev_profile

def add_cars(states, ev_profiles, ev, car_registration, car_sales, year, growth, charging, plotting=False):
    scenarios = get_scenarios()
    scenario = scenarios[growth]

    city_projection, two_wheeler_projection = [], []
    for city in car_registration.columns.tolist():
        city_projection.append(city)
        car_projections = []
        for index, item in scenario.iteritems():
            if index == 2020:
                car_projections.append(car_registration[city]['Cars_2015'] * (1+item))
            else:
                car_projections.append(car_projections[-1]*(1+item))

        car_projections = pd.DataFrame(car_projections, index=scenario.index, columns=[growth])

        two_wheeler_projection.append(car_projections[growth][year])
            
    two_wheeler_registration_projection = car_registration.loc[['Cars_2014', 'Cars_2015', 'Cars_2016']].T.drop('Total')
    two_wheeler_registration_projection['Cars_'+str(year)] = two_wheeler_projection[:-1]
    
    tw_city, two_wheelers_share = [], []
    total = two_wheeler_registration_projection['Cars_'+str(year)].sum() - two_wheeler_registration_projection['Cars_2015'].sum()
    for city in two_wheeler_registration_projection.index.tolist():
        two_wheelers_share.append((two_wheeler_registration_projection['Cars_'+str(year)][city] - two_wheeler_registration_projection['Cars_2015'][city])/total)
        tw_city.append(city)
    
    two_wheelers_share = pd.DataFrame(two_wheelers_share, index=tw_city, columns=['Share'])
    
    car_sales_2015 = car_sales[2015]['Passenger Vehicles']
    car_sales_projections = []
    for index, item in scenario.iteritems():
        if index == 2020:
            car_sales_projections.append(car_sales_2015 * (1+item))
        else:
            car_sales_projections.append(car_sales_projections[-1]*(1+item))
    car_sales_projections = pd.DataFrame(car_sales_projections, index=scenario.index, columns=[growth])

    car_sales_statewise = two_wheelers_share.Share*car_sales_projections[growth][year]
    car_sales_statewise = car_sales_statewise.to_frame()
    car_sales_statewise.columns = ['Sales']
    
    # EV Penetration
    if growth == 'stable':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.4
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.6
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.8
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
    elif growth == 'slow':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.25
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.5
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.75
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        elif year == 2040:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
    elif growth == 'rapid':
        if year == 2020:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.5
        elif year == 2025:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]*0.75
        elif year == 2030:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        elif year == 2035:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]
        else:
            ev_sales = car_sales_statewise[car_sales_statewise['Sales'] > 0]

    poverty = states.Poverty / states.Poverty['India']
    poverty_norm = (poverty - poverty.mean()) / (poverty.max() - poverty.min())
    ppp = states.PPP_PC / states.PPP_PC['India']
    ppp_norm = (ppp - ppp.mean()) / (ppp.max() - ppp.min())
    
    ev_demographics = pd.DataFrame([poverty_norm, ppp_norm]).T
    sr_e2w, lr_e2w = [], []
    
    # INPUT
    dominant = 60
    dominated = 40
    
    for index, row in ev_demographics.iterrows():
        if row.Poverty <= 0 and row.PPP_PC >= 0:
            lr_e2w.append(dominant)
            sr_e2w.append(dominated)
        elif row.Poverty >= 0 and row.PPP_PC <= 0:
            lr_e2w.append(dominated)
            sr_e2w.append(dominant)    
        elif row.Poverty >= 0 and row.PPP_PC >= 0 or row.Poverty <= 0 and row.PPP_PC <= 0:
            if row.PPP_PC >= row.Poverty:
                lr_e2w.append(dominated)
                sr_e2w.append(dominant) 
            else:
                lr_e2w.append(dominant)
                sr_e2w.append(dominated) 
    
    ev_e2w = pd.DataFrame(zip(sr_e2w, lr_e2w), index=ev_demographics.index, columns=['Short_Range', 'Long_Range'])

    hourly_profile = []
    for _ in range(0,52): 
        wd_charging, we_charging = charging_scheme(charging, ev_profiles, ev_sales)
        week_profile = []
        for _ in range(0, 5):
            wd_profile = pd.DataFrame()
            for index, row in wd_charging.iterrows():
                sr = ev_e2w.loc[index]['Short_Range']
                lr = ev_e2w.loc[index]['Long_Range']
                entry = (row*(sr/100)*ev.Power_kW['Short Range E4W'] + row*(lr/100)*ev.Power_kW['Long Range E4W'])*random.uniform(0.8, 1.2)
                wd_profile = wd_profile.append(entry)
            week_profile.append(wd_profile)
        
        for _ in range(0, 2):
            we_profile = pd.DataFrame()
            for index, row in we_charging.iterrows():
                sr = ev_e2w.loc[index]['Short_Range']
                lr = ev_e2w.loc[index]['Long_Range']
        
                entry = (row*(sr/100)*ev.Power_kW['Short Range E4W'] + row*(lr/100)*ev.Power_kW['Long Range E4W'])*random.uniform(0.6, 1.4)
                we_profile = we_profile.append(entry)
            week_profile.append(we_profile)
        
        week = pd.concat(week_profile, axis=1)
        
        hourly_profile.append(week)
    
    ev_profile = pd.concat(hourly_profile, axis=1)
        
    wd_profile = pd.DataFrame()
    for index, row in wd_charging.iterrows():
        sr = ev_e2w.loc[index]['Short_Range']
        lr = ev_e2w.loc[index]['Long_Range']
        entry = (row*(sr/100)*ev.Power_kW['Short Range E3W'] + row*(lr/100)*ev.Power_kW['Long Range E3W'])*random.uniform(0.8, 1.2)
        wd_profile = wd_profile.append(entry)
    
    ev_profile = pd.concat([ev_profile, wd_profile], axis=1)
    
    ev_profile = ev_profile.T
    ev_profile = ev_profile/1000
    
    return ev_profile
