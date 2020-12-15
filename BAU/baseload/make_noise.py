import csv
import pandas as pd

from predict import load_data, create_and_fit_models
from model_helper import index_as_date

from config import (future_yrs, historical_yrs, gdp_types, cities,
energies, PATH_TO_PREDICTIONS_NO_NOISE)

future_yrs = [2000 + yr for yr in future_yrs]
historical_yrs = [2000 + yr for yr in historical_yrs]

FOLDER = 'linear_regression'


def get_std():
    predictions = {'peak': {}, 'consumption': {}}
    models = create_and_fit_models()
    for model in models:
        pred = {}
        for yr in historical_yrs:
            predicted, actual = model.get_predictions_train_test(test_yr=yr)
            c_predicted = predicted - predicted.mean()
            c_actual = actual - actual.mean()
            diff = c_actual - c_predicted
            pred[yr] = {
                'predicted': predicted,
                'actual': actual,
                'diff': diff,
                'std': diff.std(),
                'mean_avg': (predicted.mean() + actual.mean())/2
            }
            #pred[yr]['scaled_std'] = pred[yr]['std']/pred[yr]['mean_avg']
            pred[yr]['scaled_std'] = pred[yr]['std']
            print(f'year: {yr} for region: {model.region_name} {model.energy} diff mean: {diff.mean()} and diff std: {diff.std()}')
        
        predictions[model.energy][model.region_name] = pred
    return predictions


def save_std():
    std_devs = get_std()
    file_name = f'{FOLDER}/noise.csv'
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        for region in cities:
            peak_std = []
            consumption_std = []
            for yr in historical_yrs:
                peak_std.append(
                    std_devs['peak'][region][yr]['scaled_std']
                )
                consumption_std.append(
                    std_devs['consumption'][region][yr]['scaled_std']
                )
            peak = sum(peak_std)/len(peak_std)
            consumption = sum(consumption_std)/len(consumption_std)
            writer.writerow([region, peak, consumption])



if __name__ == '__main__':
    save_std()

