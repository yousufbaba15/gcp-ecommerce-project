FROM gcr.io/dataflow-templates-base/python3-template-launcher-base
COPY . /app
WORKDIR /app
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="gcs_to_bq_pipeline.py"
ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]
