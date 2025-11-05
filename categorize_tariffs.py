import pandas as pd
import numpy as np
import os
import re
from collections import Counter
from datetime import datetime

# Enhanced categorization patterns based on actual data analysis
kundetype_patterns = {
    'Ahøj': [
        'a høj', 'a-høj', 'a0', 'net abo a høj', 'nettarif a høj',
        '30-60 kv', 'a0 forbrug', 'e-59', 'e-78', 'e-87'
    ],
    'Alav': [
        'a lav', 'a-lav', 'net abo a lav', 'nettarif a lav',
        '10-20 kv-siden af en hovedstation', 'e-58', 'e-83', 'e-86'
    ],
    'Bhøj': [
        'b høj', 'b-høj', 'net abo b høj', 'nettarif b høj',
        '10-20 kv', 'e-56', 'e-68', 'e-72', 'e-82'
    ],
    'Blav': [
        'b lav', 'b-lav', 'net abo b lav', 'nettarif b lav',
        '0,4 kv-siden af en 10-20', 'e-54', 'e-67', 'e-71', 'e-81'
    ],
    'C': [
        'net abo c', 'nettarif c', 'type c', ' c ', 'kunde c', 'kategori c',
        '0,4 kv-nettet', '0.4 kv', '0,4 kv', 'årsaflæst måler',
        'e-50', 'e-51', 'e-66', 'e-70', 'e-80', 'e-85'
    ]
}

tariftype_patterns = {
    'tidsdifferentieret': [
        'tidsdifferentieret', 'tids-differentieret', 'tid differentieret',
        'time of use', 'tou', 'timeaflæst', 'time', 'nettarif'
    ],
    'abonnement': [
        'abonnement', 'abo', 'net abo', 'subscription', 'fast betaling'
    ],
    'rådighed': [
        'rådighed', 'availability', 'kapacitet', 'rådighedstarif'
    ],
    'indfødning': [
        'indfødning', 'feed-in', 'produktion', 'producent', 'vindmølle',
        'egenprod', 'produktion', 'prod'
    ],
    'effektbetaling': [
        'effektbetaling', 'effekt', 'capacity charge', 'demand charge'
    ]
}

def get_script_directory():
    """Get the directory where the script is located"""
    return os.path.dirname(os.path.abspath(__file__))

def get_data_directory():
    """Get the Data directory parallel to the script directory"""
    script_dir = get_script_directory()
    return os.path.join(os.path.dirname(script_dir), 'Data')

def ensure_data_directory():
    """Ensure the Data directory exists"""
    data_dir = get_data_directory()
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def find_category(row, category_patterns, priority_columns=['ChargeTypeCode', 'Note', 'Description', 'ChargeType']):
    """
    Find which category a row belongs to based on pattern matching.
    Checks multiple columns in order of priority for better accuracy.
    """
    for category, patterns in category_patterns.items():
        for col in priority_columns:
            if col in row and pd.notna(row[col]):
                text_lower = str(row[col]).lower()
                for pattern in patterns:
                    if pattern in text_lower:
                        return category
    
    return "Uncategorized"

