
import streamlit as st
import pandas as pd
import os, joblib
from pathlib import Path

st.set_page_config(page_title="AI FraudShield", page_icon="🛡️", layout="wide")
st.title("🛡️ AI FraudShield — Suspicious Transaction Flagging")
st.caption("Powered by State Bank of India - Secure banking solution for Indian financial institutions")

# Fix paths to be relative to the project root
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
MODEL_PATH = str(PROJECT_ROOT / "models/model.pkl")
SAMPLE_DATA = str(PROJECT_ROOT / "data/processed/transactions.csv")

@st.cache_resource
def get_model():
    if not Path(MODEL_PATH).exists():
        st.warning("Model not found. Training a quick baseline on the sample dataset...")
        import subprocess, sys
        # Fix the path to ensure it's relative to the project root
        train_script = Path(os.path.dirname(os.path.abspath(__file__))).parent / "src" / "models" / "train.py"
        subprocess.run([sys.executable, str(train_script), "--data", SAMPLE_DATA, "--model_path", MODEL_PATH], check=True)
    blob = joblib.load(MODEL_PATH)
    return blob["pipe"]

pipe = get_model()

tab1, tab2 = st.tabs(["📤 Batch scoring (CSV)", "🧍 Single transaction"])

with tab1:
    st.subheader("Upload transactions CSV")
    st.write("Required columns are included in the sample file in `data/processed/transactions.csv`. The label column `is_fraud` is optional for scoring.")
    file = st.file_uploader("Choose CSV file", type=["csv"])
    if file:
        df = pd.read_csv(file)
        cols_needed = [c for c in ["merchant_category","device_type"] if c not in df.columns]
        if cols_needed:
            st.error(f"Missing columns: {cols_needed}")
        else:
            proba = pipe.predict_proba(df.drop(columns=[c for c in ["is_fraud"] if c in df.columns]))[:,1]
            out = df.copy()
            out["fraud_prob"] = proba
            out["is_fraud_pred"] = (out["fraud_prob"]>=0.5).astype(int)
            st.dataframe(out.head(50))
            st.download_button("Download scored CSV", out.to_csv(index=False).encode(), file_name="scored_transactions.csv")

with tab2:
    st.subheader("Enter a single transaction")
    col1, col2, col3 = st.columns(3)
    with col1:
        amount = st.number_input("Amount (₹)", min_value=0.0, value=1500.0, step=10.0)
        hour = st.slider("Hour (0-23)", 0, 23, 14)
        device_type = st.selectbox("Device Type", ["mobile","desktop","tablet"])
    with col2:
        day_of_week = st.selectbox("Day of Week (0=Mon)", list(range(7)), index=4)
        merchant_category = st.selectbox("Merchant Category", ["grocery","electronics","fashion","gaming","fuel","travel","utilities","restaurants","jewelry","crypto","telecom","education","healthcare","insurance","government"])
        distance = st.number_input("Distance from home (km)", min_value=0.0, value=2.0, step=0.5)
    with col3:
        is_foreign = st.selectbox("Is Foreign", [0,1], index=0)
        is_high_risk_merchant = st.selectbox("High Risk Merchant", [0,1], index=0)
        has_history = st.selectbox("Has Chargeback History", [0,1], index=0)

    if st.button("Score Transaction"):
        record = {
            "user_id": 1234,
            "amount": amount,
            "hour": hour,
            "day_of_week": day_of_week,
            "merchant_category": merchant_category,
            "device_type": device_type,
            "distance_from_home_km": distance,
            "is_foreign": is_foreign,
            "is_high_risk_merchant": is_high_risk_merchant,
            "has_history_of_chargeback": has_history,
        }
        x = pd.DataFrame([record])
        prob = pipe.predict_proba(x)[0,1]
        pred = int(prob>=0.5)
        st.metric("Fraud Probability", f"{prob:.2%}")
        st.write("Prediction:", "🚨 **FRAUD**" if pred==1 else "✅ Legit")

st.caption("Prototype — for demonstration only.")
