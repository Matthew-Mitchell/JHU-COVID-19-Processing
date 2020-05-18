import pandas as pd
import pickle
from datetime import date, timedelta, datetime

#Import State Lat/Long Dicts
#Lat
pkl_file = open('states_lat_dict.pkl', 'rb')
states_lat_dict = pickle.load(pkl_file)
pkl_file.close()

#Long
pkl_file = open('states_long_dict.pkl', 'rb')
states_long_dict = pickle.load(pkl_file)
pkl_file.close()

#Import Baseline File
jhuBaseDir = '/home/matt/Documents/Projects/WebDev/CoronaVirus/COVID-19/'
df = pd.read_csv(jhuBaseDir+'archived_data/archived_time_series/time_series_19-covid-Confirmed_archived_0325.csv')

dfs = [] #Make a list of dfs
#Iterate through desired date columns and create df
d1 = date(2020, 1, 22)  # start date
y, m, d = [int(x) for x in datetime.now().strftime('%Y-%m-%d').split('-')]
d2 = date(2020, 3, 22)  # end date
delta = d2 - d1         # timedelta

dates = []
for i in range(delta.days):
    d = d1 + timedelta(i)
    dates.append(d.strftime('%-m/%-d/%y'))


standard_cols = ['Province/State', 'Country/Region', 'Lat', 'Long']
for col in dates:
    temp = df[standard_cols+[col]]
    temp.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', 'ConfirmedCases']
    temp['Date'] = col
    #Append df
    dfs.append(temp)
#Concat Dataframes
transformed = pd.concat(dfs, ignore_index=True)
print(len(transformed))
transformed.Date = pd.to_datetime(transformed.Date)
transformed.Date = transformed.Date.dt.strftime('%Y-%m-%d')

daily_dir = jhuBaseDir + 'csse_covid_19_data/csse_covid_19_daily_reports/'
# dates = ['03-{}-2020'.format(i) for i in range(23,31)]

d1 = date(2020, 3, 23)  # start date
y, m, d = [int(x) for x in datetime.now().strftime('%Y-%m-%d').split('-')]
d2 = date(y, m, d)  # end date
delta = d2 - d1         # timedelta

dates = []

for i in range(delta.days):
    d = d1 + timedelta(i)
    dates.append(d.strftime('%m-%d-%Y'))

files = [date+'.csv' for date in dates]

# dfs = []
for i, file in enumerate(files):
    daily = pd.read_csv(daily_dir+file)
    columns = ['Province_State', 'Country_Region', 'Last_Update', 'Combined_Key',
               'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active'
              ]
    daily = daily.rename({'Province_State':'Province/State',
                         'Country_Region':'Country/Region',
                         'Confirmed':'ConfirmedCases',
                         'Long_':'Long'}, axis=1)
    numericalCols = ['ConfirmedCases', 'Deaths', 'Recovered', 'Active']

    us = daily[daily['Country/Region']=='US']
    us = us.groupby(['Province/State', 'Country/Region'])['ConfirmedCases'].sum().reset_index()
    us['Lat'] = us['Province/State'].map(states_lat_dict)
    us['Long'] = us['Province/State'].map(states_long_dict)
    other = daily[daily['Country/Region']!='US']
    daily = pd.concat([other, us])
    daily['Date'] = dates[i]
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily['Date'] = daily['Date'].dt.strftime('%Y-%m-%d')
   
    daily = daily[transformed.columns]
    print('Current Length:', len(transformed))
    print('Adding {} rows. Next length should read: {}'.format(len(daily), len(transformed)+len(daily)))
    transformed = transformed.append(daily, ignore_index=True)

idx_to_update = transformed[(transformed['Province/State']=='French Polynesia')
           & (transformed['Date']=='2020-03-23')].index[0]
transformed.iat[idx_to_update, 4] = 25

#Add NewCases Column
locCols = ['Province/State', 'Country/Region', 'Lat', 'Long']
transformed['Date'] = pd.to_datetime(transformed['Date'])
transformed = transformed.sort_values(by='Date')
transformed['Province/State'] = transformed['Province/State'].fillna('')
transformed['NewCases'] = transformed.groupby(locCols)['ConfirmedCases'].diff()

#Subset Data to Select Dates
transformed['Date'] = transformed['Date'].dt.strftime('%Y-%m-%d')

dates = ['2020-01-22','2020-01-26', '2020-02-02', '2020-02-09', '2020-02-16', '20202-02-23',
         '2020-03-01','2020-03-05','2020-03-08','2020-03-12', '2020-03-16', '2020-03-20']

d1 = date(2020, 3, 23)  # start date
y, m, d = [int(x) for x in datetime.now().strftime('%Y-%m-%d').split('-')]
d2 = date(y, m, d)  # end date (Today)
delta = d2 - d1         # timedelta
weekago = d2 - timedelta(weeks=1)
interval = 4
nIntervals = (weekago - d1).days // interval

#Once a week until a week ago
for i in range(nIntervals):
    d = d1 + timedelta(i*interval)
    dates.append(d.strftime('%Y-%m-%d'))

#Daily For Past Week
for i in range(7):
    d = weekago + timedelta(i)
    dates.append(d.strftime('%Y-%m-%d'))
transformed = transformed[transformed.Date.isin(dates)]
#Save
dir_ = '/home/matt/Documents/Projects/WebDev/mmitchell_net/FlaskApp/static/data/'
yesterday = datetime.now()-timedelta(1)
filename = 'Confirmed_Cases_through_{}.csv'.format(yesterday.strftime('%b%d'))
print("Saving to:", filename)
transformed.to_csv(dir_+filename, index=False)