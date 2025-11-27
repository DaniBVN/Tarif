import os
import requests
import polars as pl
from datetime import datetime
from typing import Optional

def fetch_datahub_pricelist(
    start_date: str = '2021-01-01', 
    end_date: str = '2025-12-31', 
    parquet_path: Optional[str] = None, 
    use_cached: bool = True
):
    """
    Fetch DatahubPricelist from Energi Dataservice API or load from parquet file.
    
    Args:
        start_date (str): Start date for data extraction (YYYY-MM-DD)
        end_date (str): End date for data extraction (YYYY-MM-DD)
        parquet_path (str, optional): Custom path for parquet file. 
                                      If None, uses default 'datahub_pricelist.parquet' in Data folder
        use_cached (bool): Whether to use existing parquet file if available
    
    Returns:
        tuple: (Polars DataFrame with price data, directory path of the parquet file)
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create path to Data folder (parallel to script folder)
    data_dir = os.path.join(os.path.dirname(script_dir), 'Data')
    
    # Determine parquet file path
    if parquet_path is None:
        parquet_path = os.path.join(data_dir, 'datahub_pricelist.parquet')
    else:
        # If custom path provided, ensure it's in the Data folder
        filename = os.path.basename(parquet_path)
        parquet_path = os.path.join(data_dir, filename)
    
    # Ensure Data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Check if cached parquet file exists and use_cached is True
    if use_cached and os.path.exists(parquet_path):
        print(f"Loading data from existing parquet file: {parquet_path}")
        try:
            return pl.read_parquet(parquet_path), data_dir
        except Exception as e:
            print(f"Error reading parquet file: {e}")
            print("Falling back to API fetch...")
    
    # Base URL for the API
    base_url = 'https://api.energidataservice.dk/dataset/DatahubPricelist'
    
    # Prepare query parameters
    params = {
        'start': start_date,
        'end': end_date,
        'limit': 1000000000  # Increase limit to get more records
    }
    
    try:
        # Send GET request to the API
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        
        # Parse JSON response
        result = response.json()
        
        # Extract records
        records = result.get('records', [])
        
        if not records:
            print("No records found in the specified date range.")
            return None, None
        
        # Convert records to Polars DataFrame
        df = pl.DataFrame(records)
        
        # Optional: Convert date column to datetime if needed
        if 'date' in df.columns:
            df = df.with_columns(pl.col('date').str.to_datetime())
        
        # Save to parquet for future use
        df.write_parquet(parquet_path)
        
        # Create CSV path in the same Data directory
        csv_path = parquet_path.replace('.parquet', '.csv')
        df.write_csv(csv_path)
        
        print(f"Data saved to parquet file: {parquet_path}")
        print(f"Data saved to CSV file: {csv_path}")
        
        return df, data_dir
    
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def main():
    # Fetch the data - now the file will be saved in the Data folder
    df, save_dir = fetch_datahub_pricelist(
        start_date='2021-01-01', 
        end_date='2024-12-31',
        parquet_path='Tarif_data_2021_2024.parquet'  # Just filename, will be placed in Data folder
    )
    
    if df is not None:
        pd_df = df.to_pandas()
        print(f"Data successfully loaded. Shape: {pd_df.shape}")
        print(f"Files saved in directory: {save_dir}")
    else:
        print("Failed to load data.")

if __name__ == '__main__':
    main()