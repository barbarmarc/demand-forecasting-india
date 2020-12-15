import pandas as pd

def index_as_date(df):
    df.index = pd.to_datetime(df.index)
    df.index = pd.DatetimeIndex(df.index.values,
                                freq=df.index.inferred_freq)
    return df

def add_gdp_type(df, gdp_type):
    """
    Hack to pull out relevant gdp type from three options
    """
    colnames = df.columns
    colname = [col for col in colnames
               if 'gdp' in col and gdp_type in col][0]
    gdp = df[colname]
    for col in colnames:
        if 'gdp' in col:
            df.drop([col], axis=1, inplace=True)
    df['gdp'] = gdp
    return df

