#!/usr/bin/env python3
import os
import sys

# Example: shp2pgsql -I -s 4326 NUTS_NL_01m_2024.shp public.geo_test | psql -h 127.0.0.1 -U user -d postgres -p 5432

INPUT_CRS = 3857

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Input error: Please provide as input the shape file and the table name.")
    exit(1)

  shape_fn = str(sys.argv[1])
  new_table_name = str(sys.argv[2])

  if not shape_fn.endswith(".shp"):
    print(f"Input error: Input file is not of shape file (.shp) {shape_fn}")
    exit(1)
  
  os.system(f"shp2pgsql -I -s {INPUT_CRS} {shape_fn} {new_table_name} | psql -h 127.0.0.1 -U user -d postgres -p 5432")
