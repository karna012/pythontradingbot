import streamlit as st
import pandas as pd
import numpy as np
import re
import requests
import json
import pytz
import os
import matplotlib.pyplot as plt

H1=st.header('Welcome to Futures')

H2=st.header('Earn in seconds')

tf=st.radio('Time frame for trading',('1m','3m','5m','30m','1h'))

pr=st.text_input('which pair you want to trade')

limit = st.select_slider('select number of rows for prediction, each row difference represents the choosen time frame', options=[i for i in range(1,1440)])    

api_key = os.environ.get('Xfh7L86PTI39vFaJNdcHsNoMw5J6qu8W6el4oTsLZtRbUNadJYmCcRFF8pOHhv9f')
api_secret = os.environ.get('3fb5dqB2GxIIKCpHpu3TCPHQmBOl8KcugdDnYvRbSImsBawoVQdRZVJtRTqBYocy')

endpoint = 'https://fapi.binance.com/fapi/v1/klines'
params = {'symbol': pr, 'interval': tf, 'limit': limit}
response = requests.get(endpoint, params=params)
klines = response.json()

df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore' ])
df[['Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Taker buy base asset volume', 'Taker buy quote asset volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Taker buy base asset volume', 'Taker buy quote asset volume']].apply(pd.to_numeric)
df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
df['Taker sell_quote_asset_volume'] = df['Quote asset volume'] - df['Taker buy quote asset volume']
df['Taker sell_quote_asset_volume'] = df['Quote asset volume'] - df['Taker buy quote asset volume']
df = df.reindex(columns=['Open time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume','Quote asset volume'])
# Create a timezone object for IST
ist_tz = pytz.timezone("Asia/Kolkata")

# Convert the UTC time column to a datetime object and localize to UTC timezone
utc_time_col = pd.to_datetime(df['Open time']).dt.tz_localize('UTC')

# Convert the localized UTC time to IST timezone
ist_time_col = utc_time_col.dt.tz_convert(ist_tz)

# Replace the original UTC time column with the IST time column
df['ist_time'] = ist_time_col
df = df.reindex(columns=['ist_time','Open time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume','Quote asset volume'])
# set global float formatting option
pd.options.display.float_format = '{:.4f}'.format
df['ist_time'] = pd.to_datetime(df['ist_time'])
# Convert the ist_time column to a string representation
df['ist_time_str'] = df['ist_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
df = df.reindex(columns=['ist_time','ist_time_str','Open time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume','Quote asset volume'])
df.drop('ist_time',axis=1,inplace=True)
df.drop('Open time', axis=1,inplace=True)
df['Time'] = pd.to_datetime(df['ist_time_str'])
df['Date_Time'] = pd.to_datetime(df['ist_time_str'])
df.drop(columns=['ist_time_str','Time'],axis=1,inplace =True)
df['Date'] = df['Date_Time'].dt.date
df['Time'] = df['Date_Time'].dt.time
df.drop('Date_Time',axis=1,inplace=True)
df = df.reindex(columns=['Date','Time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume','Quote asset volume'])
df=df_sorted = df.sort_values('Time', ascending=False)
d1=st.dataframe(df)

@st.cache_data
def convert_df(df_var):
    return df.to_csv().encode('utf-8')
csv = convert_df(df)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f'{pr}.csv',
    mime='text/csv',
)


# Convert 'Close' column to numeric if needed
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')


# Create a new figure and axis
fig, ax = plt.subplots(figsize=(16, 9))

# Plot the 'Close' column as a line plot
df['Close'].plot(ax=ax, kind='line')

# Set the title and labels with bold font
ax.set_title('BTCUSDT Prices', fontweight='bold')
ax.set_xlabel('Date', fontweight='bold')
ax.set_ylabel('Price', fontweight='bold')


# Display the plot in Streamlit
st.pyplot(fig)
# Increase dpi for better resolution
#dpi_value = 300
#st.pyplot(fig, dpi=dpi_value)