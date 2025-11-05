# Danish Electricity Tariff Data Pipeline

A complete pipeline for fetching, processing, and categorizing Danish electricity tariff data from the Energi Dataservice API.

## 📋 Overview

This project consists of three Python scripts that work together to:
1. **Fetch** tariff data from Denmark's official energy data API
2. **Categorize** the data into customer types (Kundetype) and tariff types (Tariftype)
3. **Generate** comprehensive Excel reports with statistics and analysis

## 🗂️ Project Structure

```
Tarif_codebase/
│
├── tariff_pipeline_main.py          # Main pipeline script (run this!)
├── fetch_datahub_data.py            # Downloads data from API
├── categorize_tariff_data.py        # Categorizes and analyzes data
└── README.md                        # This file

Data/                                # Created automatically
├── Tarif_data_2021_2024.csv         # Raw data (CSV format)
├── Tarif_data_2021_2024.parquet     # Raw data (Parquet format)
└── tariff_categorization_results.xlsx  # Final categorized results
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy polars requests openpyxl
```

### Running the Pipeline

1. Open `tariff_pipeline_main.py`
2. Edit the configuration section at the top:
```python
START_DATE = '2021-01-01'  # Change start date
END_DATE = '2024-12-31'    # Change end date
USE_CACHED = True          # Set False to force fresh download
```

3. Run the script:
```bash
python tariff_pipeline_main.py
```

That's it! The pipeline will automatically fetch and categorize the data.

## 📄 Script Details

### 1. `tariff_pipeline_main.py` - Main Pipeline

**Purpose:** Orchestrates the entire workflow

**What it does:**
- Runs both data fetching and categorization in sequence
- Provides progress updates and summary statistics
- Handles errors gracefully

**Configuration Variables:**
- `START_DATE`: Start date for data extraction (YYYY-MM-DD format)
- `END_DATE`: End date for data extraction (YYYY-MM-DD format)
- `USE_CACHED`: Whether to use existing downloaded data (True/False)
- `RAW_DATA_FILENAME`: Base name for raw data files
- `OUTPUT_FILENAME`: Name for the final Excel output

### 2. `fetch_datahub_data.py` - Data Fetching

**Purpose:** Downloads tariff data from the Energi Dataservice API

**What it does:**
- Connects to `https://api.energidataservice.dk/dataset/DatahubPricelist`
- Downloads data for the specified date range
- Saves data in both Parquet (efficient) and CSV (readable) formats
- Caches data locally to avoid unnecessary API calls

**Key Features:**
- **Smart caching:** Checks if data already exists before downloading
- **Dual format:** Saves as both .parquet and .csv
- **Auto-directory creation:** Creates the Data folder automatically

**API Endpoint:**
```
https://api.energidataservice.dk/dataset/DatahubPricelist
```

### 3. `categorize_tariff_data.py` - Data Categorization

**Purpose:** Categorizes tariff data into standardized types

**What it does:**
- Reads the CSV file from the Data folder
- Applies pattern matching to categorize each entry
- Generates comprehensive statistics and analysis
- Creates a multi-sheet Excel file with results

**Categorization Logic:**

#### Kundetype (Customer Type)
Identifies five customer types based on voltage levels and connection points:

- **Ahøj**: High voltage A customers (30-60 kV)
  - Patterns: "a høj", "a-høj", "30-60 kv", "e-59", "e-78", "e-87"

- **Alav**: Low voltage A customers (10-20 kV from main station)
  - Patterns: "a lav", "a-lav", "10-20 kv-siden af en hovedstation", "e-58", "e-83"

- **Bhøj**: High voltage B customers (10-20 kV)
  - Patterns: "b høj", "b-høj", "10-20 kv", "e-56", "e-68", "e-72"

- **Blav**: Low voltage B customers (0.4 kV from 10-20 kV station)
  - Patterns: "b lav", "b-lav", "0,4 kv-siden af en 10-20", "e-54", "e-67"

- **C**: Standard customers (0.4 kV network, annual metering)
  - Patterns: "net abo c", "0,4 kv", "årsaflæst måler", "e-50", "e-51"

#### Tariftype (Tariff Type)
Identifies five tariff types:

- **tidsdifferentieret**: Time-of-use tariffs
  - Patterns: "tidsdifferentieret", "time of use", "timeaflæst"

- **abonnement**: Subscription-based tariffs
  - Patterns: "abonnement", "abo", "net abo", "subscription"

- **rådighed**: Availability/capacity tariffs
  - Patterns: "rådighed", "availability", "kapacitet"

- **indfødning**: Feed-in tariffs (for producers)
  - Patterns: "indfødning", "feed-in", "produktion", "vindmølle"

- **effektbetaling**: Power/demand charge tariffs
  - Patterns: "effektbetaling", "effekt", "capacity charge"

**Pattern Matching Strategy:**
The script searches through multiple columns in priority order:
1. `ChargeTypeCode` - Official code
2. `Note` - Detailed notes
3. `Description` - Description text
4. `ChargeType` - Type classification

## 📊 Output Files

### Excel Output Structure

The final Excel file (`tariff_categorization_results.xlsx`) contains multiple sheets:

