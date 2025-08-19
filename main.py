import logging
from pathlib import Path
from read_file import setup_logging, read_gpd, clean_data, export_lotplan
import numpy as np

# Setup logging
log_dir = Path('.logs')
setup_logging(log_dir)

# File paths
shp_file = r'files\shapefile\Cadastral_data_QLD_CADASTRE_DCDB.shp'
csv_file = 'files/dataset/Sunshine Coast Merged.csv'
export_file = Path(r'files\export')
export_file.mkdir(parents=True, exist_ok=True)

clean_csv_file = r'files\export\cleaned_data_20250819_173943.csv'
export_shpfile = r'files\merged_shapefile'

# User choice menu
choices = {
    1: 'Extract File',
    2: 'Extract Shapefile and Centroid',
    3: 'Exit'
}

print('\nPLEASE ENTER WHAT YOU WANT TO PROCESS:')
for key, val in choices.items():
    print(f"{key}: {val}")

try:
    choice = int(input("Enter choice: "))
    
    if choice == 1:
        logging.info("Starting file cleaning...")
        clean_data(csv_file, export_file)
        logging.info("Cleaning complete.")
    
    elif choice == 2:
        logging.info("Starting shapefile + centroid export...")
        export_lotplan(shp_file, clean_csv_file, export_shpfile)
        logging.info("Export complete.")
    
    elif choice == 3:
        print("Exiting...")

    else:
        print("Invalid choice.")

except ValueError:
    print("Please enter a valid number.")
