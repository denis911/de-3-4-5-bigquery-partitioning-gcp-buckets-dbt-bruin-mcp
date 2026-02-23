# de-3-4-5-bigquery-partitioning-gcp-buckets-dbt-duckdb-bruin-mcp

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

```sql
-- Q4 How many records have a fare_amount of 0?
SELECT  COUNT(*) 
FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned
WHERE fare_amount = 0

-- answer - 8333
;
```

```sql
-- Create a partitioned table from external table
CREATE OR REPLACE TABLE evident-axle-339820.nytaxi.yellow_tripdata_partitioned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned
;
```

```sql
-- Impact of partition - we have data only for 2024 but unpartitioned 
-- table does not know it in advance, so it has to run a query.
-- This query will process 310.24 MB when run.
SELECT DISTINCT(VendorID)
FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30'
;
```

```sql
-- This query will process 0 B when run:
-- because we have data only for 2024, nothing for 2019 - this is why 0 B .
SELECT DISTINCT(VendorID)
FROM evident-axle-339820.nytaxi.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30'
;
```

```sql
-- Q6 - query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive). 
SELECT DISTINCT(VendorID)
FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned
-- FROM evident-axle-339820.nytaxi.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2024-03-01' AND '2024-03-15'
-- non-part -  process 310.24 MB when run
-- part - will process 26.85 MB when run.
;
```

```sql
-- Q9. Write a `SELECT count(*)` query FROM the materialized table you created. 
-- How many bytes does it estimate will be read? Why?
SELECT COUNT(*)
FROM evident-axle-339820.nytaxi.yellow_tripdata_non_partitioned
-- This query will process 0 B when run. 
-- Look at table info - Number of rows 20,332,093
;
```

## Local DBT and DuckDB setup

This guide walks you through setting up a local analytics engineering environment using DuckDB and dbt.

<div align="center">

