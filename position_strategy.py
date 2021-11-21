#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 15:53:36 2019

@author: Argonnn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time 
import os 
import warnings
import datetime
from scipy import stats
from make_cache import *
warnings.filterwarnings("ignore")

output = os.getcwd()+'/result/'
try :
    hs300 = pd.read_pickle(r'cache.pkl')
    datelast = hs300.index[-1]
    datenow = datetime.datetime.now()
    if (datenow.date() - datelast).days >=0:
        make_cache()
        hs300 = pd.read_pickle(r'cache.pkl')
except:
    make_cache()
    hs300 = pd.read_pickle(r'cache.pkl')
        
hs300.columns = [x.lower() for x in hs300.columns] 
hs300.index.name = None
hs300.dropna(inplace = True)
window = 30
hs_ret = hs300['close'].pct_change()[1:]
#mean_ret = hs_ret.rolling(window = window).mean()
mean_ret = hs_ret.ewm(halflife = 20).mean()

upper = []
down = []
beta = []
for i,day in enumerate(hs_ret.index):
    if i < window - 1:
        continue
    y = hs300['high'][i-window+1:i+1]
    y = y - y.mean()
    x = hs300['low'][i-window+1:i+1]
    x = x - x.mean()
    beta.append((x*y).sum()/(x*x).sum())
    tem = hs_ret[i-window+1:i+1] - mean_ret[i]
    upper.append((tem[tem>0]**2).sum()/window)
    down.append((tem[tem<0]**2).sum()/window)
mean_ret = pd.DataFrame(mean_ret[window-1:])
N = 600
mean_ret['up'] = upper
mean_ret['down'] = down
mean_ret['rsrs'] = beta
mean_ret['rsrs'] = stats.boxcox(mean_ret['rsrs'])[0]
mean_ret['rsrs'] = (mean_ret['rsrs'] - mean_ret['rsrs'].rolling(window = N).mean())/mean_ret['rsrs'].rolling(window = N).std()
mean_ret['up2down'] = (mean_ret['up']/mean_ret['down'])
mean_ret['up2down'] = stats.boxcox(mean_ret['up2down'])[0]
mean_ret['up2down'] = (mean_ret['up2down'] - mean_ret['up2down'].rolling(window = N).mean())/mean_ret['up2down'].rolling(window = N).std()
w = 0.4
#mean_ret['factor'] = w*mean_ret['rsrs'] + (1-w)*mean_ret['up2down']
def newposition(factor):
    new_position = 0.1 + 1*(factor - 0.6)
    new_position = max(new_position,0.1)
    new_position = min(new_position,0.9)
    return new_position
def newposition_rsrs(factor):
    new_position = 0.1 + 0.9*(factor + 0.5)
    new_position = max(new_position,0.1)
    new_position = min(new_position,0.9)
    return new_position
position1 = list(map(lambda x:newposition(x),mean_ret['up2down']))
position2 = list(map(lambda x:newposition_rsrs(x),mean_ret['rsrs']))
position = np.array(position1)*w + np.array(position2)*(1-w)
for i,item in enumerate(position):
    if item > 0.5:
        position[i] = max(position1[i],position2[i])
    else:
        position[i] = min(position1[i],position2[i])
split = pd.cut(position,bins = [-np.inf,0.1,0.4,0.6,0.89,np.inf],labels = [0.1,0.3,0.5,0.7,0.9])
position = split.get_values()
mean_ret['suggested_position'] = position
#mean_ret['suggested_position']  = mean_ret['suggested_position'].ewm(halflife = 1).mean()
mean_ret['suggested_position'] = mean_ret['suggested_position'].shift(1)
newest_suggested_position = position[-1]
rf = 0
frac = 6/10000
capital = [10000]
position = [0]
change = [0]    
for i,day in enumerate(mean_ret.index):
    if i < 2:
        continue
    ret = hs_ret[day]
    new_position = mean_ret['suggested_position'][i]
    capital_now = position[-1]*capital[-1]*(1+ret) + (1-position[-1])*capital[-1]*(1+rf)
    position_real = position[-1]*capital[-1]*(1+ret)/capital_now
    if abs(position[-1] - new_position)>=0.05:
#        new_position = position[-1]+0.2*((position[-1] < new_position)-0.5)*2
        capital_now = capital_now - abs(capital_now*(position[-1] - new_position)*frac)
        position.append(new_position)
        change.append(1)
    else:
        position.append(position_real)
        change.append(0)
    capital.append(capital_now)
target = pd.DataFrame(hs300.loc[mean_ret.index[1:],'close'])
target['capital'] = capital
target.columns = ['hs300','tactic']
target['change'] = change
target['position'] = position
target = pd.concat([target,mean_ret['suggested_position']],axis = 1,sort = True)
target = target.dropna()
tenyr = target.loc[:,['hs300','tactic']]
tenyr = tenyr/tenyr.iloc[0,:]
tenyr['relative'] = tenyr['tactic']/tenyr['hs300']
plt.rcParams['figure.figsize'] = (24.0, 10.0)
plt.figure('a')
plt.suptitle('return in 10 yr')
plt.subplot(2,1,1)
plt.grid(True)
plt.plot(tenyr.loc[:,['hs300','tactic']])
plt.legend(['hs300','tactic'])
plt.subplot(2,1,2)
plt.plot(tenyr.loc[:,'relative'],linestyle = '--',color = 'red',linewidth = 0.6)
plt.grid(True)
plt.legend(['relative'])
plt.savefig(output+'近十年收益.png')
plt.show()


oneyr = target[['hs300','tactic']].iloc[-252:,:]
oneyr = oneyr/oneyr.iloc[0,:]
oneyr['relative'] = oneyr['tactic']/oneyr['hs300']
plt.figure('b')
plt.rcParams['figure.figsize'] = (24.0, 10.0)
plt.suptitle('return in 1 yr')
plt.subplot(2,1,1)
plt.grid(True)
plt.plot(oneyr.loc[:,['hs300','tactic']])
plt.legend(['hs300','tactic'])
plt.subplot(2,1,2)
plt.grid(True)
plt.plot(oneyr.loc[:,'relative'],linestyle = '--',color = 'red',linewidth = 0.6)
plt.legend(['relative'])
plt.savefig(output+'近一年收益.png')
plt.show()

print(r'最近1年的建议仓位和实际模拟仓位和是否调仓（0代表否，1代表是）')
print(target[['suggested_position','position','change']].iloc[-252:,:])
print('\033[4;0;31m')
print(f'最新建议仓位为：{newest_suggested_position*100}%')

result = target[['suggested_position','position','change']].iloc[-252:,:]
nextday = result.index[-1]+datetime.timedelta(1)
result.loc[nextday,:] = np.nan
result.loc[nextday,'suggested_position'] = newest_suggested_position
plt.rcParams['figure.figsize'] = (12.0, 8.0)
plt.plot(result.loc[:,['suggested_position','position']])
plt.grid(True)
plt.title('Suggested position and mimic position in last one year')
plt.legend(['suggested_position','position'])
plt.savefig(output+'近一年推荐仓位和模拟仓位.png')
plt.show()
result.to_csv(output+'近一年推荐仓位和模拟仓位.csv')