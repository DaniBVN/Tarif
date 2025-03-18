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
                                      If None, uses default 'datahub_pricelist.parquet'
        use_cached (bool): Whether to use existing parquet file if available
    
    Returns:
        tuple: (Polars DataFrame with price data, directory path of the parquet file)
    """
    # Determine parquet file path
    if parquet_path is None:
        parquet_path = 'datahub_pricelist.parquet'
    
    # Ensure absolute path and directory exists
    parquet_path = os.path.abspath(parquet_path)
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    
    # Check if cached parquet file exists and use_cached is True
    if use_cached and os.path.exists(parquet_path):
        print(f"Loading data from existing parquet file: {parquet_path}")
        try:
            return pl.read_parquet(parquet_path), os.path.dirname(parquet_path)
        except Exception as e:
            print(f"Error reading parquet file: {e}")
            print("Falling back to API fetch...")
    
    # Base URL for the API
    base_url = 'https://api.energidataservice.dk/dataset/DatahubPricelist'
    
    # Prepare query parameters
    params = {
        'start': start_date,
        'end': end_date,
        'limit': 10000  # Increase limit to get more records
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
        print(f"Data saved to parquet file: {parquet_path}")
        
        return df, os.path.dirname(parquet_path)
    
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def analyze_notes_by_chargeowner(df):
    """
    Analyze unique Notes for each ChargeOwner.
    
    Args:
        df (pl.DataFrame): Input DataFrame
    
    Returns:
        pl.DataFrame: Analysis of Notes by ChargeOwner
    """
    # Check if required columns exist
    if 'ChargeOwner' not in df.columns or 'Note' not in df.columns:
        print("Required columns 'ChargeOwner' or 'Note' not found.")
        return None
    
    # Group by ChargeOwner and Note, count occurrences
    notes_by_chargeowner = (
        df.group_by(['ChargeOwner', 'Note'])
          .agg(pl.len().alias('count'))
          .sort(['ChargeOwner', 'count'], descending=[False, True])
    )
    
    # Optional: Get total notes per ChargeOwner for context
    total_notes_per_chargeowner = (
        df.group_by('ChargeOwner')
          .agg(pl.len().alias('total_records'))
          .sort('total_records', descending=True)
    )
    
    # Combine the analyses
    print("\nNotes Analysis by ChargeOwner:")
    
    # Iterate through unique ChargeOwners
    chargeowners = notes_by_chargeowner['ChargeOwner'].unique()
    
    for owner in chargeowners:
        # Filter notes for this ChargeOwner
        owner_notes = notes_by_chargeowner.filter(pl.col('ChargeOwner') == owner)
        
        # Get total records for this ChargeOwner
        total_records = total_notes_per_chargeowner.filter(pl.col('ChargeOwner') == owner)['total_records'][0]
        
        print(f"\n--- {owner} (Total Records: {total_records}) ---")
        print(owner_notes)
    
    return notes_by_chargeowner

def main():
    # Fetch the data
    df, save_dir = fetch_datahub_pricelist(
        start_date='2021-01-01', 
        end_date='2023-12-31',
        parquet_path='C:/Users/DNI/OneDrive - Green Power Denmark/Dokumenter/GitHub/Tarif/energy_data_2021_2025.parquet'
    )
    pd_df = df.to_pandas()
    if df is not None and save_dir is not None:
        # Analyze Notes by ChargeOwner
        notes_analysis = analyze_notes_by_chargeowner(df)
        
        # Optionally save the analysis to a CSV
        if notes_analysis is not None:
            notes_csv_path = os.path.join(save_dir, 'notes_by_chargeowner.csv')
            notes_analysis.write_csv(notes_csv_path)
            print(f"\nNotes analysis saved to {notes_csv_path}")

if __name__ == '__main__':
    main()
