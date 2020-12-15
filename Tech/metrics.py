import pandas as pd
import numpy as np
import random
import datetime
import itertools
import ast
import os
from scipy import stats
import matplotlib.pyplot as plt

def clean_states(states):
    
    low_months = []
    high_months = []
    for index, row in states.iterrows():
        l_lst = row.Low_Months
        h_lst = row.High_Months
        l_lst = ast.literal_eval(l_lst)
        h_lst = ast.literal_eval(h_lst)
        if 0 in l_lst:
            l_lst = np.nan
        if 0 in h_lst:
            l_lst = np.nan
        low_months.append(l_lst)
        high_months.append(h_lst)
    states.Low_Months = low_months
    states.High_Months = high_months
    states = states.set_index('State')

    return states

def get_scenarios():

    gdp_projections = pd.read_excel("data/gdp_projections.xlsx", index_col=0)
    growth = gdp_projections[['stable_growth', 'rapid_growth', 'slow_growth']]
    growth.columns = ['stable','rapid', 'slow']

    return growth
