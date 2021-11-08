#created by argon
#2021/11/01

import pandas as pd
import numpy as np
import datetime as dt
import tushare as ts

def screen(code,startDay,endDay):
    df = ts.pro_bar(ts_code=code, asset='E', adj = 'hfq',start_date=startDay, end_date=endDay,factors = 'vr').sort_values(['trade_date'],ascending = True)
    try:
        if df.volume_ratio.iloc[-1] >= 2:
            return 0
        elif len(df.pct_chg[df.pct_chg > 0]) < 6:
            return 0
        elif df.close.iloc[-1] / df.close.iloc[0] - 1 < 0.2:
            return 0
        elif df.amount.mean() < 90000:
            return 0
    except:
        print(code+' not available')
        return 0
    print(code + ' get in')
    return 1

if __name__ == '__main__':
    pro = ts.pro_api()
    # get time interval, k stands for the length of the interval
    today = (dt.datetime.today() - dt.timedelta(0)).strftime('%Y%m%d')
    datedf = pro.query('trade_cal', start_date=(dt.datetime.today() - dt.timedelta(30)).strftime('%Y%m%d'), end_date=today)
    datelist = datedf[datedf.is_open == 1].copy()
    k = 10
    kdaysago = datelist.iloc[[-k], :].cal_date.values[0]
    #get adj_fac,
    adjfac = pro.query('adj_factor',  trade_date=today)
    #screening
    df = pro.daily(trade_date = today)
    df = df[df.close < 90]
    df = df[df.amount > 120000]
    judgedf = [((x[:2] == '00')or(x[:2] == '60')) for x in df.ts_code.to_list()]
    finaldf = df[judgedf]
    codelist = finaldf.ts_code
    ansList = []
    codelist.apply(screen,args = (kdaysago,today))