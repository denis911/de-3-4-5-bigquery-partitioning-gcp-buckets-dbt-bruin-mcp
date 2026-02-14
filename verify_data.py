import duckdb

con = duckdb.connect('taxi_rides_ny/taxi_rides_ny.duckdb')

# Get tables in prod schema
tables = con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='prod'").fetchall()

print("=== Tables in prod schema ===")
for t in tables:
    print(f"  - {t[0]}")

print("\n=== Data counts ===")
yellow_count = con.execute("SELECT COUNT(*) FROM prod.yellow_tripdata").fetchone()[0]
print(f"Yellow tripdata: {yellow_count:,} rows")

green_count = con.execute("SELECT COUNT(*) FROM prod.green_tripdata").fetchone()[0]
print(f"Green tripdata: {green_count:,} rows")

print("\n=== Sample data from yellow_tripdata ===")
result = con.execute("SELECT * FROM prod.yellow_tripdata LIMIT 1").fetchone()
print(result)

print("\n=== Column info ===")
columns = con.execute("DESCRIBE prod.yellow_tripdata").fetchall()
for col in columns[:5]:
    print(f"  {col[0]}: {col[1]}")

con.close()
print("\n=== Verification complete ===")
