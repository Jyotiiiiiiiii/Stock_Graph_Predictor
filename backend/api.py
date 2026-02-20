from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ensure paths are correct for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from stock_prediction_engine.src.data.data_handler import DataHandler
from stock_prediction_engine.src.features.feature_engineer import FeatureEngineer
from stock_prediction_engine.src.model.predictor import StockPredictor

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict/{ticker}")
async def get_prediction(ticker: str):
    ticker = ticker.upper()
    try:
        # 1. Data Handling
        handler = DataHandler(ticker)
        df = handler.download_data()
        if df.empty:
            raise HTTPException(status_code=404, detail="Ticker not found or no data available")
        
        df = handler.preprocess_data(df)
        
        # 2. Feature Engineering
        engineer = FeatureEngineer(df)
        df_with_features = engineer.add_technical_indicators()
        features = engineer.get_feature_list()
        
        # 3. Prediction
        predictor = StockPredictor()
        accuracy = predictor.train(df_with_features, features)
        
        # Get latest data point
        latest_row = df_with_features.tail(1)
        prediction, probability = predictor.predict_next_day(latest_row, features)
        
        direction = "UP" if prediction == 1 else "DOWN"
        confidence = float(probability[1] if prediction == 1 else probability[0])
        
        # Prepare historical data for charting (last 30 days)
        chart_data = df_with_features.tail(30).reset_index()
        history = [
            {"date": str(row['Date'].date()), "price": round(float(row['Close']), 2)}
            for _, row in chart_data.iterrows()
        ]
        
        return {
            "ticker": ticker,
            "direction": direction,
            "confidence": round(confidence * 100, 2),
            "accuracy": round(accuracy * 100, 2),
            "last_price": round(float(latest_row['Close'].values[0]), 2),
            "history": history
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
