#!/usr/bin/env python
# coding: utf-8

# In[262]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

TICK_COLOURS = 'black'


# In[263]:


# date field was shadowing datetime.date class
df = pd.read_csv('delay_history.csv', 
                 parse_dates = ['date', 'scheduled_depart', 'scheduled_arrive', 'actual_arrive']).rename(columns={'date':'date_'})
df = df.assign(day_name = df.date_.dt.day_name())
for hhmm_col in ['scheduled_depart', 'scheduled_arrive', 'actual_arrive']:
    df[hhmm_col] = pd.to_datetime(df[hhmm_col], format = '%H:%M').dt.time


# In[264]:


def plot_heatmap(from_station, time_lower, time_upper, agg_col, fmt, operator = 'LM'):
    
    metrics = {
                'minutes_late' : 'Avg. minutes late',
                'on_time' : 'Percentage of trains on time',
                'cancelled' : 'Percentage of trians cancelled'
              }
    
    fig = plt.figure(figsize = (15,15))
    ax = fig.add_subplot(111)
    
    _ = sns.heatmap(df.loc[(df.operator == operator) &                            (df.from_station == from_station) &                            (df.scheduled_depart > pd.to_datetime(time_lower).time()) &                            (df.scheduled_depart < pd.to_datetime(time_upper).time())].pivot_table(values  = agg_col,
                                                                                                  index   = 'scheduled_depart',
                                                                                                  columns = 'day_name').dropna()[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']],
        annot = True,
        cmap  = 'YlOrRd',
        alpha = .5,
        fmt   = fmt,
        linecolor = None,
        square = True,
        cbar = False,
        ax = ax
    )
    
    cbar = ax.figure.colorbar(ax.collections[0])
    #cbar.set_label('Avg. mins late', color = TICK_COLOURS, size = '12')
    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_color(TICK_COLOURS)
        
    plt.title('Operator: {}\nDeparting from: {}\nMetric: {}'.format(operator, from_station, metrics[agg_col]), color = TICK_COLOURS, size = 15)
    ax.tick_params(colors = TICK_COLOURS, labelsize = 12)
    ax.set_xlabel('Day of week', color = TICK_COLOURS, size = 12)
    ax.set_ylabel('Train departure', color = TICK_COLOURS, size = 12)
    
    ax.plot()


# In[265]:


if __name__ == '__main__':
    plot_heatmap('HRW', '07:00', '09:30', 'minutes_late', '.1f')
    plot_heatmap('EUS', '17:00', '19:30', 'minutes_late', '.1f')
    plot_heatmap('HRW', '07:00', '09:30', 'cancelled', '.1%')
    plot_heatmap('EUS', '17:00', '19:30', 'cancelled', '.1%')
    plot_heatmap('HRW', '07:00', '09:30', 'on_time', '.1%')
    plot_heatmap('EUS', '17:00', '19:30', 'on_time', '.1%')

