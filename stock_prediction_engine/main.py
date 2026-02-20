import sys
import os

# Add src to path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.data_handler import DataHandler
from src.features.feature_engineer import FeatureEngineer
from src.model.predictor import StockPredictor

def run_prediction(ticker_symbol: str):
    print(f"\n" + "="*40)
    print(f" STOCK PREDICTION ENGINE: {ticker_symbol}")
    print("="*40)
    
    # 1. Data Handling
    handler = DataHandler(ticker_symbol)
    df = handler.download_data()
    if df.empty:
        print("Failed to get data. Exiting.")
        return
    
    df = handler.preprocess_data(df)
    
    # 2. Feature Engineering
    engineer = FeatureEngineer(df)
    df_with_features = engineer.add_technical_indicators()
    features = engineer.get_feature_list()
    
    # 3. Prediction
    predictor = StockPredictor()
    accuracy = predictor.train(df_with_features, features)
    
    # Get latest data point (the today context)
    latest_row = df_with_features.tail(1)
    
    prediction, probability = predictor.predict_next_day(latest_row, features)
    
    direction = "UP" if prediction == 1 else "DOWN"
    conf = probability[1] if prediction == 1 else probability[0]
    
    print("\n" + "-"*40)
    print(f" PREDICTION FOR NEXT TRADING DAY")
    print("-"*40)
    print(f" Direction: {direction}")
    print(f" Confidence: {conf:.2%}")
    print(f" (Based on historical accuracy: {accuracy:.2%})")
    print("-"*40)
    
    if direction == "UP":
        print(" [TIP] The model suggests a bullish trend for tomorrow.")
    else:
        print(" [TIP] The model suggests a bearish trend for tomorrow.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = input("Enter Stock Ticker (e.g., TSLA, AAPL, BTC-USD): ").upper()
    
    if ticker:
        run_prediction(ticker)
    else:
        print("No ticker provided.")