#### 1. **Categorized Data**
- Original data with two new columns: `Kundetype` and `Tariftype`
- All rows from the original CSV

#### 2. **Statistics**
- Total row count
- Distribution of Kundetype categories (counts and percentages)
- Distribution of Tariftype categories (counts and percentages)

#### 3. **Pattern Analysis**
- Shows which patterns matched for each categorized entry
- Helps understand why entries were categorized the way they were
- Useful for validating the categorization logic

#### 4. **Uncategorized**
- Entries that couldn't be automatically categorized
- Includes both Kundetype and Tariftype uncategorized items
- Useful for improving pattern matching

#### 5. **Code Mapping**
- Analysis of ChargeTypeCode consistency
- Shows the most common category for each code
- Identifies codes with inconsistent categorization

#### 6. **Suggestions**
- AI-generated suggestions for improving uncategorized entries
- Proposes potential categories based on text analysis
- Includes reasoning for each suggestion

## 🔄 Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. USER CONFIGURATION                                  │
│     - Edit dates in tariff_pipeline_main.py             │
│     - Choose whether to use cached data                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. FETCH DATA (fetch_datahub_data.py)                  │
│     - Check if cached data exists                       │
│     - If not (or USE_CACHED=False):                     │
│       • Connect to Energi Dataservice API               │
│       • Download tariff data for date range             │
│       • Save as .parquet and .csv in Data folder        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. CATEGORIZE DATA (categorize_tariff_data.py)         │
│     - Read CSV file                                     │
│     - Apply pattern matching:                           │
│       • Search for Kundetype patterns                   │
│       • Search for Tariftype patterns                   │
│       • Mark uncategorized entries                      │
│     - Generate statistics                               │
│     - Create analysis sheets                            │
│     - Suggest improvements                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. OUTPUT                                              │
│     - Multi-sheet Excel file with:                      │
│       • Categorized data                                │
│       • Statistics                                      │
│       • Pattern analysis                                │
│       • Uncategorized entries                           │
│       • Code mapping                                    │
│       • Improvement suggestions                         │
└─────────────────────────────────────────────────────────┘
```

## 💡 Usage Examples

### Example 1: Default Run (2021-2024)
```python
# No changes needed - just run!
python tariff_pipeline_main.py
```

### Example 2: Custom Date Range
```python
# Edit tariff_pipeline_main.py:
START_DATE = '2022-01-01'
END_DATE = '2023-12-31'
RAW_DATA_FILENAME = 'Tarif_data_2022_2023'
OUTPUT_FILENAME = 'tariff_results_2022_2023.xlsx'

# Then run:
python tariff_pipeline_main.py
```

### Example 3: Force Fresh Download
```python
# Edit tariff_pipeline_main.py:
USE_CACHED = False  # Ignores existing files and downloads fresh data

# Then run:
python tariff_pipeline_main.py
```

## 📈 Understanding the Results

### Categorization Success Rate
The pipeline shows you:
- Total rows processed
- Number of categories found
- Percentage of fully uncategorized entries

**Good results typically show:**
- Less than 10% uncategorized entries
- Consistent patterns across ChargeTypeCodes
- Clear distribution across categories

### Using the Analysis Sheets

**Pattern Analysis Sheet:**
- Review which patterns are being matched most often
- Identify patterns that may need refinement

**Uncategorized Sheet:**
- Look for common patterns in uncategorized entries
- Add new patterns to the script if needed

**Suggestions Sheet:**
- AI-generated suggestions for improving categorization
- Can be used to update the pattern dictionaries

## 🔧 Customization

### Adding New Patterns

To improve categorization accuracy, edit `categorize_tariff_data.py`:

```python
kundetype_patterns = {
    'Ahøj': [
        'a høj', 'a-høj', 'a0',
        'your_new_pattern_here'  # Add new patterns
    ],
    # ... rest of patterns
}
```

### Adding New Categories

1. Add the new category to the pattern dictionary
2. Define its patterns
3. The script will automatically include it in analysis

## ⚠️ Troubleshooting

### "ModuleNotFoundError"
- Ensure all three Python files are in the same directory
- The script automatically adds the directory to Python's path

### "No records found"
- Check your date range - data may not exist for that period
- Verify internet connection for API access

### "Error fetching data"
- API might be temporarily unavailable
- Check if the API endpoint has changed
- Verify date format (YYYY-MM-DD)

### High Percentage of Uncategorized
- Review the Uncategorized sheet in the Excel output
- Check the Suggestions sheet for potential patterns
- Add new patterns to improve categorization

## 📝 Data Sources

**API Documentation:**
- Website: https://www.energidataservice.dk/
- Dataset: DatahubPricelist
- Update Frequency: Regular updates from Danish energy authority

## 🤝 Contributing

To improve the categorization:
1. Run the pipeline and check the Uncategorized sheet
2. Identify common patterns in uncategorized entries
3. Add new patterns to the dictionaries in `categorize_tariff_data.py`
4. Re-run and verify improved categorization

## 📄 License

This project is for data analysis and research purposes.

## 🙋 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the Excel output sheets for insights
3. Examine the console output for error messages

---

**Last Updated:** November 2025
**Version:** 1.0