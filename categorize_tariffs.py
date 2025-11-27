import pandas as pd
import polars as pl
import os
import numpy as np

# Import configuration
from categorization_config import (
    kundetype_patterns,
    pris_element_patterns,
    bruger_patterns,
    net_patterns,
    Rabat_patterns,
    kundetype_priority,
    pris_element_priority,
    bruger_priority,
    net_priority,
    Rabat_priority,
    OUTPUT_COLUMN_ORDER,
    DEFAULT_OUTPUT_FILENAME,
    use_temp_file
)

# ============================================
# DIRECTORY HELPERS
# ============================================

def get_data_directory():
    """Get Data directory parallel to script directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(script_dir), 'Data')

# ============================================
# CATEGORIZATION FUNCTIONS
# ============================================

def find_category(row, category_patterns, COLUMN_PRIORITY_ORDER,fallback):
    """
    Cascading filter with match counting: Categories compete based on number of pattern matches.
    
    Rules:
    1. If column is empty/missing in data → skip to next column (don't check patterns)
    2. If column has data AND category has empty pattern list [] → category abstains (stays)
    3. If column has data AND category has patterns:
       - Pattern matches → keep category and increment match count
       - Pattern doesn't match → eliminate category
    4. Winner is determined by highest match count
    
    Args:
        row: DataFrame row to categorize
        category_patterns: {category: {column: [patterns]}}
        COLUMN_PRIORITY_ORDER: List of columns to check in order
    
    Returns:
        Category name or string of matching patterns
    """

    candidates = list(category_patterns.keys())
    match_counts = {cat: 0 for cat in candidates}  # Track matches per category
    matching_patterns = []
    
    for c, column in enumerate(COLUMN_PRIORITY_ORDER):

        # Skip if column doesn't exist, is NaN, or is empty string
        if column not in row or pd.isna(row[column]) or str(row[column]).strip() == '':
            continue
        
        text = str(row[column]).lower()
        update_candidates = []
        
        # Loops through all candidates
        candidate_matches = False # If there are no candidates matches then do not update the candidates
        for category in candidates:

            # Get patterns for this category and column
            if column not in category_patterns[category]:
                update_candidates.append(category)
                continue
            
            patterns = category_patterns[category][column]
            
            if not patterns:  # Empty list [] - category abstains
                update_candidates.append(category)
                continue
            
            # Category has patterns - check ALL matches and count them
            has_match = False
            for pattern in patterns:
                if pattern.lower() in text:
                    match_counts[category] += 1
                    matching_patterns.append(pattern.lower())
                    has_match = True
                    
                    # DON'T break - count all matches
            
            # Only keep category if it had at least one match
            if has_match:
                update_candidates.append(category)
                candidate_matches = True # 
        
        
        # Select only the candidates which were there from the column
        if candidate_matches: # Only if there are matches you should do
            candidates = update_candidates
        
        
        # If there is only one candidate and there was a match, terminate early
        if len(candidates) == 1 and candidate_matches:
            return candidates[0]
    

    # If there have been no matches, then go to fallback or say that there are no matches
    if len(matching_patterns) == 0: 
        if fallback == None:
            return "Uncategorized - No matches"
        else:
            return fallback
            

    # If there is just one candidate
    elif len(candidates) == 1:
        return candidates[0]
    
    # If there are multiple candidates - select the one with most matches
    else:
        # Get match counts only for remaining candidates
        candidate_counts = {cat: match_counts[cat] for cat in candidates}
        
        # Find max count
        max_count = max(candidate_counts.values())
        
        # Get all categories with max count
        winners = [cat for cat, count in candidate_counts.items() if count == max_count]
        
        if len(winners) == 1:
            return winners[0]
        else:
            if matching_patterns:
                # Tie between multiple categories
                return f"Uncategorized - Tie between: {', '.join(winners)} (Matches: {', '.join(matching_patterns)})"
            else:
                return "Uncategorized - No matches"

# ============================================
# MAIN FUNCTION
# ============================================

def load_raw_tarif_data(input_file, output_dir):
    """
    Main categorization function

    Args:
        input_file: Path to input Parquet file
        output_dir: Output directory (default from config)
    """

    # Read data
    print(f"Reading: {input_file}")
    df = pl.read_parquet(input_file)
    print(f"Loaded {len(df)} rows")
    
    # Convert date columns to datetime and format them immediately
    df = df.with_columns([
        pl.col("ValidFrom").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ValidFrom"),
        pl.when(pl.col("ValidTo").is_not_null())
        .then((pl.col("ValidTo").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f") - pl.duration(hours=1)).dt.strftime("%Y-%m-%d %H:%M:%S"))
        .otherwise(pl.col("ValidTo"))
        .alias("ValidTo")
    ])
    
    # Sort by ValidFrom to ensure chronological order
    df = df.sort("ValidFrom")
    
    # Identify all columns
    date_cols = ['ValidFrom', 'ValidTo']
    price_cols = [col for col in df.columns if col.lower().startswith('price')]
    
    # Non-price, non-date columns (these define the groups)
    id_cols = [col for col in df.columns if col not in date_cols and col not in price_cols]
    
    # Group by ID columns and process
    result_rows = []
    
    for group_keys, group_df in df.group_by(id_cols, maintain_order=True):
        group_df = group_df.sort("ValidFrom")
        group_data = group_df.to_dicts()
        
        i = 0
        while i < len(group_data):
            # Start a new period
            current_row = group_data[i].copy()
            current_prices = [current_row[col] for col in price_cols]
            period_start = current_row['ValidFrom']
            period_end = current_row['ValidTo']
            
            # Look ahead to find consecutive rows with same prices
            j = i + 1
            while j < len(group_data):
                next_row = group_data[j]
                next_prices = [next_row[col] for col in price_cols]
                
                # Check if all prices are the same
                if current_prices == next_prices:
                    # Extend the period
                    period_end = max(period_end, next_row['ValidTo']) if next_row['ValidTo'] else period_end
                    j += 1
                else:
                    # Prices changed, stop extending
                    break
            
            # Create result row with extended date range
            result_row = current_row.copy()
            result_row['ValidFrom'] = period_start
            result_row['ValidTo'] = period_end
            result_rows.append(result_row)
            
            # Move to next distinct price period
            i = j
    
    # Create result dataframe
    df_result = pl.DataFrame(result_rows)
    
    # Restore original column order
    df_result = df_result.select(df.columns)

    temp_path = os.path.join(output_dir, 'temp.csv')
    df_result.write_csv(temp_path)

    print(f"After deduplication: {len(df_result)} rows (was {len(df)} rows)")

    return df_result


def categorize_tariff_data(df):
    """
    Main categorization function
    
    Args:
        input_file: Path to input CSV file
        output_file: Output filename (default from config)
        use_data_folder: If True, save to Data folder; if False, save to same dir as input
    """
    
    
    # Categorize
    print("Categorizing...")
    df['KundeType'] = df.apply(lambda row: find_category(row, kundetype_patterns,kundetype_priority,None), axis=1)
    df['PrisElement'] = df.apply(lambda row: find_category(row, pris_element_patterns,pris_element_priority,None), axis=1)
    df['OverliggendeNet'] = df.apply(lambda row: find_category(row, net_patterns,net_priority,"Eget net"), axis=1)
    df['Rabat'] = df.apply(lambda row: find_category(row, Rabat_patterns,Rabat_priority,"Normal"), axis=1)
    df['Bruger'] = df.apply(lambda row: find_category(row, bruger_patterns,bruger_priority,"Forbrug"), axis=1)

    # Reorder columns
    priority_cols = [col for col in OUTPUT_COLUMN_ORDER if col in df.columns]
    other_cols = [col for col in df.columns if col not in priority_cols]
    df = df[priority_cols + other_cols]
    
    # Statistics
    print(f"\nResults:")
    print(f"  KundeType: {df['KundeType'].value_counts().to_dict()}")
    print(f"  PrisElement: {df['PrisElement'].value_counts().to_dict()}")
    print(f"  OverliggendeNet: {df['OverliggendeNet'].value_counts().to_dict()}")  
    print(f"  Rabat: {df['Rabat'].value_counts().to_dict()}")  
    print(f"  Bruger: {df['Bruger'].value_counts().to_dict()}")
    
    
    return df

def merge_only_overlapping_periods(df_pl,COLUMNS,col_groupby):
        """
        Merge ONLY overlapping or consecutive periods with identical prices.
        Does NOT bridge gaps - respects discontinuities in the data.
        """
        
        #col_groupby = ['KundeType', 'PrisElement', 'ChargeOwner','Bruger']
        price_cols = [f'Price{i}' for i in range(1, 25)]
        
        # Parse dates if needed (adjust format as needed)
        df_pl = df_pl.with_columns([
            pl.col('ValidFrom').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S"),
            pl.col('ValidTo').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
        ])
        
        # Sort: ValidFrom ascending, ValidTo descending
        df_sorted = df_pl.sort(
            col_groupby + price_cols + ['ValidFrom', 'ValidTo'],
            descending=[False] * (len(col_groupby) + len(price_cols)) + [False, True]
        )
        
        # Within each group (same prices and attributes), check if current period overlaps with previous
        df_sorted = df_sorted.with_columns([
            # Get previous row's ValidTo within the same price group
            pl.col('ValidTo').shift(1).over(col_groupby + price_cols).alias('prev_ValidTo'),
            pl.col('ValidFrom').alias('curr_ValidFrom')
        ])
        
        # Mark start of NEW non-overlapping period:
        # - First row in group (prev_ValidTo is null)
        # - OR there's a gap (current start > previous end)
        df_sorted = df_sorted.with_columns([
            pl.when(
                pl.col('prev_ValidTo').is_null() |  # First row
                (pl.col('curr_ValidFrom') > pl.col('prev_ValidTo'))  # Gap exists
            )
            .then(1)
            .otherwise(0)
            .alias('is_new_period')
        ])
        
        # Create period_id by cumulative sum - this groups consecutive overlapping rows
        df_sorted = df_sorted.with_columns([
            pl.col('is_new_period')
            .cum_sum()
            .over(col_groupby + price_cols)
            .alias('period_id')
        ])
        
        # Now aggregate by period_id - each period_id represents one merged group
        result = (
            df_sorted
            .group_by(col_groupby + price_cols + ['period_id'])
            .agg([
                pl.col('ValidFrom').min().alias('ValidFrom'),  # Earliest start in this continuous period
                pl.col('ValidTo').max().alias('ValidTo'),      # Latest end in this continuous period
                pl.len().alias('merged_count')  # Optional: see how many rows were merged
            ])
            .drop('period_id')
            .sort(col_groupby + ['ValidFrom'])
        )

        result = result.select(COLUMNS)
        
        return result


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Standalone execution"""

    #row = pd.DataFrame({'Note':['Nettarif B lav produktion time'],'Description':['Tarif, egenproduktion (time)']})
    #find_category(row.iloc[0], kundetype_patterns,kundetype_priority)

    data_dir = get_data_directory()
    input_file = os.path.join(data_dir, 'Tarif_data_2021_Maj2025.parquet')
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    
    use_data_folder=True

    # Determine output directory
    if use_data_folder:
        output_dir = get_data_directory()
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(input_file)

    output_file=DEFAULT_OUTPUT_FILENAME
    if output_file is None:
        output_file = DEFAULT_OUTPUT_FILENAME

    output_path = os.path.join(output_dir, output_file)

    if use_temp_file:
        temp_file_path = os.path.join(output_dir,'temp.csv')
        df = pd.read_csv(temp_file_path)
    else:
        df = load_raw_tarif_data(
            input_file=input_file,
            output_dir=output_dir)
    
    df = df.to_pandas()
    df = categorize_tariff_data(df)

    # Save
    print(f"\nSaving to: {output_path}")
    df.to_excel(output_path, sheet_name='Categorized Data', index=False)
    
    

    ''' New processing, where costumers which have been categorized in Costumer and price element are then grouped such that there are no duplicates'''

    # For each Kundetype, PrisElement, ChargeOwner, ValidFrom, ValidTo
        # Remove duplicates
    # Check if Price1 to Price24 are the same. If so remove the duplicate

    df_pl = pl.from_pandas(df)
    

    COLUMNS = [
    'KundeType',
    'PrisElement',
    'Bruger',
    'ChargeOwner',
    'OverliggendeNet',
    'Rabat',
    'ValidFrom',
    'ValidTo',
    'Price1','Price2','Price3','Price4','Price5',
    'Price6','Price7','Price8','Price9','Price10',
    'Price11','Price12','Price13','Price14','Price15',
    'Price16','Price17','Price18','Price19','Price20',
    'Price21','Price22','Price23','Price24'
    ]

    col_groupby = ['KundeType', 'PrisElement', 'ChargeOwner','OverliggendeNet','Rabat','Bruger']

    # Use it
    df_merged = merge_only_overlapping_periods(df_pl,COLUMNS,col_groupby)
    print(f"Original rows: {len(df_pl)}")
    print(f"After merging overlaps: {len(df_merged)}")

    # Convert back to pandas if needed
    df = df_merged.to_pandas()

    print(df.head())
    print(f"\nShape: {df.shape}")
    output_path = os.path.join(output_dir, 'cleaned.xlsx')
    df.to_excel(output_path, sheet_name='Data', index=False)


if __name__ == "__main__":
    main()