import pandas as pd
import numpy as np

class FeatureEngineer:
    """
    Calculates technical indicators to be used as model features.
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def add_technical_indicators(self) -> pd.DataFrame:
        """
        Calculates and adds various technical indicators.
        """
        if self.data.empty:
            return self.data
            
        # 1. Moving Averages
        self.data['SMA_10'] = self.data['Close'].rolling(window=10).mean()
        self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()
        
        # 2. Relative Strength Index (RSI)
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. Volatility (Standard Deviation)
        self.data['Volatility'] = self.data['Close'].rolling(window=20).std()
        
        # 4. Momentum (Price Change)
        self.data['Momentum'] = self.data['Close'].diff(5)
        
        # 5. Price relative to SMA
        self.data['Price_SMA_Ratio'] = self.data['Close'] / self.data['SMA_50']
        
        # Drop rows with NaN values resulting from rolling calculations
        self.data = self.data.dropna()
        
        return self.data

    def get_feature_list(self):
        """
        Returns the list of column names used as features.
        """
        return ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_10', 'SMA_50', 'RSI', 'Volatility', 'Momentum', 'Price_SMA_Ratio']

if __name__ == "__main__":
    from data_handler import DataHandler
    handler = DataHandler("AAPL")
    df = handler.download_data()
    df = handler.preprocess_data(df)
    
    engineer = FeatureEngineer(df)
    df_features = engineer.add_technical_indicators()
    print(df_features.tail())
    print("\nFeatures:", engineer.get_feature_list())
