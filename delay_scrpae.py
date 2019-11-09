#!/usr/bin/env python
# coding: utf-8

# In[167]:


import pandas as pd
import re
import numpy as np
import os
import requests

pd.options.display.max_columns = 100

SOURCE_DIR  = 'Downloads//LM//'
OUT_HTML    = 'train_delays.html'
RETURN_HTML = 'train_delays_retrun.html'
FILE_OUT    = 'delay_history.csv'
URL_OUT = "https://www.recenttraintimes.co.uk/Home/Search?Op=Srch&Fr=Harrow+%26+Wealdstone+%28HRW%29&To=London+Euston+%28EUS%29&TimTyp=D&TimDay=A&Days=Al&TimPer=Cu&dtFr={}%2F{}%2F{}&dtTo={}%2F{}%2F{}&ShwTim=AvAr&MxArCl=1000&ShwAdv=ShwAdv&TOC=All&ArrSta=5&MetAvg=Mea&MetSpr=RT&MxScDu=&MxSvAg=&MnScCt="
URL_OUT = URL_OUT.format('01', '08', '2019', '08', '11', '2019')
URL_RET = "https://www.recenttraintimes.co.uk/Home/Search?Op=Srch&Fr=London+Euston+%28EUS%29&To=Harrow+%26+Wealdstone+%28HRW%29&TimTyp=D&TimDay=A&Days=Al&TimPer=Cu&dtFr={}%2F{}%2F{}&dtTo={}%2F{}%2F{}&ShwTim=AvAr&MxArCl=1000&ShwAdv=ShwAdv&TOC=All&ArrSta=5&MetAvg=Mea&MetSpr=RT&MxScDu=&MxSvAg=&MnScCt="
URL_RET = URL_RET.format('01', '08', '2019', '08', '11', '2019')


# In[168]:


def parse_html_delays(filepath):
    
    try:
        df = pd.read_html(filepath)[1]
    except:
        print(pd.read_html(filepath)[0])
        
    df = df.droplevel(axis=1,level=0)
    df = df[list(df.columns.values[0:4]) + list(df.columns.values[23:])]
    df.columns = ['operator', 'scheduled_depart', 'scheduled_arrive', 'duration', '1/11/2019'] + [re.sub('[^0-9/]+ ', '', x) + '/2019' for x in df.columns.values[5:]]
    df = df.melt(id_vars=['operator', 'scheduled_depart', 'scheduled_arrive', 'duration'], var_name='date', value_name='status')
    df.dropna(inplace=True)
    df['cancelled'] = df.status == 'CANC/NR'
    df =\
        df.assign(
            cancelled      = df.status == 'CANC/NR',
            on_time        = df.status.str.contains('RT'),
            actual_arrival = [re.sub('[CANC/NR|Unknown]', '', x) for x in df.status.str.split(expand = True)[0]],
            minutes_late   = [re.sub('[RT|L]', '', x) for x in df.status.str.split(expand = True)[1].fillna('')]
        )
    df.loc[df.minutes_late == '', 'minutes_late'] = np.nan
    df['minutes_late'] = df.minutes_late.astype(float)
    df['date'] = pd.to_datetime(df['date'])
    for hh_mm_col in ['scheduled_depart']:
        df[hh_mm_col] = df[hh_mm_col].str.replace('*','')
    
    return(df)


# In[169]:


df_out =     parse_html_delays(URL_OUT).assign(
        from_station = 'HRW', 
        to_station = 'EUS')
    
df_return =     parse_html_delays(URL_RET).assign(
        from_station = 'EUS', 
        to_station = 'HRW')


# In[170]:


for x in [df_out.head(), '\n\n\n\n', df_return.head()]:
    print(x)


# In[171]:


if os.path.isfile(FILE_OUT):
    pd.concat([df_out, df_return]).to_csv(FILE_OUT, 
                                      header=True,
                                      index=False)
else:
    pd.concat([df_out, df_return]).to_csv(FILE_OUT,
                                      mode = 'a', 
                                      header=True,
                                      index=False)


# In[172]:


pd.read_csv(FILE_OUT).drop_duplicates().to_csv(FILE_OUT, index=False)

