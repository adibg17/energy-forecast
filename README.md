# ✅ Windows PowerShell Commands (Complete Copy–Paste)

Below are all steps required to run the full pipeline on Windows without WSL.

------------------------------------------------------------
✅ PART 1 — Start Docker (Kafka + HDFS)
------------------------------------------------------------

Open VS Code terminal (PowerShell) and run:

    docker compose up -d
    docker compose ps

Expected services:
    zookeeper   Up
    kafka       Up
    namenode    Up
    datanode    Up

------------------------------------------------------------
✅ PART 2 — Python Environment (Windows PowerShell)
------------------------------------------------------------

Create virtual environment:

    python -m venv .venv

Activate it:

    .\.venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

------------------------------------------------------------
✅ PART 3 — Download Dataset
------------------------------------------------------------

Option A (Git Bash):

    bash download_data.sh

Option B (Manual):
Download:
https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip

Extract and move:
    data/household_power_consumption.txt

------------------------------------------------------------
✅ PART 4 — Run Kafka Producer
------------------------------------------------------------

Run producer (streams CSV → Kafka):

    python producer\kafka_producer.py --broker localhost:9093 --topic smart_meter --interval 0.005

------------------------------------------------------------
✅ PART 5 — Spark Streaming (Kafka → LOCAL Parquet)
------------------------------------------------------------

Edit spark_streaming_to_hdfs.py:
Change:

    output_path = "hdfs://namenode:9000/user/data/smart_meter"

To:

    output_path = "file:///tmp/smart_meter_parquet"

Run Spark Streaming:

    "C:\spark\spark-3.4.1-bin-hadoop3\bin\spark-submit" ^
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 ^
      spark\spark_streaming_to_hdfs.py

------------------------------------------------------------
✅ PART 6 — Train Model
------------------------------------------------------------

Train using raw CSV:

    python model\preprocess_and_train.py

Train using local Parquet:

    python model\preprocess_and_train.py --parquet_dir "C:\tmp\smart_meter_parquet"

------------------------------------------------------------
✅ PART 7 — Serve the Model (API)
------------------------------------------------------------

Start API server:

    python model\serve_model.py

API endpoint:
    http://localhost:5000/predict

------------------------------------------------------------
✅ PART 8 — Test API
------------------------------------------------------------

Send test request:

    curl -X POST http://localhost:5000/predict ^
      -H "Content-Type: application/json" ^
      -d "{\"hour\":14,\"dayofweek\":2,\"is_weekend\":0,\"gap_mean_lag_1\":1.0,\"gap_max_lag_1\":2.0}"

------------------------------------------------------------
✅ SUMMARY — 8 Commands To Run Everything
------------------------------------------------------------

    docker compose up -d
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    python producer\kafka_producer.py
    "C:\spark\spark-3.4.1-bin-hadoop3\bin\spark-submit" spark\spark_streaming_to_hdfs.py
    python model\preprocess_and_train.py
    python model\serve_model.py

------------------------------------------------------------

✅ Now your Windows Big Data + ML pipeline is fully operational.