[![dbt Core](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)

</div>

>[!NOTE]
>*This guide will explain how to do the setup manually. If you want an additional challenge, try to run this setup using Docker Compose or a Python virtual environment.*

**Important**: All dbt commands must be run from inside the `taxi_rides_ny/` directory. The setup steps below will guide you through:

1. Installing the necessary tools
2. Configuring your connection to DuckDB
3. Loading the NYC taxi data
4. Verifying everything works

### Step 1: Install DuckDB

DuckDB is a fast, in-process SQL database that works great for local analytics workloads. To install DuckDB, follow the instruction on the [official site](https://duckdb.org/docs/installation) for your specific operating system.

> [!TIP]
> *You can install DuckDB in two ways. You can install the CLI or install the client API for your favorite programming language (in the case of Python, you can use `pip install duckdb` or better `uv add duckdb`).*

### Step 2: Install dbt

```bash
pip install dbt-duckdb # uv add dbt-duckdb
```

This installs:

* `dbt-core`: The core dbt framework
* `dbt-duckdb`: The DuckDB adapter for dbt

### Step 3: Configure dbt Profile

Since this repository already contains a dbt project (`taxi_rides_ny/`), you don't need to run `dbt init`. Instead, you need to configure your dbt profile to connect to DuckDB.
To copy ``` https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering/taxi_rides_ny ``` from github as a zip file I use ``` https://download-directory.github.io/ ``` website - just copy/paste the folder url and unzip the directory later.


#### Create or Update `~/.dbt/profiles.yml`

The dbt profile tells dbt how to connect to your database. Create or update the file `~/.dbt/profiles.yml` with the following content:

```yaml
taxi_rides_ny:
  target: dev
  outputs:
    # DuckDB Development profile
    dev:
      type: duckdb
      path: taxi_rides_ny.duckdb
      schema: dev
      threads: 1
      extensions:
        - parquet
      settings:
        memory_limit: '8GB'
        preserve_insertion_order: false

    # DuckDB Production profile
    prod:
      type: duckdb
      path: taxi_rides_ny.duckdb
      schema: prod
      threads: 1
      extensions:
        - parquet
      settings:
        memory_limit: '8GB'
        preserve_insertion_order: false

# Troubleshooting:
# - If you have less than 4GB RAM, try setting memory_limit to '1GB'
# - If you have 16GB+ RAM, you can increase to '4GB' for faster builds
# - Expected build time: 5-10 minutes on most systems
```

#### Step 4: Download and Ingest Data

Now that your dbt profile is configured, let's load the taxi data into DuckDB. Navigate to the dbt project directory and run the ingestion script

```python
import duckdb
import requests
from pathlib import Path

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

def download_and_convert_files(taxi_type):
    data_dir = Path("data") / taxi_type
    data_dir.mkdir(exist_ok=True, parents=True)

    for year in [2019, 2020]:
        for month in range(1, 13):
            parquet_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            parquet_filepath = data_dir / parquet_filename

            if parquet_filepath.exists():
                print(f"Skipping {parquet_filename} (already exists)")
                continue

            # Download CSV.gz file
            csv_gz_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
            csv_gz_filepath = data_dir / csv_gz_filename

            response = requests.get(f"{BASE_URL}/{taxi_type}/{csv_gz_filename}", stream=True)
            response.raise_for_status()

            with open(csv_gz_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Converting {csv_gz_filename} to Parquet...")
            con = duckdb.connect()
            con.execute(f"""
                COPY (SELECT * FROM read_csv_auto('{csv_gz_filepath}'))
                TO '{parquet_filepath}' (FORMAT PARQUET)
            """)
            con.close()

            # Remove the CSV.gz file to save space
            csv_gz_filepath.unlink()
            print(f"Completed {parquet_filename}")

def update_gitignore():
    gitignore_path = Path(".gitignore")

    # Read existing content or start with empty string
    content = gitignore_path.read_text() if gitignore_path.exists() else ""

    # Add data/ if not already present
    if 'data/' not in content:
        with open(gitignore_path, 'a') as f:
            f.write('\n# Data directory\ndata/\n' if content else '# Data directory\ndata/\n')

if __name__ == "__main__":
    # Update .gitignore to exclude data directory
    update_gitignore()

    for taxi_type in ["yellow", "green"]:
        download_and_convert_files(taxi_type)

    con = duckdb.connect("taxi_rides_ny.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS prod")

    for taxi_type in ["yellow", "green"]:
        con.execute(f"""
            CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
            SELECT * FROM read_parquet('data/{taxi_type}/*.parquet', union_by_name=true)
        """)

    con.close()
```

This script downloads yellow and green taxi data from 2019-2020, creates the `prod` schema, and loads the raw data into DuckDB. The download may take several minutes depending on your internet connection.

!!! ATTENTION !!! Resulting ```taxi_rides_ny\taxi_rides_ny.duckdb``` file is about 3GB in size - add .duckdb to gitignore - DO NOT COMMIT it to github...

### Step 5: Test the dbt Connection

Verify dbt can connect to your DuckDB database:

```bash
uv run dbt debug
```

### Step 6: Install dbt Power User Extension (VS Code Users)

If you're using Visual Studio Code, install the **dbt Power User** extension to enhance your dbt development experience.

#### What is dbt Power User?

dbt Power User is a VS Code extension that provides:

* SQL syntax highlighting and formatting for dbt models
* Inline column-level lineage visualization
* Auto-completion for dbt models, sources, and macros
* Interactive documentation preview
* Model compilation and execution directly from the editor

#### Why Not Use the Official dbt Extension?

dbt Labs released an official VS Code extension called [dbt Extension](https://marketplace.visualstudio.com/items?itemName=dbtLabsInc.dbt) powered by the new dbt Fusion engine. However, this extension **requires dbt Fusion** and does not support dbt Core.

Since we're using **dbt Core** with DuckDB for local development, we need the community-maintained **dbt Power User by AltimateAI** extension instead. This extension:

* Works seamlessly with dbt Core (not just dbt Cloud)
* Supports all dbt adapters, including DuckDB
* Is actively maintained and open source
* Provides a rich feature set for local development

#### Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "dbt Power User"
4. Install **dbt Power User by AltimateAI** (not the dbt Labs version)

Alternatively, install it from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=innoverio.vscode-dbt-power-user).

> [!NOTE]
> At this point, your local dbt environment is fully configured and ready to use.

### Additional Resources

* [DuckDB Documentation](https://duckdb.org/docs/)
* [dbt Documentation](https://docs.getdbt.com/)
* [dbt-duckdb Adapter](https://github.com/duckdb/dbt-duckdb)
* [NYC Taxi Data Dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)

### Step 7: Run duckdb UI and see if data ingested properly

To launch the DuckDB UI from your uv environment and verify the ingested data:

```bash
# From the project root, run:
uv run duckdb -ui taxi_rides_ny/taxi_rides_ny.duckdb
```

This will:

1. Open DuckDB using the CLI from your uv environment
2. Launch the built-in UI in your default browser
3. Connect to the `taxi_rides_ny.duckdb` database file

Once the UI opens, you can run SQL queries to verify the data, for example:

```sql
-- Check tables in the database
SHOW TABLES;

-- Count records in yellow_tripdata
SELECT COUNT(*) FROM prod.yellow_tripdata;

-- List schema
SELECT * FROM information_schema.tables;
```

Alternatively run ```uv run verify_data.py``` to see if data is loaded.

### Step 8: Check current config

First cd to the directory with our DBT files:

```bash
cd taxi_rides_ny
```

Then try to run a test build from there:

```bash
uv run dbt build
```

Ideally it should finish without errors - read build errors if any...
If no errors - try to check a prod build:

```bash
uv run dbt run --select prod
```

Useful DBT commands are (as a list):
(good idea to select a Python interpreter first from venv and cd taxi_rides_ny)

```bash
# 0. INIT - run once! - builds dbt project
uv run dbt init

# 1. DEBUG - checks database connection
uv run dbt debug

# 2. SEED - ingest, uploads or materialises seeds - in our case csv files for zones and ppayment types
uv run dbt seed 

# 3. RUN - less heavy than build - tries to compile models and materialise it
uv run dbt run

# 4. BUILD - heavy - builds all models + runs tests + materialises seeds.... etc etc
uv run dbt build 

# 5. DEPS - short for dependencies - installs packages
uv run dbt deps 

# 6. COMPILE - compiles sql files without jinja - ready to send to actual database engine - into target / compile folder - if I need to spot jinja errors...
uv run dbt compile 

# 7. TEST - run all tests from tests folder
uv run dbt test 

# 8. RETRY - starts from the point where last build failed.
uv run dbt retry
```

### Step 9: If all good - query the duckdb UI:

After testing dbt build, you can build the prod models and materialise them into the duckdb database - this will create the final tables in the duckdb database. For me it required increasing RAM limits to 32GB - or it was giving errors about memory overflow.
Please be patient - it can take 30 mins or so to build all tables on average i5 PC.

```bash
uv run dbt build --select prod
```

Start testing with launching duckdb UI:

```bash
cd taxi_rides_ny
uv run duckdb -ui taxi_rides_ny.duckdb
```

then you can run SQL queries to verify the data, for example:

```sql
-- Count of records in fct_monthly_zone_revenue?
-- 12184
SELECT COUNT(*)

from taxi_rides_ny.prod.fct_monthly_zone_revenue
```

or 

```sql
-- Zone with highest revenue for Green taxis in 2020? 
-- East Harlem North
SELECT revenue_monthly_total_amount, pickup_zone
FROM taxi_rides_ny.prod.fct_monthly_zone_revenue
WHERE service_type = 'Green' 
  and year(revenue_month) = 2020
ORDER BY 1 DESC
LIMIT 10

```

or

```sql
-- Zone with highest revenue for Green taxis in 2020? 
-- East Harlem North
SELECT revenue_monthly_total_amount, pickup_zone
FROM taxi_rides_ny.prod.fct_monthly_zone_revenue
WHERE service_type = 'Green' 
  and year(revenue_month) = 2020
ORDER BY 1 DESC
LIMIT 10

```

or

```sql
-- Total trips for Green taxis in October 2019?
-- 384624
SELECT COUNT(*)
from taxi_rides_ny.prod.fct_trips
WHERE service_type = 'Green' 
  and month(pickup_datetime) = 10
  and year(pickup_datetime) = 2019

```

## Starting Bruin - Simple Pipeline

This pipeline is a simple example of a Bruin project. It demonstrates how to use the `bruin` CLI to build and run a pipeline.
DuckDB was chosen for its simplicity. This setup assumes DuckDB is available; you can swap `duckdb.sql` asset types.

The pipeline includes the following sample assets:

- `dataset.players`: An ingestr asset that loads chess player data into DuckDB.
- `dataset.player_stats`: A DuckDB SQL asset that builds a table from `dataset.players`.
- `my_python_asset`: A Python asset that prints a message.

### Setup

This template includes a `.bruin.yml` with sample DuckDB and chess connections. You can replace or extend with your connections and environments as needed.

Here's a sample `.bruin.yml` file:

```yaml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: "duckdb-default"
          path: "duckdb.db"
      chess:
        - name: "chess-default"
          players:
            - "MagnusCarlsen"
            - "Hikaru"
```

You can simply switch the environment using the `--environment` flag, e.g.:

```shell
bruin validate --environment production . 
```

### Running the pipeline

bruin CLI can run the whole pipeline or any task with the downstreams:

```shell
bruin run .
```

```shell
Starting the pipeline execution...

[18:42:58] Running:  my_python_asset
[18:42:58] Running:  dataset.players
[18:42:58] [my_python_asset] >> warning: `--no-sync` has no effect when used outside of a project
[18:42:58] [my_python_asset] >> hello world
[18:42:58] Finished: my_python_asset (191ms)
⋮
[18:43:04] Finished: dataset.player_stats:player_count:not_null (24ms)
[18:43:04] Finished: dataset.player_stats:player_count:positive (33ms)
[18:43:04] Finished: dataset.player_stats:name:unique (42ms)

==================================================

PASS my_python_asset 
PASS dataset.players 
PASS dataset.player_stats .....


bruin run completed successfully in 5.439s

 ✓ Assets executed      3 succeeded
 ✓ Quality checks       5 succeeded
```

You can also run a single task:

```shell
bruin run assets/my_python_asset.py                         
```

```shell
Starting the pipeline execution...

[23:00:02] Running:  my_python_asset
[23:00:02] >> warning: `--no-sync` has no effect when used outside of a project
[23:00:02] >> hello world
[23:00:02] Finished: my_python_asset (162ms)

==================================================

PASS my_python_asset 


bruin run completed successfully in 162ms

 ✓ Assets executed      1 succeeded
```

You can optionally pass a `--downstream` flag to run the task with all of its downstreams.

That's it, you are all set. Happy Building!

If you want to dig deeper, jump into the [Concepts](https://getbruin.com/docs/bruin/getting-started/concepts.html) to learn more about the underlying concepts Bruin use for your data pipelines.
