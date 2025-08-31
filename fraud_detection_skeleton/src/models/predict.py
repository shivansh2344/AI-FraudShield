
import joblib
import pandas as pd
from typing import List, Dict, Any

def load_model(path:str="models/model.pkl"):
    blob = joblib.load(path)
    return blob["pipe"]

def predict_batch(df:pd.DataFrame, model_path:str="models/model.pkl")->pd.DataFrame:
    pipe = load_model(model_path)
    proba = pipe.predict_proba(df)[:,1]
    pred = (proba>=0.5).astype(int)
    out = df.copy()
    out["fraud_prob"] = proba
    out["is_fraud_pred"] = pred
    return out

def predict_one(record:Dict[str,Any], model_path:str="models/model.pkl")->Dict[str,Any]:
    df = pd.DataFrame([record])
    out = predict_batch(df, model_path).iloc[0].to_dict()
    return out
