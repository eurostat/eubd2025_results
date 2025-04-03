import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import zipfile
import os
import xarray as xr
import cdsapi

def get_eval_script(key):
    with open("/home/eouser/Desktop/VRI/data/evalscripts.json", "r") as json_file:
        scripts = json.load(json_file)
    return scripts.get(key, "Ključ ne postoji u JSON fajlu")

def add_year_month(df, date_col_from='from', date_col_to='to'):
    """
    Dodaje kolone 'year' i 'month' u dataset na osnovu prosečnog datuma između dve vremenske kolone.
    """
    df[date_col_from] = pd.to_datetime(df[date_col_from])
    df[date_col_to] = pd.to_datetime(df[date_col_to])
    df['mid_date'] = df[date_col_from] + (df[date_col_to] - df[date_col_from]) / 2
    df['year'] = df['mid_date'].dt.year
    df['month'] = df['mid_date'].dt.month
    df.drop(columns=['mid_date'], inplace=True)
    return df

def group_data(df, value_col, group_cols=['year', 'month']):
    """
    Grupise dataset po zadatim kolonama i računa prosečnu vrednost zadate kolone.
    """
    df_grouped = df.groupby(group_cols)[value_col].mean().unstack(level=0)
    return df_grouped

def plot_time_series(df_grouped, ylabel="Srednja vrednost", title="Vremenska serija"):
    """
    Prikazuje vremenski grafikon za grupisane podatke.
    """
    plt.figure(figsize=(12, 6))
    for year in df_grouped.columns:
        plt.plot(df_grouped.index, df_grouped[year], marker='o', label=str(year))
    
    plt.xlabel("Mesec")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(ticks=range(1, 13), labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    plt.legend(title="Godina")
    plt.grid(True)
    plt.show()
    
def fetch_data_for_ndvi_year(year, bbox, evalscript,token):
    # API URL
    url = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
    # API zaglavlja
    headers = {
        "Content-Type": "application/json",
        'Accept': 'application/json',
        "Authorization": token
    }
    stats_request = {
        "input": {
            "bounds": {
                "bbox": bbox
            },
            "data": [
                {
                    "dataFilter": {
                        "mosaickingOrder": "leastCC"
                    },
                    "type": "sentinel-2-l2a"
                }
            ]
        },
        "aggregation": {
            "timeRange": {
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year}-12-31T23:59:59Z"
            },
            "aggregationInterval": {
                "of": "P30D"
            },
            # "width": 512,
            # "height": 454.057,
            "width": 256,
            "height": 227,
            "evalscript": evalscript
        },
        "calculations": {
            "default": {
                "statistics": {
                    "default": {
                        "percentiles": {
                            "k": [25, 50, 75],
                            "interpolation": "higher"
                        }
                    }
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=stats_request)
    
    # Provera statusnog koda API odgovora
    if response.status_code != 200:
        print(f"⚠️ Greška u zahtevu za {year}: {response.status_code}")
        print(f"Odgovor API-ja: {response.text}")
        return pd.DataFrame()
    
    sh_statistics = response.json()

    # Provera API odgovora pre obrade podataka
    if "data" not in sh_statistics:
        print(f"⚠️ Nema podataka za {year}. API odgovor: {sh_statistics}")
        return pd.DataFrame()

    # Transformacija podataka u listu rečnika
    data = data = [
        {
            "from": entry["interval"]["from"],
            "to": entry["interval"]["to"],
            "B0_min": entry["outputs"]["data"]["bands"]["B0"]["stats"]["min"],
            "B0_max": entry["outputs"]["data"]["bands"]["B0"]["stats"]["max"],
            "B0_mean": entry["outputs"]["data"]["bands"]["B0"]["stats"]["mean"],
            "B0_stDev": entry["outputs"]["data"]["bands"]["B0"]["stats"]["stDev"],
            "B1_min": entry["outputs"]["data"]["bands"]["B1"]["stats"]["min"],
            "B1_max": entry["outputs"]["data"]["bands"]["B1"]["stats"]["max"],
            "B1_mean": entry["outputs"]["data"]["bands"]["B1"]["stats"]["mean"],
            "B1_stDev": entry["outputs"]["data"]["bands"]["B1"]["stats"]["stDev"],
            "B2_min": entry["outputs"]["data"]["bands"]["B2"]["stats"]["min"],
            "B2_max": entry["outputs"]["data"]["bands"]["B2"]["stats"]["max"],
            "B2_mean": entry["outputs"]["data"]["bands"]["B2"]["stats"]["mean"],
            "B2_stDev": entry["outputs"]["data"]["bands"]["B2"]["stats"]["stDev"],
            "year": year
        }
        for entry in sh_statistics["data"]
    ]

    return pd.DataFrame(data)


def fetch_data_for_moisi_year(year,bbox,evalscript,token):
    # API URL
    url = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
    # API zaglavlja
    headers = {
        "Content-Type": "application/json",
        'Accept': 'application/json',
        "Authorization": token
    }
    stats_request = {
        "input": {
            "bounds": {
                "bbox": bbox},
            "data": [
                {
                    "dataFilter": {
                        "mosaickingOrder": "leastCC"
                    },
                    "type": "sentinel-2-l2a"
                }
            ]
        },
        "aggregation": {
            "timeRange": {
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year}-12-31T23:59:59Z"
            },
            "aggregationInterval": {
                "of": "P30D"
            },
            # "width": 512,
            # "height": 454.057,
            "width": 256,
            "height": 227,
            "evalscript": evalscript
        },
        "calculations": {
            "default": {
                "statistics": {
                    "default": {
                        "percentiles": {
                            "k": [25, 50, 75],
                            "interpolation": "higher"
                        }
                    }
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=stats_request)
    sh_statistics = response.json()

    # Provera da li API odgovor sadrži "data"
    if "data" not in sh_statistics:
        print(f"⚠️ Nema podataka za {year}. API odgovor: {sh_statistics}")
        return pd.DataFrame()  # Vraća prazan DataFrame ako nema podataka

    data = []
    
    for entry in sh_statistics["data"]:
        interval_from = entry["interval"]["from"]
        interval_to = entry["interval"]["to"]
        
        # Accessing 'default' band statistics
        default_bands = entry["outputs"].get("default", {}).get("bands", {})
        B0_stats = default_bands.get("B0", {}).get("stats", {})
        B1_stats = default_bands.get("B1", {}).get("stats", {})
        B2_stats = default_bands.get("B2", {}).get("stats", {})
        B3_stats = default_bands.get("B3", {}).get("stats", {})
        
        # Accessing 'index' band statistics
        index_bands = entry["outputs"].get("index", {}).get("bands", {})
        index_stats = index_bands.get("B0", {}).get("stats", {})
        
        # Accessing 'eobrowserStats' band statistics
        eobrowser_stats_bands = entry["outputs"].get("eobrowserStats", {}).get("bands", {})
        eobrowser_B0_stats = eobrowser_stats_bands.get("B0", {}).get("stats", {})
        eobrowser_B1_stats = eobrowser_stats_bands.get("B1", {}).get("stats", {})
        
        data.append({
            "from": interval_from,
            "to": interval_to,
            "B0_min": B0_stats.get("min"),
            "B0_max": B0_stats.get("max"),
            "B0_mean": B0_stats.get("mean"),
            "B0_stDev": B0_stats.get("stDev"),
            "B1_min": B1_stats.get("min"),
            "B1_max": B1_stats.get("max"),
            "B1_mean": B1_stats.get("mean"),
            "B1_stDev": B1_stats.get("stDev"),
            "B2_min": B2_stats.get("min"),
            "B2_max": B2_stats.get("max"),
            "B2_mean": B2_stats.get("mean"),
            "B2_stDev": B2_stats.get("stDev"),
            "B3_min": B3_stats.get("min"),
            "B3_max": B3_stats.get("max"),
            "B3_mean": B3_stats.get("mean"),
            "B3_stDev": B3_stats.get("stDev"),
            "index_min": index_stats.get("min"),
            "index_max": index_stats.get("max"),
            "index_mean": index_stats.get("mean"),
            "index_stDev": index_stats.get("stDev"),
            "eobrowserStats_B0_min": eobrowser_B0_stats.get("min"),
            "eobrowserStats_B0_max": eobrowser_B0_stats.get("max"),
            "eobrowserStats_B0_mean": eobrowser_B0_stats.get("mean"),
            "eobrowserStats_B0_stDev": eobrowser_B0_stats.get("stDev"),
            "eobrowserStats_B1_min": eobrowser_B1_stats.get("min"),
            "eobrowserStats_B1_max": eobrowser_B1_stats.get("max"),
            "eobrowserStats_B1_mean": eobrowser_B1_stats.get("mean"),
            "eobrowserStats_B1_stDev": eobrowser_B1_stats.get("stDev"),
        })
    
    return pd.DataFrame(data)


def read_grib_from_zip(zip_path, extract_path, output_csv=None):
    """
    Čita GRIB dataset iz ZIP arhive, ekstrahuje podatke, konvertuje temperaturu iz Kelvina u Celzijuse i čuva u CSV.
    
    :param zip_path: Putanja do ZIP fajla
    :param extract_path: Putanja gde će se fajlovi ekstrahovati
    :param output_csv: Putanja do CSV fajla (ako je None, ne čuva CSV)
    :return: xarray dataset sa konvertovanom temperaturom
    """
    # Otpakivanje ZIP arhive
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # Pronalazak GRIB fajla
    grib_files = [f for f in os.listdir(extract_path) if f.endswith(".grib")]
    if not grib_files:
        raise FileNotFoundError("GRIB fajl nije pronađen u otpakovanom direktorijumu.")
    
    grib_path = os.path.join(extract_path, grib_files[0])
    
    # Učitavanje GRIB podataka
    ds = xr.open_dataset(grib_path, engine="cfgrib")
    
    # Konverzija temperature iz Kelvina u Celzijuse
    if "t2m" in ds:
        ds["t2m"] = ds["t2m"] - 273.15
    
    ds = ds.to_dataframe().reset_index()
    
    return ds

def plot_monthly_temperature(df):
    """
    Prikazuje vremensku seriju mesečnih prosečnih temperatura po godinama.
    
    :param df: Pandas DataFrame koji sadrži temperature i vremenske podatke
    """
    if "t2m" not in df.columns:
        raise ValueError("DataFrame ne sadrži kolonu 't2m'. Proveri unos podataka.")
    
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    monthly_avg = df.groupby(["year", "month"])["t2m"].mean().unstack(level=0)

    plt.figure(figsize=(12, 6))
    monthly_avg.plot(marker='o', colormap='coolwarm', figsize=(12, 6))

    plt.xlabel("Mesec")
    plt.ylabel("Temperatura (°C)")
    plt.title("Mesečne prosečne temperature po godinama")
    plt.grid(True)
    plt.xticks(np.arange(1, 13), 
               ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Avg", "Sep", "Okt", "Nov", "Dec"])
    plt.legend(title="Godina")
    plt.show()

# def check_and_download_zip(zip_path, dataset, request):
#     """
#     Proverava da li ZIP fajl postoji na zadatoj putanji. Ako ne postoji, preuzima ga sa CDS API-ja.
    
#     :param zip_path: Putanja do ZIP fajla
#     :param dataset: Naziv dataset-a za preuzimanje sa CDS API-ja
#     :param request: Parametri za preuzimanje podataka
#     """
#     if os.path.exists(zip_path):
#         print(f"✔ ZIP fajl već postoji: {zip_path}")
#     else:
#         print(f"⏳ ZIP fajl ne postoji, započinjem preuzimanje...")
#         client = cdsapi.Client(url='https://cds.climate.copernicus.eu/api', key='24c1dee0-725b-4152-b481-106a135bbebe')
#         client.retrieve(dataset, request).download(zip_path)
#         print(f"✔ Preuzimanje završeno: {zip_path}")

def check_and_download_zip(zip_path, dataset, request):
    """
    Checks if the ZIP file exists at the given path. If it exists, deletes it.
    Then, downloads it from the CDS API.

    :param zip_path: Path to the ZIP file
    :param dataset: Name of the dataset to download from the CDS API
    :param request: Parameters for downloading the data
    """
    # Check if the ZIP file exists
    if os.path.exists(zip_path):
        try:
            # Attempt to delete the existing file
            os.remove(zip_path)
            print(f"✔ Existing ZIP file deleted: {zip_path}")
        except OSError as e:
            print(f"❌ Error deleting file {zip_path}: {e}")
            return
    else:
        print(f"ℹ No existing ZIP file found at: {zip_path}")

    # Initialize the CDS API client
    client = cdsapi.Client(url='https://cds.climate.copernicus.eu/api', key='24c1dee0-725b-4152-b481-106a135bbebe')

    # Attempt to download the new ZIP file
    try:
        print(f"⏳ Starting download...")
        client.retrieve(dataset, request).download(zip_path)
        print(f"✔ Download completed: {zip_path}")
    except Exception as e:
        print(f"❌ Error during download: {e}")


def plot_precipitation_by_month(df):
    """
    Plots the mean precipitation by month for each year.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'time' and 'precip' columns.

    Returns:
    None
    """
    # Convert 'time' column to datetime
    df["time"] = pd.to_datetime(df["time"])

    # Extract year and month
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month

    # Group by year and month, then calculate mean precipitation
    df_grouped = df.groupby(["year", "month"])["precip"].mean().unstack(level=0)

    # Plot
    plt.figure(figsize=(12, 6))
    for year in df_grouped.columns:
        plt.plot(df_grouped.index, df_grouped[year], marker="o", linestyle="-", label=f"{year}")

    # Labels and title
    plt.xlabel("Month")
    plt.ylabel("Mean Precipitation (mm)")
    plt.title("Mean Monthly Precipitation Over the Years")
    plt.xticks(ticks=range(1, 13), labels=[
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ])
    plt.legend(title="Year", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)

    # Show plot
    plt.show()

def calculate_vri(df_ndvi, df_moisi, df_temp, df_prec, NUTS3):
    df_temp['year'] = pd.to_datetime(df_temp['time']).dt.year
    df_temp['month'] = pd.to_datetime(df_temp['time']).dt.month
    df_prec['year'] = pd.to_datetime(df_prec['time']).dt.year
    df_prec['month'] = pd.to_datetime(df_prec['time']).dt.month
    # Standardize column names for ALL DataFrames
    df_ndvi.columns = df_ndvi.columns.str.lower().str.strip()
    df_moisi.columns = df_moisi.columns.str.lower().str.strip()
    df_temp.columns = df_temp.columns.str.lower().str.strip()
    df_prec.columns = df_prec.columns.str.lower().str.strip()

    # # Merge datasets on year, month, and NUTS3
    # # Spajamo prve dvije tabele po 'year', 'month' i 'nuts3'
    # df_all = df_ndvi.merge(df_moisi, on=['year', 'month', 'nuts3'], suffixes=('_ndvi', '_moisi'))
    
    # # Zatim spajamo s tabelom sa temperaturama
    # df_all = df_all.merge(df_temp, on=['year', 'month', 'nuts3'], suffixes=('', '_temp'))
    
    # # Na kraju spajamo i tabelu sa padavinama
    # df_all = df_all.merge(df_prec, on=['year', 'month', 'nuts3'], suffixes=('', '_prec'))
    
    # # Provjera rezultata:
    # df_all.head()

    # Aggregate temperature data by year, month, and nuts3
    df_temp_agg = df_temp.groupby(['year', 'month', 'nuts3'])[['t2m', 't2m_scaled']].mean().reset_index()
    
    # Aggregate precipitation data by year, month, and nuts3
    df_prec_agg = df_prec.groupby(['year', 'month', 'nuts3'])[['precip', 'precip_scaled']].mean().reset_index()
    
    # Merge NDVI and MOISI DataFrames with suffixes for overlapping columns
    df_all = pd.merge(df_ndvi, df_moisi, on=['year', 'month', 'nuts3'], suffixes=('_ndvi', '_moisi'))
    
    # Merge with aggregated temperature data
    df_all = pd.merge(df_all, df_temp_agg, on=['year', 'month', 'nuts3'])
    
    # Merge with aggregated precipitation data
    df_all = pd.merge(df_all, df_prec_agg, on=['year', 'month', 'nuts3'])
    


    # Pivot data
    df_pivot = df_all.pivot_table(index=["year", "month", "nuts3"], 
                                  values=["b0_mean_scaled", "b0_mean_moisi", "t2m_scaled", "precip_scaled"])
    df_pivot = df_pivot.reset_index()

    # Fill NaN values with 0
    df_pivot.fillna(0, inplace=True)

    # Add NDVI from the previous month
    df_pivot["ndvi_before"] = df_pivot["b0_mean_scaled"].shift(1)
    df_pivot["ndvi_before"] = df_pivot["ndvi_before"].fillna(df_pivot["b0_mean_scaled"])

    # Define weight coefficients
    w_NDVI = 0.5
    w_MOISI = 0.25
    w_TEMP = 0.05
    w_PREC = 0.2

    # Calculate VRI using normalized values
    df_pivot["vri"] = (w_NDVI * (df_pivot["b0_mean_scaled"] / df_pivot["ndvi_before"])) + \
                        (w_MOISI * df_pivot["b0_mean_moisi"]) + (w_PREC * df_pivot["precip_scaled"]) + \
                        (w_TEMP * (1 - df_pivot["t2m_scaled"]))

    return df_pivot

