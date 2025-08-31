
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
rng = np.random.default_rng(42)

MERCHANTS = ["grocery","electronics","fashion","gaming","fuel","travel","utilities","restaurants","jewelry","crypto","telecom","education","healthcare","insurance","government"]
DEVICES   = ["mobile","desktop","tablet"]
DAYS      = list(range(7))

def generate(n_rows:int=10000, seed:int=42)->pd.DataFrame:
    rng = np.random.default_rng(seed)
    user_ids = rng.integers(1000, 5000, size=n_rows)
    # Generate amounts in USD first
    amounts_usd = np.exp(rng.normal(3.5, 1.0, size=n_rows))
    # Convert USD to INR (1 USD = approximately 83 INR)
    amounts = np.round(amounts_usd * 83, 2)  # right-skewed, now in INR
    hours = rng.integers(0,24,size=n_rows)
    dow = rng.choice(DAYS, size=n_rows)
    merch = rng.choice(MERCHANTS, size=n_rows, p=[0.12,0.08,0.10,0.05,0.08,0.07,0.10,0.12,0.04,0.04,0.06,0.05,0.04,0.03,0.02])
    device = rng.choice(DEVICES, size=n_rows, p=[0.7,0.25,0.05])
    dist_km = np.abs(rng.normal(5, 10, size=n_rows))  # distance from home/device locus
    is_foreign = rng.binomial(1, 0.04, size=n_rows)
    high_risk_merch = np.isin(merch, ["jewelry","crypto","electronics","travel"]).astype(int)
    chargeback_hist = rng.binomial(1, 0.06, size=n_rows)

    # Base fraud probability from several risk signals
    p = (
        0.005
        + 0.0004*(amounts - amounts.mean())
        + 0.02*( (hours<5) | (hours>22) )
        + 0.03*is_foreign
        + 0.02*high_risk_merch
        + 0.015*(dist_km>50)
        + 0.03*chargeback_hist
    )

    # Make crypto & travel at odd hours riskier
    p += 0.03*((merch=="crypto") & ((hours<6)|(hours>22)))

    # Bound probabilities
    p = np.clip(p, 0.001, 0.9)
    fraud = rng.binomial(1, p)

    df = pd.DataFrame({
        "user_id": user_ids,
        "amount": amounts,
        "hour": hours,
        "day_of_week": dow,
        "merchant_category": merch,
        "device_type": device,
        "distance_from_home_km": np.round(dist_km,2),
        "is_foreign": is_foreign,
        "is_high_risk_merchant": high_risk_merch,
        "has_history_of_chargeback": chargeback_hist,
        "is_fraud": fraud.astype(int)
    })
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=10000)
    ap.add_argument("--out", type=str, default="data/processed/transactions.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = generate(args.rows, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df):,} rows -> {args.out} | Fraud rate: {df['is_fraud'].mean():.3%}")

if __name__ == "__main__":
    main()
