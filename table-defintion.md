# Table columns for future use with DBT

We can use duckdb ui to connect and see what is inside our database,
command from vs code terminal is:

```bash
uv run duckdb -ui taxi_rides_ny/taxi_rides_ny.duckdb
```

Or run it from windows terminal - use full file name:

```
duckdb -ui C:\tmp\de-3-4-5-bigquery-partitioning-gcp-buckets-dbt-bruin-mcp\taxi_rides_ny\taxi_rides_ny.duckdb
```

After duckdb ui is connected, we can query our tables as:

```sql
from taxi_rides_ny.prod.green_tripdata
select
	VendorID,
	lpep_pickup_datetime,
	lpep_dropoff_datetime,
	store_and_fwd_flag,
	RatecodeID,
	PULocationID,
	DOLocationID,
	passenger_count,
	trip_distance,
	fare_amount,
	extra,
	mta_tax,
	tip_amount,
	tolls_amount,
	ehail_fee,
	improvement_surcharge,
	total_amount,
	payment_type,
	trip_type,
	congestion_surcharge
limit 10
```

And for yellow taxi:

```sql
from taxi_rides_ny.prod.yellow_tripdata
select
	VendorID,
	tpep_pickup_datetime,
	tpep_dropoff_datetime,
	passenger_count,
	trip_distance,
	RatecodeID,
	store_and_fwd_flag,
	PULocationID,
	DOLocationID,
	payment_type,
	fare_amount,
	extra,
	mta_tax,
	tip_amount,
	tolls_amount,
	improvement_surcharge,
	total_amount,
	congestion_surcharge
limit 10
```
