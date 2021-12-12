import pandas as pd
import numpy as np
import tushare as ts
import datetime as dt
import os
import matplotlib.pyplot as plt

path = r'D:\factor\basic'
os.chdir(path)
pctchg = pd.read_pickle('pct_chg.pkl').sort_index().fillna(0)
close = pd.read_pickle('close.pkl').sort_index()
adj = pd.read_pickle('adj_factor.pkl')
adj = adj.sort_index().reset_index().drop_duplicates(subset = 'index',keep = 'first').set_index(keys = 'index',drop = True)
adj = adj.loc[:,close.columns]
adjclo = close*adj
n = 5
mom5 = adjclo/adjclo.shift(n) - 1

startDay = '20110104'
endDay = '20211209'
factor = mom5
def ncut(series,n):
    if n==0:
        print('n = 0')
        return
    try:
        label = list(range(n))
        cut = pd.qcut(series.dropna(),n,labels = label)
        return cut
    except:
        return(ncut(series,n-1))
factor1 = factor.apply(ncut,args=(5,),axis = 1)
s = (factor1 == 4)*1
a = s.sum(axis = 1)
sa = s.divide(a,axis = 0)
accu = (pctchg.loc[:,sa.columns] *sa.shift(2)).sum(axis=1)

netvalue = (1 + accu/100).cumprod()
netvalue.plot()
def gettable(cangwei,pct = pctchg,rf = 0.02):
    portfolioChg = (pct.loc[cangwei.index,cangwei.columns]*cangwei).sum(axis = 1)
    netvalue = (1+portfolioChg/100).cumprod()
    desDict = {}
    desDict['winrate'] = len(portfolioChg[portfolioChg>0])/len(portfolioChg)
    desDict['withdraw250'] = np.nanmax(1 - netvalue / netvalue.rolling(250).max())
    desDict['sharperatio'] =((netvalue[-1])**(250/len(netvalue))-1-rf)/np.nanstd(portfolioChg/100)/np.sqrt(250)



