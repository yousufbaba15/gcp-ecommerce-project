E-COMMERCE END-TO-END DATA ENGINEERING PROJECT IMPLEMENTATION


#----------------------------
# ARCHITECTURE USED:
#----------------------------

GCS (CSV Files)
     ↓
Dataflow (Datflow Flex Template + Python)
     ↓
BigQuery (Dataset + Tables)
     ↓
Cloud Scheduler (Automation)


#----------------------------
# GCS BUCKET STRUCTURE:
#----------------------------

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


#----------------------------
# DATAFLOW PYTHON CODE:
#----------------------------

Checkout the complete code in gcs_to_bq_pipeline.py file
✔ Reads CSV from GCS
✔ Creates dataset & tables if not exist
✔ Appends data to BigQuery

RUN DATAFLOW JOB MANUALLY TO TEST 
Terminal CMD
gcloud dataflow flex-template run "bank-etl-test-$(date +%s)" \
--template-file-gcs-location gs://hcl-de-bank-landing/templates/bank-etl.json \
--region us-central1 \
--worker-zone us-central1-a \
--temp-location gs://hcl-de-bank-landing/temp \
--staging-location gs://hcl-de-bank-landing/staging \
--num-workers 1 \
--max-workers 1 \
--worker-machine-type e2-small

#----------------------------
# DATAFLOW TEMPLATE SETUP
#----------------------------

✔ Create a Dockerfile (setup in Dockerfile)
✔ Build and push image
   Terminal CMD
   gcloud builds submit --tag gcr.io/hcl-de-bank/dataflow-flex

✔ Create Flex Template
   Terminal CMD
   gcloud dataflow flex-template build gs://hcl-de-bank-landing/templates/bank-etl.json \
    --image gcr.io/hcl-de-bank/dataflow-flex \
    --sdk-language PYTHON \
    --metadata-file metadata.json

#----------------------------
# CLOUD SCHEDULER SETUP
#----------------------------

BASIC CONFIGURATIONS
| Field     | Value            |
| --------- | ---------------- |
| Name      | dataflow-etl-job |
| Region    | us-central1      |
| Frequency | */10 * * * *     |

TARGET VARAIABLES
| Field  | Value |
| ------ | ----- |
| Type   | HTTP  |
| Method | POST  |

URL: https://dataflow.googleapis.com/v1b3/projects/hcl-de-bank/locations/us-central1/flexTemplates:launch
HEADER: Content-Type: application/json
BODY: 
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

AUTH:
| Field           | Value                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------- |
| Auth Type       | OAuth Token                                                                                                     |
| Service Account | computeengine-default-serviceaccount.gserviceaccount.com |
| Scope           | [https://www.googleapis.com/auth/cloud-platform](https://www.googleapis.com/auth/cloud-platform)                |


