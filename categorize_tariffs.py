import pandas as pd
import polars as pl
import os

# Import configuration
from categorization_config import (
    kundetype_patterns,
    tariftype_patterns,
    chargetype_mapping,
    kundetype_priority,
    tariftype_priority,
    OUTPUT_COLUMN_ORDER,
    GRID_MAPPING_FILENAME,
    DEFAULT_OUTPUT_FILENAME
)

# ============================================
# DIRECTORY HELPERS
# ============================================

def get_data_directory():
    """Get Data directory parallel to script directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(script_dir), 'Data')

# ============================================
# GRID COMPANY MAPPING
# ============================================

def load_grid_mapping():
    """Load grid company mapping file"""
    data_dir = get_data_directory()
    mapping_file = os.path.join(data_dir, GRID_MAPPING_FILENAME)
    
    if not os.path.exists(mapping_file):
        print(f"⚠️  Grid mapping file not found: {GRID_MAPPING_FILENAME}")
        return None
    
    df_mapping = pd.read_excel(mapping_file)
    mapping = {}
    for _, row in df_mapping.iterrows():
        company_name = str(row['GRID_COMPANY_NAME']).strip()
        if company_name not in mapping:
            mapping[company_name] = {
                'MPO_GRID_AREA_CODE': row['MPO_GRID_AREA_CODE'],
                'PriceArea': row['PriceArea']
            }
    print(f"✅ Loaded {len(mapping)} grid companies")
    return mapping

def map_grid_codes(df, grid_mapping):
    """Map ChargeOwner to MPO_GRID_AREA_CODE and PriceArea"""
    if grid_mapping is None or 'ChargeOwner' not in df.columns:
        return df
    
    df['MPO_GRID_AREA_CODE'] = None
    df['PriceArea'] = None
    
    for idx, row in df.iterrows():
        if pd.notna(row.get('ChargeOwner')):
            owner = str(row['ChargeOwner']).strip()
            if owner in grid_mapping:
                df.at[idx, 'MPO_GRID_AREA_CODE'] = grid_mapping[owner]['MPO_GRID_AREA_CODE']
                df.at[idx, 'PriceArea'] = grid_mapping[owner]['PriceArea']
    
    return df

# ============================================
# CATEGORIZATION FUNCTIONS
# ============================================

def categorize_chargetype(charge_type):
    """Map D01/D02/D03 to category"""
    if pd.notna(charge_type):
        return chargetype_mapping.get(str(charge_type).strip().upper(), 'Unknown')
    return 'Unknown'

def find_category2(row, category_patterns):
    """
    Find which category a row belongs to using cascading filter approach.
    
    Algorithm:
    1. Start with all possible categories
    2. Check ChargeType - keep only categories that match (or have no patterns)
    3. If multiple remain, check ChargeTypeCode - narrow down further
    4. If multiple remain, check Note - narrow down further
    5. If multiple remain, check Description - narrow down further
    6. If exactly one category remains, return it. Otherwise "Uncategorized"
    
    Args:
        row: DataFrame row to categorize
        category_patterns: Dictionary with structure {category: {column: [patterns]}}
    
    Returns:
        Category name or "Uncategorized"
    """
    # Get column priority order from config
    column_priority = COLUMN_PRIORITY_ORDER
    
    # Start with all categories as candidates
    candidate_categories = list(category_patterns.keys())
    
    # Process each column in priority order
    for column in column_priority:
        # Skip if column doesn't exist in row or is empty
        if column not in row or pd.notna(row[column]) is False:
            continue
        
        text_lower = str(row[column]).lower()
        
        # Find which candidates match at this priority level
        matching_categories = []
        categories_with_patterns = []
        
        for category in candidate_categories:
            # Check if this category has patterns for this column
            if column not in category_patterns[category]:
                continue
            
            patterns = category_patterns[category][column]
            
            # If category has no patterns for this column, keep it as candidate
            if not patterns:
                continue
            
            # This category has patterns for this column
            categories_with_patterns.append(category)
            
            # Check if any pattern matches
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    matching_categories.append(category)
                    break  # Found a match, no need to check other patterns
        
        # If some categories had patterns for this column, filter based on matches
        if categories_with_patterns:
            if matching_categories:
                # Narrow down to only matching categories
                candidate_categories = matching_categories
            else:
                # No matches found, but some had patterns - these are eliminated
                # Keep only categories that didn't have patterns for this column
                candidate_categories = [c for c in candidate_categories if c not in categories_with_patterns]
        
        # If we're down to one candidate, we're done
        if len(candidate_categories) == 1:
            return candidate_categories[0]
        
        # If we're down to zero candidates, return uncategorized
        if len(candidate_categories) == 0:
            return "Uncategorized"
    
    # After checking all columns:
    # - If exactly one category remains, return it
    # - If multiple remain, it's ambiguous -> Uncategorized
    # - If none remain, return Uncategorized
    if len(candidate_categories) == 1:
        return candidate_categories[0]
    else:
        return "Uncategorized"

def find_category(row, category_patterns,COLUMN_PRIORITY_ORDER):
    """
    Cascading filter: Start with all categories, narrow down at each priority level.
    
    Rules:
    1. If column is empty/missing in data → skip to next column (don't check patterns)
    2. If column has data AND category has empty pattern list [] → category abstains (stays)
    3. If column has data AND category has patterns:
       - Pattern matches → keep category
       - Pattern doesn't match → eliminate category
    
    Args:
        row: DataFrame row to categorize
        category_patterns: {category: {column: [patterns]}}
    
    Returns:
        Category name or "Uncategorized"
    """
    candidates = list(category_patterns.keys())
    #print()
    #print(row[COLUMN_PRIORITY_ORDER])
    #print(candidates)
    #print(COLUMN_PRIORITY_ORDER)
    for c, column in enumerate(COLUMN_PRIORITY_ORDER):
        # Skip if column doesn't exist, is NaN, or is empty string
        if column not in row or pd.isna(row[column]) or str(row[column]).strip() == '':
            continue
        
        text = str(row[column]).lower()
        new_candidates = []
        
        for category in candidates:

            # Get patterns for this category and column
            if column not in category_patterns[category]:
                new_candidates.append(category)
                continue
            
            patterns = category_patterns[category][column]
            
            if not patterns:  # Empty list [] - category abstains
                new_candidates.append(category)
                continue
            
            # Category has patterns - check if any match
            for pattern in patterns:
                if pattern.lower() in text:
                    new_candidates.append(category)
                    break
        # After
        #if len(new_candidates) == 1:
         #   break

        candidates = new_candidates
        
        # Early termination
        if len(candidates) == 0:
            type = "Uncategorized"
            #print(type)
            return type
        if len(candidates) == 1:
            type = candidates[0]
            #print(type)
            return type
        

    c = len(COLUMN_PRIORITY_ORDER)
    # After all columns
    if len(candidates) == 0:
        type = "Uncategorized"
        #print(type)
        return type
    if len(candidates) == 1:
        type = candidates[0]
        #print(type)
        return type

# ============================================
# MAIN FUNCTION
# ============================================

def load_raw_tarif_data(input_file, output_file=None, use_data_folder=True):
    """
    Main categorization function

    Args:
        input_file: Path to input CSV file
        output_file: Output filename (default from config)
        use_data_folder: If True, save to Data folder; if False, save to same dir as input
    """

    # Determine output directory
    if use_data_folder:
        output_dir = get_data_directory()
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(input_file)

    if output_file is None:
        output_file = DEFAULT_OUTPUT_FILENAME

    output_path = os.path.join(output_dir, output_file)

    # Read data
    print(f"Reading: {input_file}")
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"Loaded {len(df)} rows")
    
    # Convert date columns to datetime
    df['ValidFrom'] = pd.to_datetime(df['ValidFrom'], errors='coerce')
    df['ValidTo'] = pd.to_datetime(df['ValidTo'], errors='coerce')
    
    # Remove duplicates and aggregate date ranges
    # Group by all columns except valid_from and valid_to
    date_cols = ['ValidFrom', 'ValidTo']
    group_cols = [col for col in df.columns if col not in date_cols]
    
    # Group and aggregate dates
    df2 = df.groupby(group_cols, dropna=False).agg({
        'ValidFrom': 'min',
        'ValidTo': 'max'
    }).reset_index()
    
    print(f"After deduplication: {len(df)} rows")

    return df2,output_path

def categorize_tariff_data(df):
    """
    Main categorization function
    
    Args:
        input_file: Path to input CSV file
        output_file: Output filename (default from config)
        use_data_folder: If True, save to Data folder; if False, save to same dir as input
    """
    
    
    
    # Map grid companies
    grid_mapping = load_grid_mapping()
    df = map_grid_codes(df, grid_mapping)
    
    # Categorize
    print("Categorizing...")
    df['ChargeType_Category'] = df['ChargeType'].apply(categorize_chargetype)
    df['Kundetype'] = df.apply(lambda row: find_category(row, kundetype_patterns,kundetype_priority), axis=1)
    df['Tariftype'] = df.apply(lambda row: find_category(row, tariftype_patterns,tariftype_priority), axis=1)
    
    # Reorder columns
    priority_cols = [col for col in OUTPUT_COLUMN_ORDER if col in df.columns]
    other_cols = [col for col in df.columns if col not in priority_cols]
    df = df[priority_cols + other_cols]
    
    # Statistics
    print(f"\nResults:")
    print(f"  Kundetype: {df['Kundetype'].value_counts().to_dict()}")
    print(f"  Tariftype: {df['Tariftype'].value_counts().to_dict()}")
    

    return df

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Standalone execution"""
    data_dir = get_data_directory()
    input_file = os.path.join(data_dir, 'Tarif_data_2021_2024.csv')
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    df,output_path = load_raw_tarif_data(
        input_file=input_file,
        output_file=DEFAULT_OUTPUT_FILENAME,
        use_data_folder=True)
    
    df = categorize_tariff_data(df)

    # Save
    print(f"\nSaving to: {output_path}")
    df.to_excel(output_path, sheet_name='Categorized Data', index=False)
    
    print("✅ Done!")

if __name__ == "__main__":
    main()