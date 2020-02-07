from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import udf
from pyspark.sql.functions import col
from pyspark.sql.functions import to_timestamp
from pyspark.sql.types import StringType
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import desc
from pyspark.sql.functions import asc
from pyspark.sql.functions import sum as Fsum
from pyspark.sql import Row 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import warnings

import os

spark = SparkSession \
    .builder \
    .appName("SF")\
    .getOrCreate()

crime_time_udf = udf(lambda x : x[:2], StringType())
process_letter = udf(lambda x : str(x).lower(), StringType())

input_path = "s3a://insightcaren/"
out_path = "s3a://insightcaren/output_his/"

########################### SF #######################
## 1.
path1 = input_path + "SF1.csv"
crime_data1 = spark.read.csv(path1,header = True)
crime_data1 = crime_data1.select([process_letter("Category").alias("Category"),"DayOfWeek", "Date", crime_time_udf("Date").alias('Month'), "Time", crime_time_udf("Time").alias('Hour'), process_letter("PdDistrict").alias('PdDistrict'), col("X").alias('Long'), col("Y").alias('Lat')])

sf_crime1 = crime_data1.select(["DayOfWeek", 'Month', 'Hour', "PdDistrict"])
sf_crime1 = sf_crime1.groupBy('PdDistrict', 'DayOfWeek', 'Month', 'Hour').count()
sf_crime1.show()

## 2.
path2 = input_path + "SF2.csv"
crime_data2 = spark.read.csv(path2,header = True)
crime_data2 = crime_data2.select([col("Incident Category").alias('Category'), col("Incident Day Of Week").alias('DayOfWeek'), col("Incident Date").alias('Date'), col("Incident Time").alias('Time'), col("Police District").alias('PdDistrict'), col("Longitude").alias('Long'), col("Latitude").alias('Lat')])
crime_data2 = crime_data2.select([process_letter("Category").alias("Category"),"DayOfWeek", "Date", crime_time_udf("Date").alias('Month'), "Time", crime_time_udf("Time").alias('Hour'), process_letter("PdDistrict").alias('PdDistrict'), "Long", "Lat"])

sf_crime2 = crime_data2.select(["DayOfWeek", 'Month', 'Hour', "PdDistrict"])
sf_crime2 = sf_crime2.groupBy('PdDistrict', 'DayOfWeek', 'Month', 'Hour').count()
sf_crime2.show()

sf_crime = sf_crime1.union(sf_crime2)
sf_crime.show()
crime_data = crime_data1.union(crime_data2)
crime_data.show()

## write out
# properties = {"user": 'postgres', "password": 'postgres',"driver": "org.postgresql.Driver"}
# host = 'db1.cakrcx1k6r20.us-west-2.rds.amazonaws.com'
# portnum = '5432'
# databasename = 'db1'
# url = "jdbc:postgresql://{}:{}/{}".format(host,portnum,databasename)
# sf_crime.write.jdbc(url=url,table='SF',mode='overwrite',properties=properties)
# crime_data.jdbc(url=url,table='SF_full',mode='overwrite',properties=properties)
file_path = out_path + "SF.csv"
sf_crime.repartition(1).write.csv(file_path, mode = "overwrite", header = "true")
file_path = out_path + "SF_full.csv"
crime_data.repartition(1).write.csv(file_path, mode = "overwrite", header = "true")
#sf_crime.write.csv(out_path)

########################### Austin #######################
get_weekday = udf(lambda x : pd.Timestamp(x).weekday_name)
hour_from_stamp = udf(lambda x : str(x)[11:13], StringType())

path = input_path + "Austin.csv"
crime_data = spark.read.csv(path,header = True)
crime_data = crime_data.select([process_letter("Highest Offense Description").alias("Category"),get_weekday("Occurred Date").alias("DayOfWeek"), col("Occurred Date").alias('Date'), hour_from_stamp("Occurred Date Time").alias('Hour'), col("Occurred Date Time").alias('TimeStamp'), process_letter("Location Type").alias('PdDistrict'), col("Longitude").alias('Long'), col("Latitude").alias('Lat')])

au_crime = crime_data.select(["Category","DayOfWeek", crime_time_udf("Date").alias('Month'), 'Hour', "PdDistrict"])

au_crime = au_crime.groupBy('PdDistrict', 'Category','DayOfWeek', 'Month', 'Hour').count()
au_crime.show()

file_path = out_path + "Austin.csv"
au_crime.repartition(1).write.csv(file_path, mode = "overwrite", header = "true")
file_path = out_path + "Austin_full.csv"
crime_data.repartition(1).write.csv(file_path, mode = "overwrite", header = "true")



