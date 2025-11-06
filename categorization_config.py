"""
Categorization Pattern Configuration
"""

# Kundetype patterns - most don't use ChargeType
kundetype_patterns = {
    'Ahøj+': {
        'Note': ['a høj plus', 'Nettarif A0','1.000.000 kWh', ' A0'],
        'Description': ['132-150 kV', '1.000.000KWH','1.000.000 kWh'],
        'ChargeTypeCode': []
    },
    'Ahøj': {
        'Note': ['a høj', 'a-høj', 'net abo a høj', 'nettarif a høj',' AH'],
        'Description': ['30-60 kv', 'a0 forbrug','100.000 - 1000.000 kWh'],
        'ChargeTypeCode': ['e-59', 'e-78', 'e-87']
    },
    'Alav': {
        'Note': ['a lav', 'a-lav', 'net abo a lav', 'nettarif a lav',' AL'],
        'Description': ['10-20 kv-siden af en hovedstation'],
        'ChargeTypeCode': ['e-58', 'e-83', 'e-86']
    },
    'Bhøj': {
        
        'Note': ['b høj', 'b-høj', 'net abo b høj', 'nettarif b høj',' BH'],
        'Description': ['10-20 kv'],
        'ChargeTypeCode': ['e-56', 'e-68', 'e-72', 'e-82']
    },
    'Blav': {
        
        'Note': ['b lav', 'b-lav', 'net abo b lav', 'nettarif b lav'],
        'Description': ['0,4 kv-siden af en 10-20'],
        'ChargeTypeCode': ['e-54', 'e-67', 'e-71', 'e-81']
    },
    'C': {
        'Note': ['net abo c', 'nettarif c', 'type c', ' c ', 'kunde c', 'kategori c','C-Kunde'],
        'Description': ['0,4 kv-nettet', '0.4 kv', '0,4 kv', 'årsaflæst måler', ' 0,4 ', ' 0.4 ','C-Kunde'],
        'ChargeTypeCode': ['e-50', 'e-51', 'e-66', 'e-70', 'e-80', 'e-85']
    }
}

# Tariftype patterns
tariftype_patterns = {
    'tidsdifferentieret': {
        'ChargeType': ['D03'],
        'ChargeTypeCode': [],
        'Note': ['tidsdifferentieret', 'tids-differentieret', 'tid differentieret', 'nettarif'],
        'Description': ['time of use', 'tou', 'time']
    },
    'abonnement': {
        'ChargeType': ['D01'],
        'ChargeTypeCode': [],
        'Note': ['abonnement', 'abo', 'net abo'],
        'Description': ['subscription', 'fast betaling']
    },
    'rådighed': {
        'ChargeType': ['D03'],  # Changed from D01 to D03
        'ChargeTypeCode': [],
        'Note': ['rådighed', 'rådighedstarif'],
        'Description': ['availability', 'kapacitet','Rådighedstarif']
    },
    'indfødning': {
        'ChargeType': ['D03'],  # Changed from D01 to D03
        'ChargeTypeCode': [],
        'Note': ['indfødning', 'producent', 'vindmølle', 'egenprod', 'prod','Nettarif indfødning'],
        'Description': ['feed-in', 'produktion','indfødningspunktet','Indfødningstarif']
    },
    'effektbetaling': {
        'ChargeType': ['D01'],
        'ChargeTypeCode': [],
        'Note': ['effektbetaling', 'effekt', 'effektbidrag'],
        'Description': ['capacity charge', 'demand charge','effektbetaling','Effektbidrag']
    }
}

# NEEDS TO BE IMPLEMENTED!!!
# afregning patterns
afregning_patterns = {
    'E01': { # Skabelonafregnet
        'ChargeType': ['D03'],
        'Note': [],
        'Description': ['årsaflæst']
    },
    'E02': { # Timeafregnet
        'ChargeType': ['D03'],
        'ChargeTypeCode': [],
        'Note': [' time'],
        'Description': [' timeaflæst ']
    },
    'D01': { # Fleksafregnet
        'ChargeType': ['D03'],  # Changed from D01 to D03
        'ChargeTypeCode': [],
        'Note': [' flex'],
        'Description': [' flex', 'timeaflæst']
    }
}

# ChargeType mapping
chargetype_mapping = {
    'D01': 'Abonnement',
    'D02': 'Gebyr',
    'D03': 'Tarif'
}

# System configuration
kundetype_priority = ['Note', 'Description','ChargeTypeCode']
tariftype_priority = ['ChargeType', 'ChargeTypeCode', 'Note', 'Description']
COLUMN_PRIORITY_ORDER = ['ChargeType', 'ChargeTypeCode', 'Note', 'Description']

OUTPUT_COLUMN_ORDER = [
    'Kundetype',
    'Tariftype',
    'ChargeType_Category',
    'MPO_GRID_AREA_CODE',
    'PriceArea',
    'ChargeOwner',
    'ValidFrom',
    'ValidTo'
]

GRID_MAPPING_FILENAME = 'Netselskabs_koder.xlsx'
DEFAULT_OUTPUT_FILENAME = 'tariff_categorization_results3.xlsx'