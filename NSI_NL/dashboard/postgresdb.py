import geopandas as gpd
import psycopg2
import config

def select_rows(table_name: str) -> gpd.GeoDataFrame:
  ret = None

  try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )

    # Execute a query
    sql_query = f"SELECT * FROM {table_name};"

    ret = gpd.GeoDataFrame.from_postgis(sql_query, conn)

    conn.close()

  except Exception as e:
    print(f"Error: {e}")

  return ret

