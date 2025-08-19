import pandas as pd
import geopandas as gpd  
import logging
from pathlib import Path
from datetime import datetime 
import os
import numpy as np


def setup_logging(directory):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    log_file = directory / f'log_{timestamp}.txt'

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_file,
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info('Logging has been configured.')

def read_gpd(filepath):
    if filepath.endswith('.shp'):
        try:
            gdf = gpd.read_file(filepath)
            logging.info(f'Shapefile loaded successfully: {filepath}')
            return gdf
        except Exception as e:
            logging.error(f'Error reading shapefile: {filepath} — {e}')
            raise
    else:
        logging.error(f'Invalid file extension: {filepath}')
        raise ValueError('Please enter a valid .shp file.')
    
def clean_data(filepath, export_path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)

    if filepath.endswith('.csv'):
        data = pd.read_csv(filepath, encoding='latin-1', low_memory=False)
        logging.info('CSV file detected and loaded.')
    elif filepath.endswith('.xlsx'):
        data = pd.read_excel(filepath)
        logging.info('Excel file detected and loaded.')
    else:
        logging.error('Invalid file extension: %s', filepath)
        raise ValueError('Please enter a valid file extension.')

    # Standardize column names
    # Clean and normalize column names
    data.columns = (
        data.columns
        .str.lower()
        .str.strip()
        .str.replace(' ', '_')
        .str.replace('²', 'm2')           # replace superscript 2
        .str.replace('â', '')             # remove stray encoding artifacts
        .str.replace(r'[^\w_]', '', regex=True)  # remove other non-word characters
    )

    try:
        # ---- numeric fields with dash placeholders ----
        # bed/bath/car: fill missing with 0 then cast
        for col in ['bed', 'bath', 'car',]:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)

        # postcode: coerce then decide how to fill (0 here)
        data['postcode'] = pd.to_numeric(data['postcode'], errors='coerce').fillna(0).astype(int)

        # sale_price: strip currency/commas/spaces, treat '-' as missing
        price = (
            data['sale_price'].astype(str)
            .str.replace(r'[\$, ]', '', regex=True)
            .replace('-', pd.NA)
        )
        price = pd.to_numeric(price, errors='coerce')
        data['sale_price'] = price.fillna(price.mean()).astype(int)

        # dates
        data['sale_date'] = pd.to_datetime(
            data['sale_date'], errors='coerce')
        
        data['settlement_date'] = pd.to_datetime(data['settlement_date'],errors='coerce')

        data_rename = {'land_size_(mÂ²)' : 'land_size_meters', 'floor_size_(mÂ²)' : 'floor_size_meters'}
        data.rename(columns=data_rename,inplace=True)

        # Convert to string, clean symbols, convert to numeric, then fill NaNs
        for col in ['land_size_mm2', 'floor_size_mm2']:
            cleaned = (
                data[col].astype(str)
                .str.replace(',', '', regex=False)
                .str.replace('-', '', regex=False)
            )
            data[col] = pd.to_numeric(cleaned, errors='coerce').fillna(0).astype(int)

        data['land_use'] = data['land_use'].replace('-', 'Unknown').fillna('Unknown')
        data['development_zone'] = data['development_zone'].replace('-', 'Unknown').fillna('Unknown')
        data['parcel_details'] = data['parcel_details'].astype(str).str.strip()
        
        data['lotplan'] = data['parcel_details'].astype(str).apply(lambda x: x.split(',')[0].strip().replace('/', ''))
        data['lotplan'] = data['lotplan'].replace(['-',''], np.nan)
        
        #THIS IS NOT WORKING
        #data['lotplan'] = data['lotplan'].str.extract(r'LOT\s*(\d+\s*\w+)', expand=False)
        #data['lotplan'] = data['lotplan'].str.replace(' ','', regex=False)

        data = data.dropna(subset=['lotplan'])
        data = data.drop_duplicates(subset=['lotplan'], keep='last')

        logging.info('Data cleaning and type conversion successful.')
    except Exception as e:
        logging.error('Error during data cleaning: %s', e)
        raise

    out_path = export_dir / f'cleaned_data_{timestamp}.csv'
    data.to_csv(out_path, index=False)
    logging.info('Cleaned data exported to %s', out_path)

    return data

def export_lotplan(shp_filepath, csv_path, export_path):
    # Validate shapefile
    if not shp_filepath.endswith('.shp'):
        logging.error('Invalid shapefile extension.')
        print('Please enter a valid shapefile path.')
        return

    # Validate CSV
    if not csv_path.endswith('.csv'):
        logging.error('Invalid CSV file extension.')
        print('Please enter a valid CSV file path.')
        return

    # Read shapefile
    gdf = gpd.read_file(shp_filepath)
    gdf = gdf.to_crs(epsg=4326)
    logging.info(f'Shapefile loaded: {shp_filepath}')

    gdf = gdf.dropna(subset=['lotplan'])
    logging.info('Dropping null values in lotplan.')

    # Read CSV
    data = pd.read_csv(csv_path, encoding='latin-1', low_memory=False)
    logging.info(f'CSV loaded: {csv_path}')

    # Merge
    merged = gdf.merge(data, left_on= 'lotplan', right_on='lotplan', how='right')
    logging.info('Merge completed.')

    merged_centroid = merged.copy()
    merged_centroid['geometry'] = merged_centroid.centroid
    logging.info('Creating centroid.')

    merged_centroid = merged_centroid.to_crs(epsg=4326)

    # Safe filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exported_shapefile_{timestamp}.shp'
    centroid_filename = f'exported_shapefile_centroid_{timestamp}.shp'

    # Export
    output_path = os.path.join(export_path, filename)
    merged.to_file(output_path)
    merged_centroid.to_file(os.path.join(export_path,centroid_filename))
    logging.info(f'Shapefile exported to: {output_path}')
