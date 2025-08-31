
import argparse, joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier

def load_data(path:str)->pd.DataFrame:
    return pd.read_csv(path)

def build_pipeline(cat_cols, num_cols):
    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", StandardScaler(), num_cols),
        ]
    )
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        n_jobs=-1,
        class_weight="balanced_subsample",
        random_state=42,
    )
    pipe = Pipeline([("pre", pre), ("clf", model)])
    return pipe

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=str, default="data/processed/transactions.csv")
    ap.add_argument("--model_path", type=str, default="models/model.pkl")
    args = ap.parse_args()

    df = load_data(args.data)
    target = "is_fraud"
    X = df.drop(columns=[target])
    y = df[target]

    cat_cols = ["merchant_category","device_type"]
    num_cols = [c for c in X.columns if c not in cat_cols]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    pipe = build_pipeline(cat_cols, num_cols)
    pipe.fit(X_train, y_train)

    y_proba = pipe.predict_proba(X_test)[:,1]
    y_pred = (y_proba >= 0.5).astype(int)

    print("AUC:", roc_auc_score(y_test, y_proba))
    print(classification_report(y_test, y_pred, digits=4))

    Path(args.model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipe": pipe, "cat_cols": cat_cols, "num_cols": num_cols}, args.model_path)
    print(f"Saved model -> {args.model_path}")

if __name__ == "__main__":
    main()
