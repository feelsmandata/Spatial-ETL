# Spatial-ETL

Spatial-ETL is a Python project designed for **Extract, Transform, and Load (ETL)** operations on spatial datasets.  
It provides tools to read, clean, and process geospatial data (such as shapefiles), making it easier to integrate into analytical workflows or GIS applications.  

## Features
- Read and process shapefiles and geospatial data  
- Clean and transform raw spatial datasets  
- Export results into structured formats (e.g., CSV)  
- Modular design for easy extension and automation  

## Project Structure
files/ # Raw and processed data
main.py # Main entry point
read_file.py # Utilities for reading shapefiles
.logs/ # Logs for debugging and tracking runs


## Getting Started
1. Clone this repository:
   ```bash
   git clone https://github.com/feelsmandata/Spatial-ETL.git
   cd Spatial-ETL
   
2. Create and activate a virtual environment:
  python -m venv .venv
  source .venv/bin/activate  # Linux/Mac
  .venv\Scripts\activate     # Windows

3. Install dependencies:
  pip install -r requirements.txt

4. Run the project:
   python main.py
