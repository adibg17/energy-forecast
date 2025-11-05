from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("kafka-to-hdfs-smart-meter") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

    kafka_bootstrap = "localhost:9093"

    schema = StructType([
        StructField("Date", StringType(), True),
        StructField("Time", StringType(), True),
        StructField("Global_active_power", DoubleType(), True),
        StructField("Global_reactive_power", DoubleType(), True),
        StructField("Voltage", DoubleType(), True),
        StructField("Global_intensity", DoubleType(), True),
        StructField("Sub_metering_1", DoubleType(), True),
        StructField("Sub_metering_2", DoubleType(), True),
        StructField("Sub_metering_3", DoubleType(), True),
    ])

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap) \
        .option("subscribe", "smart_meter") \
        .option("startingOffsets", "earliest") \
        .load()

    json_df = df.selectExpr("CAST(value AS STRING) AS json_str")
    parsed = json_df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

    combined = parsed.withColumn(
        "datetime_str",
        concat_ws(" ", col("Date"), col("Time"))
    )

    combined = combined.withColumn(
        "timestamp",
        to_timestamp(col("datetime_str"), "dd/MM/yyyy HH:mm:ss")
    )

    combined = combined.withColumn("date", col("timestamp").cast("date"))

    output_path = "hdfs://namenode:9000/user/data/smart_meter"
    # For local debugging:
    # output_path = "file:///tmp/smart_meter_parquet"

    query = combined.writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints/smart_meter_check") \
        .option("path", output_path) \
        .partitionBy("date") \
        .outputMode("append") \
        .start()

    query.awaitTermination()
