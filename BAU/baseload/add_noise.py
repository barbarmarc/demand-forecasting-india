import os
import csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from predict import load_data
from model_helper import index_as_date
from config import (future_yrs, historical_yrs, gdp_types, cities,
energies, PATH_TO_PREDICTIONS_NO_NOISE)
from make_noise import FOLDER

future_yrs = [2000 + yr for yr in future_yrs]
historical_yrs = [2000 + yr for yr in historical_yrs]

noise_filename = f"{FOLDER}/noise.csv"

def load_predictions():
    def get_energy_predictions(energy):
        return {gdp: index_as_date(
            pd.read_csv(
                f'{PATH_TO_PREDICTIONS_NO_NOISE}/{gdp}_{energy}s.csv',
                header=0,
                index_col=0
            )
        ) for gdp in gdp_types}

    return {
        energy: get_energy_predictions(energy) for energy in energies
    }


def get_noise():
    noise = {}

    noise_df = pd.read_csv(noise_filename)

    for index, row in noise_df.iterrows():
        noise[row.region] = {
            'peak': float(row.peak_std),
            'consumption': float(row.consumption_std)
        }
    
    return noise


def add_noise(predictions):
    noises = get_noise()
    new = { 
        region: {
            energy: {
                gdp: None for gdp in gdp_types
            } for energy in energies
        } for region in cities
    }
    for energy in energies:
        print(f'energy: {energy}')
        edfs = predictions[energy]
        for gdp in gdp_types:
            gdfs = edfs[gdp]
            for region in cities:
                rdfs = gdfs[region]
                n = noises[region][energy]
                dfs = []
                for yr in future_yrs:
                    df = rdfs[rdfs.index.year == yr]
                    #sigma = n * df.mean()
                    sigma = n
                    noise = np.random.normal(0, sigma, df.shape)
                    dfs.append(df+noise) 
                combined = pd.concat(dfs, axis=0)
                new[region][energy][gdp] = combined
    return new

def save_noise(with_noise):
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)
    for gdp_type in gdp_types:
        subfolder = f'{FOLDER}/{gdp_type}_predictions_with_noise'
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)
    for yr in future_yrs:
        for gdp_type in gdp_types:
            peaks, consumptions = [], []
            regions = list(cities)
            for region in regions:
                peaks.append(
                    with_noise[region]['peak'][gdp_type]
                )
                consumptions.append(
                    with_noise[region]['consumption'][gdp_type]
                )
            peak = pd.concat(peaks, axis=1, names=regions)
            consumption = pd.concat(consumptions, axis=1, names=regions)

            
            consumption.loc[consumption.index.year == yr].to_csv(
                f'{FOLDER}/{gdp_type}_predictions_with_noise/{yr}_consumption.csv',
                index=True, header=True
            )
            peak.loc[peak.index.year == yr].to_csv(
                    f'{FOLDER}/{gdp_type}_predictions_with_noise/{yr}_peak.csv',
                index=True, header=True
            )

if __name__ == '__main__':
    predictions = load_predictions()
    with_noise = add_noise(predictions)
    save_noise(with_noise)
