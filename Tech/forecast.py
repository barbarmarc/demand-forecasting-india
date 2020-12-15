#%% packages
import os
import pandas as pd
from metrics import get_scenarios, clean_states
from profiles import read_profiles, add_profile
from ev import add_e2w, add_light, add_cars
from ac import add_ac
from result import results, result_summary, to_genx

scenarios = get_scenarios()
states = clean_states(pd.read_excel("data/state.xlsx"))
ac_capacity = pd.read_csv("data/ac_capacity.csv", index_col='Year')
ac_demand = pd.read_csv("data/ac_demand.csv", index_col='Year')
ac_stock_base = pd.read_csv("data/ac_stock_base.csv", index_col='Year')
ac_stock = pd.read_csv("data/ac_stock.csv", index_col='Year')
ev = pd.read_excel("data/ev.xlsx", index_col=0)
ev_profiles = pd.read_excel("data/ev_profiles.xlsx")
car_sales = pd.read_excel("data/car_sales.xlsx", index_col=0)
car_registration = pd.read_excel("data/car_registration.xlsx")
car_registration = car_registration.T
new_header = car_registration.iloc[0]
car_registration = car_registration[1:]
car_registration.columns = new_header

def run_profiles():
    for growth in ['stable', 'rapid', 'slow']:
        for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
            base_profile, base_consumption, consumption = read_profiles(year, growth)
            _ = add_profile(year, states, base_profile, base_consumption, consumption)        
def run_ac():
    for efficiency in ['baseline', 'iea']:
        for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
            res_ac, com_ac = add_ac(efficiency, year, states, ac_stock, ac_stock_base, ac_demand, ac_capacity)
            res_ac.to_csv('res_'+efficiency+'_'+str(year)+'.csv')
            com_ac.to_csv('com_'+efficiency+'_'+str(year)+'.csv')
    dirlist = os.listdir('input/ac/')
    for file in dirlist:
        df = pd.read_csv('input/ac/'+file, index_col=0)
        df = df*1000
        df.to_csv('input/ac/'+file)
def run_e2w():
    for growth in ['stable', 'slow', 'rapid']:
        for charging in ['home', 'work', 'public']:
            for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
                e2w_profile = add_e2w(states, ev_profiles, ev, car_registration, car_sales, year, growth, charging)
                e2w_profile.to_csv('input/e2w/e2w_'+growth+'_'+charging+'_'+str(year)+'.csv')
    dirlist = os.listdir('input/e2w/')
    for file in dirlist:
        df = pd.read_csv('input/e2w/'+file, index_col=0)
        df = df*1.75 # charging factor
        df['Arunachal Pradesh'] = 0 # no car data
        df.to_csv('input/e2w/'+file)
def run_e3w():
    for growth in ['stable', 'slow', 'rapid']:
        for charging in ['home', 'work', 'public']:
            for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
                light_profile = add_light(states, ev_profiles, ev, car_registration, car_sales, year, growth, charging)
                light_profile.to_csv('input/e3w/e3w_'+growth+'_'+charging+'_'+str(year)+'.csv')
    dirlist = os.listdir('input/e3w/')
    for file in dirlist:
        df = pd.read_csv('input/e3w/'+file, index_col=0)
        df = df*1.75 # charging factor
        df['Arunachal Pradesh'] = 0 # no car data
        df.to_csv('input/e3w/'+file)
def run_e4w():
    for growth in ['stable', 'slow', 'rapid']:
        for charging in ['home', 'work', 'public']:
            for year in [2020, 2025, 2030, 2035, 2040, 2045, 2050]:
                cars_profile = add_cars(states, ev_profiles, ev, car_registration, car_sales, year, growth, charging)
                cars_profile.to_csv('input/e4w/e4w_'+growth+'_'+charging+'_'+str(year)+'.csv')
    dirlist = os.listdir('input/e4w/')
    for file in dirlist:
        df = pd.read_csv('input/e4w/'+file, index_col=0)
        df = df*1.75 # charging factor
        df['Arunachal Pradesh'] = 0 # no car data
        df.to_csv('input/e4w/'+file)

def run_results():
    results()
    result_summary()
    to_genx()