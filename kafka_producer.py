#!/usr/bin/env python3
import time
import csv
import json
from kafka import KafkaProducer
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--broker", default="localhost:9093")
parser.add_argument("--topic", default="smart_meter")
parser.add_argument("--file", default="data/household_power_consumption.txt")
parser.add_argument("--interval", type=float, default=0.01)
args = parser.parse_args()

producer = KafkaProducer(
    bootstrap_servers=[args.broker],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def parse_line(row):
    return {
        "Date": row[0],
        "Time": row[1],
        "Global_active_power": None if row[2] == "?" else float(row[2]),
        "Global_reactive_power": None if row[3] == "?" else float(row[3]),
        "Voltage": None if row[4] == "?" else float(row[4]),
        "Global_intensity": None if row[5] == "?" else float(row[5]),
        "Sub_metering_1": None if row[6] == "?" else float(row[6]),
        "Sub_metering_2": None if row[7] == "?" else float(row[7]),
        "Sub_metering_3": None if row[8] == "?" else float(row[8]),
    }

if __name__ == "__main__":
    if not os.path.exists(args.file):
        raise SystemExit("File not found, run download_data.sh")

    with open(args.file, "r") as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for idx, row in enumerate(reader):
            if not row:
                continue
            producer.send(args.topic, parse_line(row))
            if idx % 1000 == 0:
                producer.flush()
            time.sleep(args.interval)
