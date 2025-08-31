# AI FraudShield — Real-Time Fraud Detection for Digital Transactions

Hackathon project by **Team Innov8Crew** (JEC Jabalpur)  
Developed for the **National CyberShield Hackathon 2025**

---

## Project Overview
AI FraudShield is designed to flag suspicious financial transactions in **real time** using machine learning and anomaly detection.

- End-to-end ML pipeline with **data → features → model → prediction → demo UI**  
- **Streamlit-based demo app** already functional  
- **Flask backend + HTML/CSS/JS frontend** under active development  
- Optimized for **Indian banking sector**, with INR currency support in progress  

---

## Project Status
- ✅ Core fraud detection pipeline working  
- ✅ Streamlit demo app live and testable  
- 🚧 Flask + HTML/JS frontend under development  
- 🚧 INR-specific dataset handling in progress  
- 🚧 Evaluation metrics and dashboard visualizations being improved  

---

## Features
- Synthetic dataset generator → `src/data/generate_synthetic.py`  
- Feature engineering + model training → `src/models/train.py`  
- Batch and single-transaction prediction utilities → `src/models/predict.py`  
- Streamlit demo app → `app/app.py`  
- Flask API backend → `app/api.py`  
- Modern HTML/CSS/JS frontend (in progress) → `frontend/`  
- Processed dataset → `data/processed/transactions.csv`  

---

## Tech Stack
Python • Pandas • NumPy • Scikit-learn • Streamlit • Flask • Flask-CORS • Matplotlib • HTML5 • CSS3 • JavaScript  

---

# Running the Application
- Option 1: Streamlit Demo
```streamlit run app/app.py


Available at: http://localhost:8501
```
- Option 2: HTML/JS Frontend with Flask API
```
Start backend

python app/api.py


Serve frontend

cd frontend
python -m http.server 8000


Frontend: http://localhost:8000

API: http://localhost:5000
```
## Roadmap

- INR currency optimization for Indian banks and UPI ecosystem
- Enhanced web frontend with fraud heatmaps and interactive analytics
- Advanced evaluation metrics (F2 score, ROC/PR curves)
- Deployment-ready backend (Docker/Kubernetes support)
- Continuous retraining pipeline for real-world adaptability

##Project Structure
```
fraudshield/
├── app/                # Streamlit & Flask backend
├── data/               # raw + processed datasets
├── frontend/           # HTML/CSS/JS frontend
├── models/             # trained ML models
├── notebooks/          # EDA & experiments
├── src/                # data, features, models
└── requirements.txt
```

## Evaluation (Work in Progress)

- Metrics
-- Recall
-- AUC
-- F2 score (recall-heavy)

- Visualization
-- Confusion matrix
-- Precision-Recall curve

- Priority
-- Minimize false negatives (fraud must not slip through)