def enhanced_categorize_tariff_data(
    file_path, 
    output_filename=None,
    use_data_folder=True
):
    """
    Enhanced categorization of tariff data with improved pattern matching
    """
    try:
        # Determine output directory
        if use_data_folder:
            output_dir = ensure_data_directory()
        else:
            output_dir = os.path.dirname(file_path)
        
        if output_filename is None:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_filename = f"{base_name}_categorized.xlsx"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # Read the CSV file
        print(f"Reading data from: {file_path}")
        df = pd.read_csv(file_path, encoding='utf-8')
        
        print(f"Successfully read {len(df)} rows from CSV")
        print(f"Columns found: {df.columns.tolist()}")
        
        # Verify required columns exist
        required_columns = ['ChargeType', 'ChargeTypeCode', 'Note', 'Description']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns: {missing_columns}")
        
        # Convert text columns to string and handle NaN values
        for col in required_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', '')
        
        # Apply categorization
        print("Applying categorization...")
        df['Kundetype'] = df.apply(
            lambda row: find_category(row, kundetype_patterns), 
            axis=1
        )
        df['Tariftype'] = df.apply(
            lambda row: find_category(row, tariftype_patterns), 
            axis=1
        )
        
        # Generate comprehensive statistics
        stats = generate_comprehensive_stats(df)
        
        # Create analysis sheets
        analysis_data = create_analysis_sheets(df)
        
        # Save to Excel with multiple sheets
        print(f"Saving results to: {output_path}")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main categorized data
            df.to_excel(writer, sheet_name='Categorized Data', index=False)
            
            # Statistics sheet
            stats_df = create_stats_dataframe(stats)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Pattern analysis
            analysis_data['pattern_matches'].to_excel(writer, sheet_name='Pattern Analysis', index=False)
            
            # Uncategorized entries
            analysis_data['uncategorized'].to_excel(writer, sheet_name='Uncategorized', index=False)
            
            # Code mapping analysis
            analysis_data['code_mapping'].to_excel(writer, sheet_name='Code Mapping', index=False)
            
            # Suggestions for improvement
            if not analysis_data['suggestions'].empty:
                analysis_data['suggestions'].to_excel(writer, sheet_name='Suggestions', index=False)
        
        print(f"Excel file saved successfully!")
        print_comprehensive_stats(stats)
        
        return {
            'df': df,
            'stats': stats,
            'output_path': output_path,
            'analysis': analysis_data
        }
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def generate_comprehensive_stats(df):
    """Generate comprehensive statistics about the categorization"""
    total_rows = len(df)
    
    # Basic categorization counts
    kundetype_counts = df['Kundetype'].value_counts()
    tariftype_counts = df['Tariftype'].value_counts()
    
    # Cross-tabulation
    cross_tab = pd.crosstab(df['Kundetype'], df['Tariftype'], margins=True)
    
    # Uncategorized analysis
    uncategorized_both = len(df[
        (df['Kundetype'] == 'Uncategorized') & 
        (df['Tariftype'] == 'Uncategorized')
    ])
    
    # ChargeTypeCode mapping analysis
    code_kundetype = df.groupby('ChargeTypeCode')['Kundetype'].agg(['count', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Mixed'])
    code_tariftype = df.groupby('ChargeTypeCode')['Tariftype'].agg(['count', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Mixed'])
    
    return {
        'total_rows': total_rows,
        'kundetype_counts': kundetype_counts,
        'tariftype_counts': tariftype_counts,
        'cross_tab': cross_tab,
        'uncategorized_both': uncategorized_both,
        'code_kundetype': code_kundetype,
        'code_tariftype': code_tariftype
    }

def create_analysis_sheets(df):
    """Create detailed analysis sheets for the Excel output"""
    
    # Pattern matching analysis
    pattern_analysis = []
    for _, row in df.iterrows():
        for category_type, patterns_dict in [('Kundetype', kundetype_patterns), ('Tariftype', tariftype_patterns)]:
            category = row[category_type]
            if category != 'Uncategorized':
                # Find which pattern matched
                matched_patterns = []
                for col in ['ChargeTypeCode', 'Note', 'Description', 'ChargeType']:
                    if col in row and pd.notna(row[col]):
                        text_lower = str(row[col]).lower()
                        for pattern in patterns_dict[category]:
                            if pattern in text_lower:
                                matched_patterns.append(f"{col}:'{pattern}'")
                
                pattern_analysis.append({
                    'ChargeTypeCode': row['ChargeTypeCode'],
                    'Note': row['Note'],
                    'Category_Type': category_type,
                    'Assigned_Category': category,
                    'Matched_Patterns': '; '.join(matched_patterns[:3])  # Top 3 matches
                })
    
    pattern_df = pd.DataFrame(pattern_analysis).drop_duplicates()
    
    # Uncategorized analysis
    uncategorized = df[
        (df['Kundetype'] == 'Uncategorized') | 
        (df['Tariftype'] == 'Uncategorized')
    ][['ChargeTypeCode', 'Note', 'Description', 'Kundetype', 'Tariftype']].drop_duplicates()
    
    # Code mapping analysis
    code_mapping = []
    for code in df['ChargeTypeCode'].unique():
        code_data = df[df['ChargeTypeCode'] == code]
        kundetype_mode = code_data['Kundetype'].mode()
        tariftype_mode = code_data['Tariftype'].mode()
        
        code_mapping.append({
            'ChargeTypeCode': code,
            'Count': len(code_data),
            'Most_Common_Kundetype': kundetype_mode.iloc[0] if len(kundetype_mode) > 0 else 'N/A',
            'Kundetype_Consistency': len(code_data['Kundetype'].unique()) == 1,
            'Most_Common_Tariftype': tariftype_mode.iloc[0] if len(tariftype_mode) > 0 else 'N/A',
            'Tariftype_Consistency': len(code_data['Tariftype'].unique()) == 1,
            'Sample_Note': code_data['Note'].iloc[0] if len(code_data) > 0 else ''
        })
    
    code_mapping_df = pd.DataFrame(code_mapping).sort_values('Count', ascending=False)
    
    # Suggestions for uncategorized items
    suggestions = suggest_improvements(uncategorized)
    
    return {
        'pattern_matches': pattern_df,
        'uncategorized': uncategorized,
        'code_mapping': code_mapping_df,
        'suggestions': suggestions
    }

def suggest_improvements(uncategorized_df):
    """Suggest improvements for uncategorized items"""
    suggestions = []
    
    for _, row in uncategorized_df.iterrows():
        note = str(row['Note']).lower()
        desc = str(row['Description']).lower()
        code = str(row['ChargeTypeCode']).lower()
        
        suggestion = {
            'ChargeTypeCode': row['ChargeTypeCode'],
            'Note': row['Note'],
            'Current_Kundetype': row['Kundetype'],
            'Current_Tariftype': row['Tariftype'],
            'Suggested_Kundetype': '',
            'Suggested_Tariftype': '',
            'Reasoning': ''
        }
        
        # Kundetype suggestions
        if any(x in note or x in desc for x in ['a', 'høj', 'lav']):
            if 'a' in note and 'høj' in note:
                suggestion['Suggested_Kundetype'] = 'Ahøj'
                suggestion['Reasoning'] += 'Contains "a" and "høj"; '
            elif 'a' in note and 'lav' in note:
                suggestion['Suggested_Kundetype'] = 'Alav'
                suggestion['Reasoning'] += 'Contains "a" and "lav"; '
            elif 'b' in note and 'høj' in note:
                suggestion['Suggested_Kundetype'] = 'Bhøj'
                suggestion['Reasoning'] += 'Contains "b" and "høj"; '
            elif 'b' in note and 'lav' in note:
                suggestion['Suggested_Kundetype'] = 'Blav'
                suggestion['Reasoning'] += 'Contains "b" and "lav"; '
        
        if 'c' in note or '0,4' in desc or '0.4' in desc:
            suggestion['Suggested_Kundetype'] = 'C'
            suggestion['Reasoning'] += 'Contains "c" or voltage indicators; '
        
        # Tariftype suggestions
        if 'abo' in note or 'abonnement' in desc:
            suggestion['Suggested_Tariftype'] = 'abonnement'
            suggestion['Reasoning'] += 'Contains subscription terms; '
        elif 'time' in note or 'timeaflæst' in desc:
            suggestion['Suggested_Tariftype'] = 'tidsdifferentieret'
            suggestion['Reasoning'] += 'Contains time-related terms; '
        elif any(x in note or x in desc for x in ['producent', 'produktion', 'vindmølle']):
            suggestion['Suggested_Tariftype'] = 'indfødning'
            suggestion['Reasoning'] += 'Contains production terms; '
        elif 'effekt' in note or 'effekt' in desc:
            suggestion['Suggested_Tariftype'] = 'effektbetaling'
            suggestion['Reasoning'] += 'Contains power/effect terms; '
        
        if suggestion['Suggested_Kundetype'] or suggestion['Suggested_Tariftype']:
            suggestions.append(suggestion)
    
    return pd.DataFrame(suggestions)

def create_stats_dataframe(stats):
    """Convert statistics to DataFrame format"""
    rows = []
    
    # Overall stats
    rows.append({'Category': 'Overall', 'Metric': 'Total Rows', 'Value': stats['total_rows']})
    
    # Kundetype distribution
    for category, count in stats['kundetype_counts'].items():
        percentage = (count / stats['total_rows']) * 100
        rows.append({
            'Category': 'Kundetype',
            'Metric': category,
            'Value': count,
            'Percentage': f'{percentage:.2f}%'
        })
    
    # Tariftype distribution
    for category, count in stats['tariftype_counts'].items():
        percentage = (count / stats['total_rows']) * 100
        rows.append({
            'Category': 'Tariftype',
            'Metric': category,
            'Value': count,
            'Percentage': f'{percentage:.2f}%'
        })
    
    return pd.DataFrame(rows)

def print_comprehensive_stats(stats):
    """Print comprehensive statistics"""
    print(f"\n{'='*50}")
    print("CATEGORIZATION RESULTS SUMMARY")
    print(f"{'='*50}")
    
    print(f"Total rows processed: {stats['total_rows']}")
    
    print(f"\nKUNDETYPE DISTRIBUTION:")
    for category, count in stats['kundetype_counts'].items():
        percentage = (count / stats['total_rows']) * 100
        print(f"  {category}: {count} ({percentage:.2f}%)")
    
    print(f"\nTARIFTYPE DISTRIBUTION:")
    for category, count in stats['tariftype_counts'].items():
        percentage = (count / stats['total_rows']) * 100
        print(f"  {category}: {count} ({percentage:.2f}%)")
    
    print(f"\nCompletely uncategorized: {stats['uncategorized_both']} rows")
    
    print(f"\nCROSS-TABULATION (Kundetype vs Tariftype):")
    print(stats['cross_tab'])

def main():
    """Main execution function"""
    # Set up file paths using the Data directory structure
    script_dir = get_script_directory()
    data_dir = get_data_directory()
    
    # Input file path - adjust this to your actual file location
    input_file = os.path.join(data_dir, 'Tarif_data_2021_2024.csv')
    
    # Alternative: if file is in same directory as script
    # input_file = os.path.join(script_dir, 'Tarif_data_2021_2024.csv')
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        print("Please ensure the CSV file is in the correct location.")
        return
    
    # Run the categorization
    result = enhanced_categorize_tariff_data(
        file_path=input_file,
        output_filename='tariff_categorization_results.xlsx',
        use_data_folder=True
    )
    
    if 'error' not in result:
        print(f"\n✅ Categorization completed successfully!")
        print(f"📊 Results saved to: {result['output_path']}")
        
        # Quick summary
        df = result['df']
        print(f"\n📈 Quick Summary:")
        print(f"   Total rows: {len(df)}")
        print(f"   Kundetype categories: {df['Kundetype'].nunique()}")
        print(f"   Tariftype categories: {df['Tariftype'].nunique()}")
        print(f"   Uncategorized (both): {len(df[(df['Kundetype'] == 'Uncategorized') & (df['Tariftype'] == 'Uncategorized')])}")
        
    else:
        print(f"❌ Error occurred: {result['error']}")

if __name__ == "__main__":
    main()