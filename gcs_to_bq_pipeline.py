import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from google.cloud import bigquery
import csv
import io

# -----------------------------
# CONFIGURATION
# -----------------------------
PROJECT_ID = "hcl-de-bank"
DATASET_ID = "bank_dataset"

CUSTOMERS_TABLE = "customers"
MERCHANTS_TABLE = "merchants"
TRANSACTIONS_TABLE = "transactions"


# GCS paths
CUSTOMERS_FILE = "gs://hcl-de-bank-landing/raw/customers.csv"
MERCHANTS_FILE = "gs://hcl-de-bank-landing/raw/merchants.csv"
TRANSACTIONS_FILE = "gs://hcl-de-bank-landing/raw/transactions.csv"

# -----------------------------
# CREATE DATASET & TABLES IF NOT EXISTS
# -----------------------------
def create_dataset_and_tables():
    client = bigquery.Client(project=PROJECT_ID)

    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"

    # Create Dataset if not exists
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {DATASET_ID}")

    # Define schemas
    schemas = {
        CUSTOMERS_TABLE: [
            bigquery.SchemaField("customer_id", "INTEGER"),
            bigquery.SchemaField("name", "STRING"),
            bigquery.SchemaField("age", "INTEGER"),
            bigquery.SchemaField("home_country", "STRING"),
        ],
        MERCHANTS_TABLE: [
            bigquery.SchemaField("merchant_id", "INTEGER"),
            bigquery.SchemaField("merchant_name", "STRING"),
            bigquery.SchemaField("category", "STRING"),
        ],
        TRANSACTIONS_TABLE: [
            bigquery.SchemaField("txn_id", "INTEGER"),
            bigquery.SchemaField("customer_id", "INTEGER"),
            bigquery.SchemaField("merchant_id", "INTEGER"),
            bigquery.SchemaField("amount", "FLOAT"),
            bigquery.SchemaField("timestamp", "TIMESTAMP"),
            bigquery.SchemaField("channel", "STRING"),
            bigquery.SchemaField("country", "STRING"),
        ],
    }

    # Create tables if not exist
    for table_name, schema in schemas.items():
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        try:
            client.get_table(table_ref)
            print(f"Table {table_name} exists")
        except Exception:
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            print(f"Created table {table_name}")


# -----------------------------
# PARSE CSV FUNCTIONS
# -----------------------------
def parse_csv(line, headers):
    values = list(csv.reader([line]))[0]
    return dict(zip(headers, values))


def parse_customers(line):
    headers = ["customer_id", "name", "age", "home_country"]
    row = parse_csv(line, headers)
    row["customer_id"] = int(row["customer_id"])
    row["age"] = int(row["age"])
    return row


def parse_merchants(line):
    headers = ["merchant_id", "merchant_name", "category"]
    row = parse_csv(line, headers)
    row["merchant_id"] = int(row["merchant_id"])
    return row


def parse_transactions(line):
    headers = [
        "txn_id",
        "customer_id",
        "merchant_id",
        "amount",
        "timestamp",
        "channel",
        "country",
    ]
    row = parse_csv(line, headers)
    row["txn_id"] = int(row["txn_id"])
    row["customer_id"] = int(row["customer_id"])
    row["merchant_id"] = int(row["merchant_id"])
    row["amount"] = float(row["amount"])
    return row


# -----------------------------
# PIPELINE
# -----------------------------
def run():
    # Create dataset & tables first
    create_dataset_and_tables()

    options = PipelineOptions(
        runner="DataflowRunner",
        project="hcl-de-bank",
        region="us-central1",
        temp_location="gs://hcl-de-bank-landing/temp/",
        staging_location="gs://hcl-de-bank-landing/staging/",
        save_main_session=True,
    )

    with beam.Pipeline(options=options) as p:

        # ---------------- CUSTOMERS ----------------
        (
            p
            | "Read Customers" >> beam.io.ReadFromText(CUSTOMERS_FILE, skip_header_lines=1)
            | "Parse Customers" >> beam.Map(parse_customers)
            | "Write Customers to BQ" >> beam.io.WriteToBigQuery(
                f"{PROJECT_ID}:{DATASET_ID}.{CUSTOMERS_TABLE}",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )

        # ---------------- MERCHANTS ----------------
        (
            p
            | "Read Merchants" >> beam.io.ReadFromText(MERCHANTS_FILE, skip_header_lines=1)
            | "Parse Merchants" >> beam.Map(parse_merchants)
            | "Write Merchants to BQ" >> beam.io.WriteToBigQuery(
                f"{PROJECT_ID}:{DATASET_ID}.{MERCHANTS_TABLE}",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )

        # ---------------- TRANSACTIONS ----------------
        (
            p
            | "Read Transactions" >> beam.io.ReadFromText(TRANSACTIONS_FILE, skip_header_lines=1)
            | "Parse Transactions" >> beam.Map(parse_transactions)
            | "Write Transactions to BQ" >> beam.io.WriteToBigQuery(
                f"{PROJECT_ID}:{DATASET_ID}.{TRANSACTIONS_TABLE}",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )


if __name__ == "__main__":
    run()


