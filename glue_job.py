import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job


# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Le o CSV
enem = (
    spark
    .read
    .format("csv")
    .option("header", True)
    .option("inferSchema", True)
    .option("delimiter", ";")
    .load("s3://datalake-lucas-024655148599/raw_data/enem/")
)

# Escreve em parquet
(
    enem
    .write
    .mode("overwrite")
    .format("parquet")
    .partitionBy("NU_ANO")
    .save("s3://datalake-lucas-024655148599/consumerzone/enem/")
)

job.commit()
