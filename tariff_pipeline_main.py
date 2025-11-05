import os
import sys

# Add the script's directory to Python path to ensure imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from Reach_EnergiDataService import fetch_datahub_pricelist
from categorize_tariffs import enhanced_categorize_tariff_data

# ============================================================
# CONFIGURATION - Change these settings as needed
# ============================================================

START_DATE = '2021-01-01'  # Start date (YYYY-MM-DD)
END_DATE = '2024-12-31'    # End date (YYYY-MM-DD)
USE_CACHED = False          # Set to False to force fresh download from API

RAW_DATA_FILENAME = 'Tarif_data_2021_2024'           # Base filename for raw data
OUTPUT_FILENAME = 'tariff_categorization_results.xlsx'  # Final Excel output

# ============================================================


def main():
    """
    Complete pipeline to fetch and categorize tariff data.
    """
    print("="*70)
    print("TARIFF DATA PROCESSING PIPELINE")
    print("="*70)
    print(f"Start Date: {START_DATE}")
    print(f"End Date: {END_DATE}")
    print(f"Use Cached Data: {USE_CACHED}")
    print("="*70)
    
    # STEP 1: Fetch data from API
    print("\n[STEP 1/2] Fetching tariff data from API...")
    print("-"*70)
    
    df, data_dir = fetch_datahub_pricelist(
        start_date=START_DATE,
        end_date=END_DATE,
        parquet_path=f'{RAW_DATA_FILENAME}.parquet',
        use_cached=USE_CACHED
    )
    
    if df is None:
        print("❌ Failed to fetch data. Pipeline aborted.")
        return
    
    print(f"✅ Data fetched successfully!")
    print(f"   Records: {len(df)}")
    
    # STEP 2: Categorize data
    print(f"\n[STEP 2/2] Categorizing tariff data...")
    print("-"*70)
    
    csv_path = os.path.join(data_dir, f'{RAW_DATA_FILENAME}.csv')
    
    result = enhanced_categorize_tariff_data(
        file_path=csv_path,
        output_filename=OUTPUT_FILENAME,
        use_data_folder=True
    )
    
    if 'error' in result:
        print(f"❌ Categorization failed: {result['error']}")
        return
    
    # Summary
    print("\n" + "="*70)
    print("PIPELINE COMPLETED SUCCESSFULLY! 🎉")
    print("="*70)
    
    df_categorized = result['df']
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Total rows processed: {len(df_categorized)}")
    print(f"   Output file: {result['output_path']}")
    
    print(f"\n📈 CATEGORIZATION SUMMARY:")
    print(f"   Kundetype categories: {df_categorized['Kundetype'].nunique()}")
    print(f"   Tariftype categories: {df_categorized['Tariftype'].nunique()}")
    
    uncategorized_both = len(df_categorized[
        (df_categorized['Kundetype'] == 'Uncategorized') & 
        (df_categorized['Tariftype'] == 'Uncategorized')
    ])
    print(f"   Fully uncategorized: {uncategorized_both} ({(uncategorized_both/len(df_categorized)*100):.2f}%)")
    
    print(f"\n📁 FILES CREATED:")
    print(f"   Raw data (CSV): {csv_path}")
    print(f"   Raw data (Parquet): {csv_path.replace('.csv', '.parquet')}")
    print(f"   Categorized results: {result['output_path']}")
    
    print("\n" + "="*70)
    print("✅ All done! Check the Data folder for your results.")


if __name__ == "__main__":
    main()