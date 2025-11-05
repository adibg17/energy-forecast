#!/usr/bin/env bash
set -e
mkdir -p data
cd data


echo "Downloading UCI household power consumption dataset..."
URL="https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip"


if [ ! -f household_power_consumption.zip ]; then
curl -L -o household_power_consumption.zip "$URL"
fi


if [ ! -f household_power_consumption.txt ]; then
unzip -o household_power_consumption.zip
fi


echo "Done. File is data/household_power_consumption.txt"