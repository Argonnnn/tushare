# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 09:13:49 2019

@author: argon
"""

from WindPy import w
import pandas as pd
import datetime
def make_cache():
    w.start()
    if w.isconnected():
        print('wind数据库连接成功')
        code = w.htocode('000300', 'index', options=None).Data
        code = code[0][0]
        
        try:
            df = pd.read_pickle('cache.pkl')
            print('读取缓存成功！补充最新数据')
            begindate = df.index[-1]
            wsd_data=w.wsd(code, "high,low,open,close,volume,amt",begindate, datetime.datetime.now())
            fm=pd.DataFrame(wsd_data.Data,index=wsd_data.Fields,columns=wsd_data.Times)
            fm=fm.T #将矩阵转置
            fm = pd.concat([df,fm]).drop_duplicates()
            fm.to_pickle('cache.pkl')
            print('最新数据补充完成')
        except:
            print('读取缓存失败，开始生成近十年数据')
            wsd_data=w.wsd(code, "high,low,open,close,volume,amt", datetime.datetime.now() - datetime.timedelta(365*10), datetime.datetime.now())
            fm=pd.DataFrame(wsd_data.Data,index=wsd_data.Fields,columns=wsd_data.Times)
            fm=fm.T #将矩阵转置
            fm.to_pickle('cache.pkl')
            print('缓存成功生成')
    else:
        print('wind数据库连接失败')        
    w.close()
    return 
