import streamlit as st
import pandas as pd
import requests
import os
import matplotlib.pyplot as plt
import pytz

class FuturesApp:
    def __init__(self):
        self.api_key = os.environ.get('Xfh7L86PTI39vFaJNdcHsNoMw5J6qu8W6el4oTsLZtRbUNadJYmCcRFF8pOHhv9f')
        self.api_secret = os.environ.get('3fb5dqB2GxIIKCpHpu3TCPHQmBOl8KcugdDnYvRbSImsBawoVQdRZVJtRTqBYocy')
        self.endpoint = 'https://fapi.binance.com/fapi/v1/klines'
    
    def fetch_data(self, symbol, interval, limit):
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(self.endpoint, params=params)
        klines = response.json()
        df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        df[['Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Taker buy base asset volume', 'Taker buy quote asset volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Taker buy base asset volume', 'Taker buy quote asset volume']].apply(pd.to_numeric)
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
        df['Taker sell_quote_asset_volume'] = df['Quote asset volume'] - df['Taker buy quote asset volume']
        df = df.reindex(columns=['Open time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume', 'Quote asset volume'])
        return df

    def preprocess_data(self, df):
        ist_tz = pytz.timezone("Asia/Kolkata")
        utc_time_col = pd.to_datetime(df['Open time']).dt.tz_localize('UTC')
        ist_time_col = utc_time_col.dt.tz_convert(ist_tz)
        df['ist_time'] = ist_time_col
        df = df.reindex(columns=['ist_time', 'Open time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume', 'Quote asset volume'])
        pd.options.display.float_format = '{:.4f}'.format
        df['ist_time'] = pd.to_datetime(df['ist_time'])
        df['ist_time_str'] = df['ist_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df = df.reindex(columns=['ist_time', 'ist_time_str', 'Open time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume', 'Quote asset volume'])
        df.drop('ist_time', axis=1, inplace=True)
        df.drop('Open time', axis=1, inplace=True)
        df['Time'] = pd.to_datetime(df['ist_time_str']).dt.time
        df['Date'] = pd.to_datetime(df['ist_time_str']).dt.date
        df = df.reindex(columns=['Date', 'Time', 'Open', 'Close', 'High', 'Low', 'Number of trades', 'Volume', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Taker sell_quote_asset_volume', 'Quote asset volume'])
        df_sorted = df.sort_values('Time', ascending=False)
        return df_sorted

    def generate_chart(self, df):
        fig, ax = plt.subplots(figsize=(16, 9))
        df['Close'].plot(ax=ax, kind='line')
        ax.set_title('BTCUSDT Prices', fontweight='bold')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Price', fontweight='bold')
        return fig

    def run(self):
        st.header('Welcome to Futures')
        st.header('Earn in seconds')

        tf = st.radio('Time frame for trading', ('1m', '3m', '5m', '30m', '1h'))
        pr = st.text_input('Which pair you want to trade')
        limit = st.select_slider('Select number of rows for prediction, each row difference represents the chosen time frame', options=[i for i in range(1, 1440)])

        df = self.fetch_data(pr, tf, limit)
        df_sorted = self.preprocess_data(df)
        d1 = st.dataframe(df_sorted)

        @st.cache_data
        def convert_df(df_var):
            return df_var.to_csv().encode('utf-8')

        csv = convert_df(df_sorted)

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f'{pr}.csv',
            mime='text/csv',
        )

        fig = self.generate_chart(df_sorted)
        st.pyplot(fig)

if __name__ == '__main__':
    app = FuturesApp()
    app.run()
