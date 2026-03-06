import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "eighth-sandbox-480216-t1-22241b4171f4.json"
client = bigquery.Client()

# Check dataset and tables
datasets = list(client.list_datasets())
if datasets:
    print(f"Datasets: {[d.dataset_id for d in datasets]}")
    for d in datasets:
        tables = list(client.list_tables(d.dataset_id))
        print(f"Tables in {d.dataset_id}: {[t.table_id for t in tables]}")
else:
    print("No datasets found.")
