# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# MAGIC %%configure -f
# MAGIC {
# MAGIC     "defaultLakehouse": {
# MAGIC         "name": "lh_gold",
# MAGIC         "id": {
# MAGIC             "variableName": "$(/**/vl_environment_variables/gold_lakehouse_id)"
# MAGIC         },
# MAGIC         "workspaceId": {
# MAGIC             "variableName": "$(/**/vl_environment_variables/workspace_id)"
# MAGIC         }
# MAGIC     }
# MAGIC 
# MAGIC }

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from notebookutils import variableLibrary

vl = variableLibrary.getLibrary("vl_environment_variables")
bronze_lh_id = vl.getVariable("bronze_lakehouse_id")
workspace_id = vl.getVariable("workspace_id")
bronze_base = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{bronze_lh_id}"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df_product = spark.read.format("delta").load(f"{bronze_base}/Tables/dbo/product")
df_region = spark.read.format("delta").load(f"{bronze_base}/Tables/dbo/region")
df_reseller = spark.read.format("delta").load(f"{bronze_base}/Tables/dbo/reseller")
df_sales = spark.read.format("delta").load(f"{bronze_base}/Tables/dbo/sales")
df_salesperson = spark.read.format("delta").load(f"{bronze_base}/Tables/dbo/salesperson")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import regexp_replace, col, to_date, date_format

#cast a int the claves
df_product = df_product.withColumn("StandardCost", regexp_replace(col("StandardCost"), r"[\$,]", "").cast("double")) \
    .withColumn("ProductKey", col("ProductKey").cast("int"))

df_region = df_region.withColumn("SalesTerritoryKey", col("SalesTerritoryKey").cast("int"))

df_reseller = df_reseller.withColumn("ResellerKey", col("ResellerKey").cast("int"))

df_salesperson = df_salesperson.withColumn("EmployeeKey", col("EmployeeKey").cast("int"))    

#display(df_salesperson)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F

#casteo a int las claves y double los importes
df_sales = df_sales.withColumn("ResellerKey", col("ResellerKey").cast("int")) \
    .withColumn("ProductKey", col("ProductKey").cast("int")) \
    .withColumn("EmployeeKey", col("EmployeeKey").cast("int")) \
    .withColumn("SalesTerritoryKey", col("SalesTerritoryKey").cast("int")) \
    .withColumn("Quantity", col("Quantity").cast("int")) \
    .withColumn("UnitPrice", regexp_replace(col("UnitPrice"), r"[\$,]", "").cast("double")) \
    .withColumn("Sales", regexp_replace(col("Sales"), r"[\$,]", "").cast("double")) \
    .withColumn("Cost", regexp_replace(col("Cost"), r"[\$,]", "").cast("double"))

# casteo de fecha a YYYYMMDD
# partimos la fecha en partes: ["August", "25", "", "2017"]
split_date = F.split(F.regexp_replace(F.col("OrderDate"), "^[A-Za-z]+, ", ""), " ")

# extraemos cada parte por separado
# Month is index 0, Day is index 1 (quitando la coma del final), Year is index 2
df_sales = df_sales.withColumn("month_str", split_date.getItem(0)) \
                   .withColumn("day_str", F.regexp_replace(split_date.getItem(1), ",", "")) \
                   .withColumn("year_str", split_date.getItem(2))

# formateamos la fecha
df_sales = df_sales.withColumn(
    "iso_date", 
    F.to_date(F.concat_ws("-", F.col("year_str"), F.col("month_str"), F.col("day_str")), "yyyy-MMMM-d")
)

# 4. Final format
df_sales = df_sales.withColumn("OrderDateKey", F.date_format(F.col("iso_date"), "yyyyMMdd").cast("int"))

#quitamos las columnas auxiliares creadas
df_sales = df_sales.drop("OrderDate", "iso_date", "month_str", "day_str", "year_str")
display(df_sales)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# escribimos las tablas en gold

df_product.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("product")

df_region.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("region")

df_reseller.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("reseller")

df_sales.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("sales")

df_salesperson.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("salesperson")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# generamos dim date

from pyspark.sql.functions import (
    col, date_format, year, month, dayofmonth, dayofweek,
    dayofyear, weekofyear, quarter, expr
)
from pyspark.sql.types import IntegerType

# rangos
df_date = (
    spark.sql("SELECT sequence(to_date('2017-07-01'), to_date('2020-05-31'), interval 1 day) as date")
    .selectExpr("explode(date) as Date")
)

df_date = (
    df_date
    .withColumn("DateKey",            date_format(col("Date"), "yyyyMMdd").cast("int"))
    .withColumn("Year",               year(col("Date")))
    .withColumn("Quarter",            quarter(col("Date")))
    .withColumn("QuarterName",        expr("concat('Q', quarter(Date))"))
    .withColumn("Month",              month(col("Date")))
    .withColumn("MonthName",          date_format(col("Date"), "MMMM"))
    .withColumn("MonthShort",         date_format(col("Date"), "MMM"))
    .withColumn("Day",                dayofmonth(col("Date")))
    .withColumn("DayOfWeek", expr("case when dayofweek(Date) = 1 then 7 else dayofweek(Date) - 1 end"))
    .withColumn("DayName",            date_format(col("Date"), "EEEE"))
    .withColumn("DayShort",           date_format(col("Date"), "EEE"))
    .withColumn("DayOfYear",          dayofyear(col("Date")))
    .withColumn("WeekOfYear",         weekofyear(col("Date")))
    .withColumn("YearMonth",          date_format(col("Date"), "yyyyMM").cast("int"))
    .withColumn("YearMonthStr", date_format(col("Date"), "yyyy-MM"))
    .withColumn("YearQuarter",        expr("concat(year(Date), '-Q', quarter(Date))"))
    .withColumn("IsWeekend", (col("DayOfWeek").isin(6, 7)).cast("int"))    
)

#display(df_date)

df_date.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("date")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
