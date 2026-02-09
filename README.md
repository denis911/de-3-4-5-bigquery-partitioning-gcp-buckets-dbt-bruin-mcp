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

## Bigquery - playing with SQL

```sql
-- Start with creating external table from Parquet files:
-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `evident-axle-339820.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'parquet',
  uris = ['gs://evident-axle-339820-hw3-2025/yellow_tripdata_2024-*.parquet']
)
;
```

```sql
-- Q1 What is count of records for the 2024 Yellow Taxi Data?
SELECT  COUNT(*)
FROM `evident-axle-339820.nytaxi.external_yellow_tripdata`

-- answer - 20_332_093 - for the first half of 2024
;
```

```sql
-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned AS
SELECT * FROM evident-axle-339820.nytaxi.external_yellow_tripdata
;
```

```sql
-- Q2 What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?
SELECT  COUNT (DISTINCT PULocationID)
-- FROM `evident-axle-339820.nytaxi.external_yellow_tripdata`
FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned

-- answer - 262 PULocationIDs, 0B from external and 155.12 MB when run on non-partitioned materialised table
;
```

```sql
-- Q3
SELECT  COUNT (DISTINCT PULocationID) AS count_pickup_location_id,
        COUNT (DISTINCT DOLocationID) AS count_dropoff_location_id
FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned

-- answer - query will process 310.24 MB when run - from 2 columns
;
```
