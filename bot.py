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
        
        # Convert time to IST
        ist_tz = pytz.timezone("Asia/Kolkata")
        utc_time_col = pd.to_datetime(df['Open time']).dt.tz_localize('UTC')
        ist_time_col = utc_time_col.dt.tz_convert(ist_tz)
        df['Open time'] = ist_time_col.dt.strftime('%Y-%m-%d %H:%M:%S')
        df = df.sort_values('Open time', ascending=False)
        
        return df
    
    def generate_chart(self, df):
        fig, ax = plt.subplots(figsize=(16, 9))
        df['Close'].plot(ax=ax, kind='line')
        ax.set_title('BTCUSDT Prices', fontweight='bold')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Price', fontweight='bold')
        return fig
    
    def run(self):
        st.header('Welcome to Futures trading')
        st.header('Get the pair data for data modelling')

        tf = st.radio('Time frame for trading', ('1m', '3m', '5m', '30m', '1h'))
        pr = st.text_input('Which pair are you interested in?')

        try:
            limit = st.number_input('Number of rows to fetch', min_value=1, max_value=1440, value=60)
            df = self.fetch_data(pr, tf, int(limit))
            
            if not df.empty:
                st.success('Data fetched successfully!')
                
                st.write('Data Preview:')
                st.dataframe(df.head(limit),height=600)
                csv = df.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name=f'{pr}.csv', mime='text/csv')

                # Displaying the entire DataFrame using st.table() instead of st.dataframe()

                fig = self.generate_chart(df)
                st.pyplot(fig)
            else:
                st.warning('No data available for the selected pair and time frame.')
        except Exception as e:
            st.error(f'Error occurred: {str(e)}')

if __name__ == '__main__':
    bot = FuturesApp()
    bot.run()