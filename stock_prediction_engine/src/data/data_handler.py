import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

class DataHandler:
    """
    Handles downloading and preparing historical stock data.
    """
    def __init__(self, ticker: str, period: str = "5y", interval: str = "1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.data = None

    def download_data(self) -> pd.DataFrame:
        """
        Downloads historical data for the given ticker.
        """
        print(f"Downloading data for {self.ticker}...")
        try:
            ticker_obj = yf.Ticker(self.ticker)
            self.data = ticker_obj.history(period=self.period, interval=self.interval)
            
            if self.data.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")
            
            # Basic cleanup
            self.data = self.data[['Open', 'High', 'Low', 'Close', 'Volume']]
            print(f"Successfully downloaded {len(self.data)} rows of data.")
            return self.data
        except Exception as e:
            print(f"Error downloading data: {e}")
            return pd.DataFrame()

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Basic preprocessing (handling missing values, etc.)
        """
        if data.empty:
            return data
            
        # Fill missing values if any
        data = data.ffill()
        
        # Add target column: 1 if Close of tomorrow > Close of today, else 0
        data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
        
        return data

if __name__ == "__main__":
    handler = DataHandler("AAPL")
    df = handler.download_data()
    df = handler.preprocess_data(df)
    print(df.tail())
