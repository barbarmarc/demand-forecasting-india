import os

from config import *
from helper import *

PATH_TO_DATA = "../data"
PATH_TO_SAVE = PATH_TO_INTERMEDIATE_DATA

if not os.path.exists(PATH_TO_SAVE):
    os.makedirs(PATH_TO_SAVE)

# Nasa fields to save into independent variables
nasa_names = list(fields.values())


# READ IN GROUND TRUTH CONSUMPTION AND PEAK DATA

def read_data(filename):
    """
    Read ground truth peak and consumption data for 2014-2019
    """
    allyears = [pd.read_csv(f'{PATH_TO_DATA}/energy/{year}_{filename}.csv', header=0,
                            index_col='Date')
                for year in range(2014,2020)]

    df = pd.concat(allyears, axis=0)
    df.index = pd.to_datetime(df.index)
    df.index = pd.DatetimeIndex(df.index.values,
                                freq=df.index.inferred_freq)
    return df

peaks, consumption = read_data('Peak_MW'), read_data('Consumption_GWh')


peaks.to_csv(f'{PATH_TO_SAVE}/peaks.csv', index=True, header=True)
consumption.to_csv(f'{PATH_TO_SAVE}/consumption.csv', index=True, header=True)


def add_features(df):
    # for i in range(1, 13):
    #     df[f'month_{i}'] = df.index.month == i
    #     df[f'month_{i}'] = df[f'month_{i}'].astype(int)
    #df[f'year'] = df.index.year - 2013
    return df

# READ IN HISTORICAL DATA

def get_past_X_for_region(region_name, regional_cities):
    # load and process all fields from nasa dataset
    def process_nasa_field(field_name):
        results = []
        result_names = []
        for i, city in enumerate(regional_cities):
            path = f"{PATH_TO_DATA}/nasa/regions/{region_name}/{city}_{field_name}.csv"
            field = pd.read_csv(path, header=None, index_col=0, 
                                names=['Date', field_name])
            field.index = pd.to_datetime(field.index)
            field.index = pd.DatetimeIndex(field.index.values,
                                           freq=field.index.inferred_freq)
            # specific processing logic for specific data fields
            if field_name == "t2m" or field_name == "t10m":
                field = field[field_name]-273.15

            field_min = field.resample('D').min()
            field_max = field.resample('D').max()
            field_avg = field.resample('D').mean()
            results.extend([field_min, field_max, field_avg])
            result_names.extend([
                f'{city}_{field_name}_min',
                f'{city}_{field_name}_max',
                f'{city}_{field_name}_avg',
            ])
        res = pd.concat(
            results,
            keys=result_names,
            axis=1,
        )
        res.columns = res.columns.get_level_values(0)
        return res

    dfs = [process_nasa_field(field_name) for field_name in nasa_names]
    df = dfs[0].join(dfs[1:])

    # load historical GDP for the region
    def load_gdp(region_name):
        gdp = pd.read_csv(f'{PATH_TO_DATA}/gdp/linear_gdp.csv', header=0,
                          index_col='Date', usecols=["Date", region_name])
        gdp.columns = ['gdp']
        return gdp
    gdp = get_subset(load_gdp(region_name), historical_yrs)
    df = df.join(gdp)
    
    # load historical population for the region
    def load_population(region_name):
        pop = pd.read_csv(f'{PATH_TO_DATA}/population.csv', header=0,
                          index_col='Date', usecols=["Date", region_name])
        pop.columns = [f"population"]
        return pop
    
    #pop = get_subset(load_population(region_name), historical_yrs)
    #df = df.join(pop)

    df = add_features(df)
    return df


def get_past_Xs():
    return {
        region_name: get_past_X_for_region(region_name, city_dict.keys())
        for region_name, city_dict in cities.items()
    }

past_Xs = get_past_Xs()

for region_name, past_X in past_Xs.items():
    past_X.to_csv(f'{PATH_TO_SAVE}/{region_name}_past.csv', index=True, header=True)


# READ IN FUTURE DATA

def get_future_X_for_region(region_name, regional_cities):
    # load and process all fields from nasa dataset
    def process_nasa_field(field_name):
        field_names = []
        for city in regional_cities:
            field_names.extend([
                f'{city}_{field_name}_min',
                f'{city}_{field_name}_max',
                f'{city}_{field_name}_avg',
            ])
        raw = past_Xs[region_name][field_names]
        past_average = raw.groupby([raw.index.month, raw.index.day]).mean()

        res = []
        #for yr in future_yrs:
        for yr in future_yrs:
            drng = get_date_range(yr)
            future_copy = handle_leap(past_average.copy(), yr)
            future_copy['Date'] = drng
            future_copy.reset_index()
            future_copy.index = pd.to_datetime(future_copy.Date)
            future_copy.index = pd.DatetimeIndex(future_copy.index.values,
                                                 freq=future_copy.index.inferred_freq)
            future_copy.drop(['Date'], axis=1, inplace=True)
            res.append(future_copy)
        return pd.concat(res, axis=0)

    dfs = [process_nasa_field(field_name) for field_name in nasa_names]
    df = dfs[0].join(dfs[1:])

    def load_gdp(region_name):
        gdps = []
        for gdp_type in gdp_types:
            gdp = pd.read_csv(f'{PATH_TO_DATA}/gdp/{gdp_type}_gdp.csv', header=0,
                              index_col='Date', usecols=["Date", region_name])
            gdp.columns = [f'gdp_{gdp_type}']
            gdps.append(gdp)
        all_gdps = gdps[0].join(gdps[1:])
        return all_gdps

    gdp = get_subset(load_gdp(region_name), future_yrs)
    df = df.join(gdp)
    
    # load historical population for the region
    def load_population(region_name):
        pop = pd.read_csv(f'{PATH_TO_DATA}/population.csv', header=0,
                          index_col='Date', usecols=["Date", region_name])
        pop.columns = [f"population"]
        return pop
    
    #pop = get_subset(load_population(region_name), future_yrs)
    #df = df.join(pop)

    df = add_features(df)
    return df

def get_future_Xs():
    return {
        region_name: get_future_X_for_region(region_name, city_dict.keys())
        for region_name, city_dict in cities.items()
    }

future_Xs = get_future_Xs()

for region_name, future_X in future_Xs.items():
    future_X.to_csv(f'{PATH_TO_SAVE}/{region_name}_future.csv', index=True, header=True)

