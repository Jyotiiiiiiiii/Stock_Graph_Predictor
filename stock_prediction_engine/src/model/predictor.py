import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class StockPredictor:
    """
    Handles training, evaluating, and predicting using a Random Forest model.
    """
    def __init__(self, model_path: str = "model.joblib"):
        self.model_path = model_path
        self.model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
        self.is_trained = False

    def train(self, df: pd.DataFrame, features: list):
        """
        Trains the model on the provided data.
        """
        X = df[features]
        y = df['Target']
        
        # Time-based split (keep last 20% for testing)
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        preds = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, preds)
        print(f"Model Accuracy: {accuracy:.2%}")
        # print("Classification Report:\n", classification_report(y_test, preds))
        
        self.is_trained = True
        return accuracy

    def predict_next_day(self, latest_data_row: pd.DataFrame, features: list):
        """
        Predicts if the stock will go up or down for the next trading day.
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions.")
            
        prediction = self.model.predict(latest_data_row[features])
        probability = self.model.predict_proba(latest_data_row[features])
        
        return prediction[0], probability[0]

    def save_model(self):
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            print(f"Model loaded from {self.model_path}")
        else:
            print("No saved model found.")
