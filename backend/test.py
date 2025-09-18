import xarray as xr
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

def ingest_argo_file(nc_file_path, db_connection_string):
    """
    Reads an Argo NetCDF file, checks for BGC data, and loads it
    into a PostgreSQL database with separate date and time columns.
    """
    engine = create_engine(db_connection_string)
    
    with xr.open_dataset(nc_file_path) as ds:
        num_profiles = ds.sizes['N_PROF']
        platform_number = int(ds['PLATFORM_NUMBER'].values[0])
        print(f"Processing {num_profiles} profiles from float {platform_number}...")

        for i in range(num_profiles):
            full_timestamp = pd.to_datetime(ds['JULD'].values[i])
            profile_data = {
                'latitude': ds['LATITUDE'].values[i],
                'longitude': ds['LONGITUDE'].values[i],
                'profile_date': full_timestamp.date(),
                'profile_time': full_timestamp.time(),
                'float_wmo_id': platform_number
            }
            
            profile_df_single = pd.DataFrame([profile_data])
            
            try:
                profile_df_single.to_sql('profiles', engine, if_exists='append', index=False)
                
                with engine.connect() as conn:
                    stmt = text("""
                        SELECT profile_id FROM profiles 
                        WHERE float_wmo_id = :wmo_id AND profile_date = :p_date AND profile_time = :p_time
                    """)
                    result = conn.execute(stmt, {
                        "wmo_id": platform_number, 
                        "p_date": profile_data['profile_date'],
                        "p_time": profile_data['profile_time']
                    })
                    profile_id = result.scalar()

                if profile_id is None:
                    continue

                # Start with core measurements
                measurements_data = {
                    'profile_id': profile_id,
                    'pressure_dbar': ds['PRES'].values[i],
                    'temperature_celsius': ds['TEMP'].values[i],
                    'salinity_psu': ds['PSAL'].values[i]
                }
                
                # BGC CHANGE: Dynamically check for and add BGC variables
                if 'DOXY' in ds:
                    measurements_data['doxy_umol_kg'] = ds['DOXY'].values[i]
                if 'CHLA' in ds:
                    measurements_data['chla_mg_m3'] = ds['CHLA'].values[i]
                if 'NITRATE' in ds:
                    measurements_data['nitrate_umol_kg'] = ds['NITRATE'].values[i]

                measurements_df = pd.DataFrame(measurements_data)
                
                # BGC CHANGE: Update the subset for dropping empty rows
                all_measurement_cols = [
                    'pressure_dbar', 'temperature_celsius', 'salinity_psu',
                    'doxy_umol_kg', 'chla_mg_m3', 'nitrate_umol_kg'
                ]
                # Keep only the columns that actually exist in the DataFrame
                existing_cols = [col for col in all_measurement_cols if col in measurements_df.columns]
                measurements_df.dropna(how='all', subset=existing_cols, inplace=True)

                if not measurements_df.empty:
                    measurements_df.to_sql('measurements', engine, if_exists='append', index=False)
            
            except IntegrityError:
                print(f"  - Skipping duplicate profile for timestamp {full_timestamp}.")
                continue
            except Exception as e:
                print(f"An error occurred on profile {i}: {e}")
                continue
    
    print("Data ingestion complete.")

if __name__ == "__main__":
    # IMPORTANT: You must use a .nc file from a BGC float to test this
    NC_FILE = '20250102_prof.nc' 
    DB_URL = "postgresql://postgres:123456@localhost:5432/Aquaman"
    ingest_argo_file(NC_FILE, DB_URL)