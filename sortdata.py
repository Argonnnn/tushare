#created by argon
#2021/11/03

import pandas as pd
import numpy as np
import datetime as dt
import tushare as ts
import os
pro = ts.pro_api()

os.chdir('D:\data')
yearList = os.listdir()
dfList = []
for j in yearList:
    os.chdir(j)
    dayList = os.listdir()
    dfList.append(pd.concat([pd.read_csv(i,index_col=0) for i in dayList]))
    os.chdir('..')
df = pd.concat(dfList)

name = ['open', 'high', 'low', 'close', 'pre_close',
       'change', 'pct_chg', 'vol', 'amount']
for i in name:
    targetF = df.pivot(columns= 'ts_code',index = 'trade_date',values = i)
    targetF.to_pickle(i+'.pkl')


os.chdir(r'D:\factor\basic')
close = pd.read_pickle('close.pkl')
close.index = [int(q) for q in close.index]
startDay = max(close.index)
endDay = dt.datetime.today().strftime('%Y%m%d')
tradeD = pro.trade_cal(exchange='', start_date=startDay, end_date=endDay)
tradeD = tradeD[tradeD.is_open==1]
tradeList = tradeD.cal_date.to_list()
if len(close.loc[startDay,:].dropna()):
    tradeList.remove(str(startDay))


df = pd.concat([pro.daily(trade_date = i) for i in tradeList])
name = ['open', 'high', 'low', 'close', 'pre_close',
       'change', 'pct_chg', 'vol', 'amount']
for i in name:
    tempD = pd.read_pickle(i+'.pkl')
    toBeAppend = df.pivot(columns= 'ts_code',index = 'trade_date',values = i)
    toSave = pd.concat([tempD,toBeAppend],axis = 0)
    toSave.index = [str(q) for q in toSave.index]
    toSave.to_pickle(i+'.pkl')

