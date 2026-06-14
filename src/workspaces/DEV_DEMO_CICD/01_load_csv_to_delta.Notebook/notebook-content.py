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
# MAGIC         "name": "lh_bronze",
# MAGIC         "id": {
# MAGIC             "variableName": "$(/**/vl_environment_variables/bronze_lakehouse_id)"
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


FILES_CONFIG = [
    {"file": "Product.csv", "table": "product"},
    {"file": "Region.csv", "table": "region"},
    {"file": "Reseller.csv", "table": "reseller"},
    {"file": "Salesperson.csv", "table": "salesperson"},
    {"file": "Sales.csv", "table": "sales"}
]

BASE_PATH = "Files/"

for cfg in FILES_CONFIG:
    file_path  = BASE_PATH + cfg["file"]
    table_name = cfg["table"]

    print(f"⏳ Loading {cfg['file']} → {table_name}")

    df = spark.read.format("csv").option("sep", "\t").option("header","true").load(file_path)
    df = df.toDF(*[c.strip().replace(" ", "").replace("-","") for c in df.columns])
    
    df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)
    
    print(f"   ✅ Done — {df.count()} rows, {len(df.columns)} columns\n")

print("🎉 All tables loaded.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
