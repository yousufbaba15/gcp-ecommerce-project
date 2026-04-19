# E-Commerce End-to-End Data Engineering Project

## 📌 Architecture Overview

```
GCS (CSV Files)
     ↓
Dataflow (Flex Template + Python)
     ↓
BigQuery (Dataset + Tables)
     ↓
Cloud Scheduler (Automation)
```

---

## 📂 GCS Bucket Structure

```
gs://hcl-de-bank-landing/
│
├── raw/
│   ├── customers.csv
│   ├── merchants.csv
│   └── transactions.csv
│
├── temp/
├── staging/
└── templates/
```

---

## ⚙️ Dataflow Pipeline (Python)

Refer to: `gcs_to_bq_pipeline.py`

### Features

- Reads CSV files from GCS
- Creates BigQuery dataset & tables (if not exists)
- Appends data to BigQuery

---

## ▶️ Run Dataflow Job (Manual Testing)

```bash
gcloud dataflow flex-template run "bank-etl-test-$(date +%s)" --template-file-gcs-location gs://hcl-de-bank-landing/templates/bank-etl.json --region us-central1 --worker-zone us-central1-a --temp-location gs://hcl-de-bank-landing/temp --staging-location gs://hcl-de-bank-landing/staging --num-workers 1 --max-workers 1 --worker-machine-type e2-small
```

---

## 🐳 Dataflow Flex Template Setup

### 1. Build Dockerfile

- Check Dockerfile for dependencies and env setup

### 2. Build Docker Image

```bash
gcloud builds submit --tag gcr.io/hcl-de-bank/dataflow-flex
```

### 3. Create Flex Template

```bash
gcloud dataflow flex-template build gs://hcl-de-bank-landing/templates/bank-etl.json --image gcr.io/hcl-de-bank/dataflow-flex --sdk-language PYTHON --metadata-file metadata.json
```

---

## ⏰ Cloud Scheduler Configuration

### Basic Configuration

| Field     | Value            |
| --------- | ---------------- |
| Name      | dataflow-etl-job |
| Region    | us-central1      |
| Frequency | _/10 _ \* \* \*  |

### Target Configuration

| Field  | Value |
| ------ | ----- |
| Type   | HTTP  |
| Method | POST  |

### Endpoint URL

```
https://dataflow.googleapis.com/v1b3/projects/hcl-de-bank/locations/us-central1/flexTemplates:launch
```

### Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "launchParameter": {
    "jobName": "bank-etl-job",
    "containerSpecGcsPath": "gs://hcl-de-bank-landing/templates/bank-etl.json",
    "environment": {
      "tempLocation": "gs://hcl-de-bank-landing/temp",
      "zone": "us-central1-b"
    }
  }
}
```

---

## 🔐 Authentication

| Field           | Value                                                    |
| --------------- | -------------------------------------------------------- |
| Auth Type       | OAuth Token                                              |
| Service Account | computeengine-default-serviceaccount.gserviceaccount.com |
| Scope           | https://www.googleapis.com/auth/cloud-platform           |

---

## ✅ Summary

This project implements a fully automated ETL pipeline using:

- Google Cloud Storage (data ingestion)
- Dataflow (processing)
- BigQuery (storage & analytics)
- Cloud Scheduler (automation)

The pipeline supports scalable, repeatable, and production-ready data ingestion workflows.
