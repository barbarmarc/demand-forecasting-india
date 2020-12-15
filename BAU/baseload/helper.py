import pandas as pd

# HELPERS
def is_leap_year(year):
    return ((year % 400 == 0) or ((year % 4 == 0 ) and (year % 100 != 0)))

def get_date_range(yr):
    periods = 366 if is_leap_year(yr) else 365
    drng = pd.date_range(f'20{yr}-01-01', periods=periods, freq='D')
    return drng

def handle_leap(df, yr):
    if not(is_leap_year(yr)):
        df = df.drop(index=(2, 29))
    return df

def get_subset(data, yrs):
    def get_date_range_df(yr):
        return pd.DataFrame(get_date_range(yr), columns=['Date'])
    res = []
    for yr in yrs:
        df = get_date_range_df(yr)
        for col in data.columns:
            df[col] = float(str(
                data[col][pd.to_datetime(f'20{yr}').year]
            ).replace(',',''))
        res.append(df)
    df = pd.concat(res, axis=0)
    df.index = pd.to_datetime(df.Date)
    df.index = pd.DatetimeIndex(df.index.values,
                                 freq=df.index.inferred_freq)
    df.drop(columns=["Date"], inplace=True)
    return df
