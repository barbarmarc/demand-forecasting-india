import os

from multiprocessing import Pool
import pandas as pd

import config, model_helper
from model import LinearRegression as LR

NUM_THREADS=8


def load_data():
    def load_regional(time):
        return {
            region_name: model_helper.index_as_date(pd.read_csv(
                f'{config.PATH_TO_INTERMEDIATE_DATA}/{region_name}_{time}.csv',
                header=0,
                index_col=0
            )) for region_name in config.cities
        }

    def load_energy(energy):
        return model_helper.index_as_date(pd.read_csv(
            f'{config.PATH_TO_INTERMEDIATE_DATA}/{energy}.csv',
            header=0,
            index_col=0),
        )
    
    energies = {
        'peak': load_energy('peaks'),
        'consumption': load_energy('consumption')
    }
    past_Xs, future_Xs = load_regional('past'), load_regional('future')

    return energies, past_Xs, future_Xs


def get_train_test_split(df):
    return df[df.index.year != 2019], df[df.index.year == 2019]

def initialize_models(energies, past_Xs, future_Xs, l1_ratio=.9, alpha=1.0):
    models = []
    for region in config.cities:
        past_X, future_X = past_Xs[region], future_Xs[region]
        for energy in energies:
            y = energies[energy][region]
            models.append(
                LR(
                    past_X, y, 
                    future_X, energy, region,
                    l1_ratio=l1_ratio,
                    alpha=alpha,
                ),
            )
    return models

def model_fit(model):
    model.fit()
    
def create_and_fit_models():
    energies, past_Xs, future_Xs = load_data()
    models = initialize_models(energies, past_Xs, future_Xs)

    for model in models:
        model_fit(model)
#     with Pool(NUM_THREADS) as p:
#         p.map(model_fit, models)
    print('Done fitting')
    return models

def run_model_predictions(models):
    peaks = {gdp_type: [] for gdp_type in config.gdp_types}
    consumptions = {gdp_type: [] for gdp_type in config.gdp_types}

    for model in models:
        for gdp_type in config.gdp_types:
            res = model.future_X.copy()
            res[f'{model.region_name}'] = model.predict(gdp_type=gdp_type)
            if model.energy == 'peak':
                peaks[gdp_type].append(res[f'{model.region_name}'])
            elif model.energy == 'consumption':
                consumptions[gdp_type].append(res[f'{model.region_name}'])

    def combine_df(energy_list):
        energy = pd.concat(energy_list, axis=1)
        energy.index.name='Date'
        return energy

    peaks = {gdp_type: combine_df(peak) for gdp_type, peak in peaks.items()}
    consumptions = {gdp_type: combine_df(consumption)
                    for gdp_type, consumption in consumptions.items()}

    return peaks, consumptions

def save_linear_regression(folder='linear_regression'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for gdp_type in config.gdp_types:
        subfolder = f'{folder}/{gdp_type}_predictions'
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)
    
    models = create_and_fit_models()
    peaks, consumptions = run_model_predictions(models)
    for gdp in config.gdp_types:
        peaks[gdp].to_csv(f'{folder}/{gdp}_peaks.csv', index=True, header=True)
        consumptions[gdp].to_csv(f'{folder}/{gdp}_consumptions.csv', index=True, header=True)

    for yr in config.future_yrs:
        yr = 2000 + yr
        for gdp_type in config.gdp_types:
            consumption = consumptions[gdp_type]
            consumption.loc[consumption.index.year == yr].to_csv(
                f'{folder}/{gdp_type}_predictions/{yr}_consumption.csv',
                index=True, header=True
            )
            peak = peaks[gdp_type]
            peak.loc[peak.index.year == yr].to_csv(
                f'{folder}/{gdp_type}_predictions/{yr}_peak.csv',
                index=True, header=True
            )

if __name__ == '__main__':
    save_linear_regression()

