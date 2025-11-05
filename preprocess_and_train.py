#!/usr/bin/env python3
import os
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import joblib

parser = argparse.ArgumentParser()
parser.add_argument("--parquet_dir", default="data_parquet")
parser.add_argument("--raw_csv", default="data/household_power_consumption.txt")
parser.add_argument("--model_out", default="model/peak_model.joblib")
args = parser.parse_args()

def load_data():
    if os.path.exists(args.parquet_dir):
        print("Reading parquet from", args.parquet_dir)
        return pd.read_parquet(args.parquet_dir)
    print("Reading raw CSV")
    return pd.read_csv(args.raw_csv, sep=';', na_values='?', low_memory=False)

def prepare_features(df):
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["Date"] + " " + df["Time"],
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce"
        )
    df = df.sort_values("timestamp").dropna(subset=["timestamp"])

    df["gap"] = pd.to_numeric(df["Global_active_power"], errors="coerce")
    df = df.dropna(subset=["gap"])

    df.set_index("timestamp", inplace=True)
    hourly = df["gap"].resample("1H").agg(["mean", "max", "sum"])
    hourly.columns = ["gap_mean", "gap_max", "gap_sum"]
    hourly = hourly.reset_index()

    hourly["hour"] = hourly["timestamp"].dt.hour
    hourly["dayofweek"] = hourly["timestamp"].dt.dayofweek
    hourly["is_weekend"] = hourly["dayofweek"].isin([5, 6]).astype(int)

    for lag in [1,2,3,6,12,24]:
        hourly[f"gap_mean_lag_{lag}"] = hourly["gap_mean"].shift(lag)
        hourly[f"gap_max_lag_{lag}"] = hourly["gap_max"].shift(lag)

    hourly["rolling_3h_max"] = hourly["gap_max"].rolling(3).max().shift(1)
    hourly["rolling_24h_mean"] = hourly["gap_mean"].rolling(24).mean().shift(1)

    hourly = hourly.dropna()
    hourly["target_peak_next"] = hourly["gap_max"].shift(-1)
    hourly = hourly.dropna(subset=["target_peak_next"])

    features = [
        c for c in hourly.columns
        if c not in ["timestamp", "gap_mean", "gap_max", "gap_sum", "target_peak_next"]
    ]

    return hourly[features], hourly["target_peak_next"], hourly

def train_and_save(X, y, out_path):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("MSE:", mean_squared_error(y_test, preds))
    print("MAE:", mean_absolute_error(y_test, preds))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(model, out_path)
    print("Saved model to", out_path)

if __name__ == "__main__":
    df = load_data()
    X, y, hourly = prepare_features(df)
    train_and_save(X, y, args.model_out)
