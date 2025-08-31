# AI FraudShield — Suspicious Transaction Flagging

> Hackathon project by team Innov8crew with dual interfaces: Streamlit demo + Modern HTML/JS frontend with Flask backend currently under development process
>
> Optimized for Indian banking sector with INR currency support

## 🚀 What's inside
- **Synthetic dataset generator** (`src/data/generate_synthetic.py`)
- **Feature pipeline + model training** (`src/models/train.py`)
- **Batch and single-txn prediction utils** (`src/models/predict.py`)
- **Streamlit app** for live demo (`app/app.py`)
- **Flask API backend** for serving the model (`app/api.py`)
- **Modern HTML/CSS/JS frontend** for a professional UI (`frontend/`)
- **Processed sample dataset** (`data/processed/transactions.csv`) to start instantly

## 🧰 Tech stack
Python • pandas • numpy • scikit-learn • streamlit • matplotlib • flask • flask-cors • HTML5 • CSS3 • JavaScript

## 🛠️ Setup (local)
```bash
# 1) Create venv (optional)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Generate data (optional, a sample is already provided)
python src/data/generate_synthetic.py --rows 50000 --out data/processed/transactions.csv

# 4) Train model
python src/models/train.py --data data/processed/transactions.csv --model_path models/model.pkl
```

## 🚀 Running the Application

### Option 1: Streamlit UI
```bash
# Run the Streamlit app
streamlit run app/app.py
```
The Streamlit UI will open in your default web browser at `http://localhost:8501`.

### Option 2: HTML/JS Frontend with Flask Backend

#### Step 1: Start the Flask API Server
```bash
# Start the Flask backend
python app/api.py
```
This will start the Flask server at `http://localhost:5000`.

#### Step 2: Open the HTML Frontend

**Option A: Using a simple HTTP server**
```bash
# In a new terminal window
cd frontend
python -m http.server 8000
```
Then open your browser and navigate to `http://localhost:8000`.

**Option B: Directly open the HTML file**

Simply open the `frontend/index.html` file in your web browser. However, some browsers may block API requests due to CORS policies when opening files directly. If you encounter issues, use Option A.

## 📂 Project structure
```
fraud_detection_skeleton/
├── app/
│   ├── app.py          # Streamlit application
│   └── api.py          # Flask API for the HTML frontend
├── data/
│   ├── processed/
│   │   └── transactions.csv
│   └── raw/
├── frontend/          # HTML/CSS/JS frontend
│   ├── index.html      # Main HTML file
│   ├── css/
│   │   └── styles.css  # CSS styles
│   └── js/
│       └── script.js   # JavaScript functionality
├── models/
│   └── model.pkl       # created after training
├── notebooks/          # your EDA here
├── src/
│   ├── data/
│   │   └── generate_synthetic.py
│   ├── features/
│   │   └── build_features.py
│   └── models/
│       ├── train.py
│       └── predict.py
└── requirements.txt
```

## 🧪 Evaluation (under construction)
- Focusing on **Recall** and **AUC** for fraud class
- Tracking of confusion matrix + PR curve
- Trying thresholds optimized for **F2 score** (recall-heavy)

## 🔧 Troubleshooting

### "Model not found" Error
If you encounter a "model.py not found" error in the Streamlit version, it's due to path resolution issues. The fix has been implemented in the latest version by using absolute paths instead of relative paths.

If you still encounter issues:
1. Ensure that the paths in the application are correctly set up
2. Verify that the `data/processed/transactions.csv` file exists
3. Check that you have the necessary permissions to write to the `models/` directory

### API Connection Issues
If the HTML frontend cannot connect to the Flask API:
1. Ensure the Flask server is running at `http://localhost:5000`
2. Check for any CORS issues in your browser's developer console
3. Verify that the API URL in `frontend/js/script.js` matches your Flask server address

Thankyou for showing interest in our project✨
