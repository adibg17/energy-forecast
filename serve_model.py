#!/usr/bin/env python3
from flask import Flask, request, jsonify
import joblib
import pandas as pd

MODEL_PATH = "model/peak_model.joblib"
model = joblib.load(MODEL_PATH)

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])
    pred = model.predict(df)[0]
    return jsonify({"predicted_next_hour_peak": float(pred)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
