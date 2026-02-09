# de-3-4-5-bigquery-partitioning-gcp-buckets-dbt-bruin-mcp

Assorted tech sandbox for GCP, DBT, data engineering platforms, batch and streaming.

## Overview

This project loads NYC Yellow Taxi trip data from the TLC public dataset into a Google Cloud Storage (GCS) bucket. The data is downloaded in Parquet format and uploaded concurrently for efficient processing.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd de-3-4-5-bigquery-partitioning-gcp-buckets-dbt-bruin-mcp
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Configure GCP credentials:**
   - Place your GCP service account JSON key file as `gcs.json` in the project root
   - Update `BUCKET_NAME` in `load_yellow_taxi_data.py` if needed

## Usage

Run the data loading script:

```bash
python load_yellow_taxi_data.py
```

This will:
- Download Yellow Taxi trip data (Jan-Jun 2024) from the NYC TLC public data portal
- Upload the files to the configured GCS bucket
- Verify successful uploads

## Configuration

Edit `load_yellow_taxi_data.py` to customize:
- `BUCKET_NAME` - Target GCS bucket
- `MONTHS` - List of months to download
- `DOWNLOAD_DIR` - Local download directory
- `CHUNK_SIZE` - Upload chunk size
