import pandas as pd
import numpy as np
import tushare as ts
import datetime as dt
import os
pro = ts.pro_api('640ab6afd74c33c9464b832ef12188365ead3168185f651bfeefa34f')
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print('new folder: '+path)
    else:
        print(path + 'already exists')
def get_daily(year,path):
    year = str(year)
    path = path+'\\'+year
    mkdir(path)
    df = pro.trade_cal(exchange='', start_date=year+'0101', end_date=year+'1231')
    tradelist = df[df.is_open == 1].cal_date.tolist()
    for i in tradelist:
        df = pro.daily(trade_date = i)
        df.to_csv(path + '\\' + i + '.csv')
    return 'done'
def get_daily_basic(year,path):
    year = str(year)
    path = path+'\\'+year
    mkdir(path)
    df = pro.trade_cal(exchange='', start_date=year+'0101', end_date=year+'1231')
    tradelist = df[df.is_open == 1].cal_date.tolist()
    for i in tradelist:
        df = pro.daily_basic(trade_date = i)
        df.to_csv(path + '\\' + i + '.csv')
    return 'done'

def get_is(code):
    try:
        df = pro.income(ts_code=code, start_date='20110101', end_date = dt.datetime.today().strftime('%Y%m%d'))
        df.to_csv(r'D:\data\income\\'+code+'.csv')
        return 1
    except:
        print(code+' is null')
        return 0

if __name__== '_main_':
    year = 2011
    while year<2022:
        get_daily_basic(year, r'D:\data\daily_basic')
        year += 1

