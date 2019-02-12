def lag(series, periods=1):
    return series.shift(periods=periods)

def maximum(series, window=5):
    return series.rolling(window=window).max()

def minimum(series, window=5):
    return series.rolling(window=window).min()

def crossover(series_1, series_2):
    past = lag(series_1, periods=1) < lag(series_2, periods=1)
    now = series_1 > series_2
    return past & now

def crossunder(series_1, series_2):
    past = lag(series_1, periods=1) > lag(series_2, periods=1)
    now = series_1 < series_2
    return past & now

def preprocess(stock_1, stock_2):
    '''
    依據日期之交集回傳股價資料
    '''
    stock_1 = stock_1.copy()
    stock_2 = stock_2.copy()
    stock_1.dropna(inplace=True)
    stock_2.dropna(inplace=True)
    date_index = stock_1.merge(stock_2, on='date')['date']
    stock_1 = stock_1[stock_1.date.isin(date_index)]
    stock_1.reset_index(inplace=True, drop=True)
    stock_2 = stock_2[stock_2.date.isin(date_index)]
    stock_2.reset_index(inplace=True, drop=True)
    return stock_1, stock_2