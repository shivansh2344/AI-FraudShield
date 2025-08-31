import os
import joblib
import pandas as pd
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

# Helper function for consistent error responses
def error_response(message, status_code=400):
    """Create a consistent error response format"""
    return jsonify({
        "error": message,
        "success": False
    }), status_code

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Fix paths to be relative to the project root
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
MODEL_PATH = str(PROJECT_ROOT / "models/model.pkl")

# Load the model
def load_model():
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run the training script first.")
    try:
        blob = joblib.load(MODEL_PATH)
        if "pipe" not in blob:
            raise KeyError(f"Model file at {MODEL_PATH} does not contain the expected 'pipe' key.")
        return blob["pipe"]
    except (EOFError, ValueError) as e:
        raise ValueError(f"Model file at {MODEL_PATH} appears to be corrupted: {str(e)}")
    except Exception as e:
        raise Exception(f"Error loading model from {MODEL_PATH}: {str(e)}")

# Initialize model
try:
    model = load_model()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed status information"""
    model_status = "loaded" if model is not None else "not_loaded"
    model_error = None
    
    # If model is not loaded, try to get the error
    if model is None:
        try:
            load_model()
        except Exception as e:
            model_error = str(e)
    
    return jsonify({
        "status": "healthy",
        "model_status": model_status,
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "model_exists": Path(MODEL_PATH).exists(),
        "model_error": model_error,
        "api_version": "1.0.0"
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint to predict fraud probability for a single transaction"""
    if model is None:
        return error_response("Model not loaded", 500)
    
    try:
        # Get data from request
        data = request.json
        if not data:
            return error_response("No data provided")
        
        # Required fields
        required_fields = ["amount", "merchant_category", "device_type"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return error_response(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Create DataFrame from the input data
        record = {
            "user_id": data.get("user_id", 1234),
            "amount": data.get("amount", 0.0),
            "hour": data.get("hour", 0),
            "day_of_week": data.get("day_of_week", 0),
            "merchant_category": data.get("merchant_category", ""),
            "device_type": data.get("device_type", ""),
            "distance_from_home_km": data.get("distance_from_home_km", 0.0),
            "is_foreign": data.get("is_foreign", 0),
            "is_high_risk_merchant": data.get("is_high_risk_merchant", 0),
            "has_history_of_chargeback": data.get("has_history_of_chargeback", 0),
        }
        
        # Validate numeric fields
        try:
            record["amount"] = float(record["amount"])
            record["distance_from_home_km"] = float(record["distance_from_home_km"])
        except (ValueError, TypeError):
            return error_response("Invalid numeric values provided")
        
        x = pd.DataFrame([record])
        
        # Make prediction
        prob = model.predict_proba(x)[0, 1]
        pred = int(prob >= 0.5)
        
        # Return prediction
        return jsonify({
            "fraud_probability": float(prob),
            "is_fraud": bool(pred),
            "transaction": record
        })
    
    except Exception as e:
        # Log the full error with traceback
        print(f"Error in predict endpoint: {str(e)}")
        print(traceback.format_exc())
        return error_response(f"Error processing request: {str(e)}", 500)

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Endpoint to predict fraud probability for multiple transactions"""
    if model is None:
        return error_response("Model not loaded", 500)
    
    try:
        # Get data from request
        data = request.json
        
        if not data:
            return error_response("No data provided")
            
        if not isinstance(data, list):
            return error_response("Expected a list of transactions")
            
        if len(data) == 0:
            return error_response("Empty transaction list provided")
        
        # Create DataFrame from the input data
        df = pd.DataFrame(data)
        
        # Add user_id if missing
        if 'user_id' not in df.columns:
            df['user_id'] = range(1000, 1000 + len(df))
        
        # Check required columns
        required_columns = ["amount", "merchant_category", "device_type", "distance_from_home_km", 
                          "is_foreign", "is_high_risk_merchant", "has_history_of_chargeback"]
        cols_needed = [c for c in required_columns if c not in df.columns]
        if cols_needed:
            return error_response(f"Missing columns: {cols_needed}")
            
        # Validate numeric columns
        numeric_columns = ["amount", "distance_from_home_km"]
        for col in numeric_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    return error_response(f"Invalid numeric values in column: {col}")
        
        # Make predictions
        proba = model.predict_proba(df)[:, 1]
        preds = (proba >= 0.5).astype(int)
        
        # Prepare results
        results = []
        for i, (prob, pred) in enumerate(zip(proba, preds)):
            transaction = data[i].copy()
            transaction["fraud_probability"] = float(prob)
            transaction["is_fraud"] = bool(pred)
            results.append(transaction)
        
        # Return predictions
        return jsonify(results)
    
    except Exception as e:
        # Log the full error with traceback
        print(f"Error in batch_predict endpoint: {str(e)}")
        print(traceback.format_exc())
        return error_response(f"Error processing batch request: {str(e)}", 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)