"""
Categorization Pattern Configuration


"""

# Kundetype patterns - most don't use ChargeType
kundetype_priority = ['Note', 'Description','ChargeTypeCode']
kundetype_patterns = {
    'A0': {
        'Note': [
                 'Nettarif A0'
                 , ' A0'],
        'Description': [' 132-150 kV ',
                        ' 132/150 kV',
                        '132/150 og 400 kv nettet',
                        'tilsluttet transmissionsnettet'],
        'ChargeTypeCode': []
    },
    'Ahøj+maske': {
        'Note': ['a høj plus maske'
                 ,' A høj plus maske' # Er med to gange så A høj fra "A høj" ikke går at den bliver ukategoriseret
                 ,'A-høj + maske'
                 ,'ahøjplusmaske'
                 ,' a '
                 ,'Net abo A høj plus maske'],
        'Description': ['132-150/30-60 kV-transformerstation i maskenet'],
        'ChargeTypeCode': []
    },
    'Ahøj+': {
        'Note': ['a høj plus'
                 ,' A høj plus' # Er med to gange så A høj fra "A høj" ikke går at den bliver ukategoriseret
                 ,'A-høj +'
                 ,'ahøjplus'
                 ,' a '],
        'Description': [
                         'A-høj +',
                         'A høj plus',
                         'AHØJPLUS'],
        'ChargeTypeCode': ['A200GWH R','A200GWH D']
    },
    'Ahøj': {
        'Note': ['a høj', 
                 'a-høj', 
                 'net abo a høj', 
                 'nettarif a høj',
                  ' AH',
                  'ahøj',
                  ' a ',
                  'a1'],
        'Description': ['30-60 kv',
                        '30-60 kV-nettet',
                        ' 60 kV ',
                        '60 kV-net',
                        ' 60/20 kV ', 
                        'overliggende net 60/10' # Er dette korrekt? Hvad menes med overliggende net?
                        ],
        'ChargeTypeCode': ['e-59', 
                           'e-78', 
                           'e-87']
    },
    'Alav': {
        'Note': ['a lav', 
                 'a-lav', 
                 'net abo a lav', 
                 'nettarif a lav',
                 ' AL',
                 'alav',
                 ' a ',
                 'A2'],
        'Description': ['10-20 kv-siden af en hovedstation',
                        '10-20 kV-siden af en 30-60/10-20 kV-transformerstation',
                        '10-30 kV-siden af en hovedstation'],
        'ChargeTypeCode': ['e-58', 
                           'e-83', 
                           'e-86']
    },
    'Bhøj': {
        
        'Note': ['b høj', 
                 'b-høj', 
                 'net abo b høj', 
                 'nettarif b høj',
                 ' BH',
                 'B 20GWh',
                 'bhøj', 
                 ' b ',
                 'b1'],
        'Description': [' 10-20 kv ',
                        'er i 10-20 kV-nettet',
                        'er i 10-20 kV',
                        'er i 10-30 kV-nettet',
                        ' 10-30 kV ',
                        '10 KV niveau i 10/04 transformerstation',
                        ],
        'ChargeTypeCode': ['e-56', 'e-68', 'e-72', 'e-82','B20GWh D','B20GWh R D']
    },
    'Blav': {
        
        'Note': ['b lav'
                 ,'b-lav'
                 ,'blav'
                 , 'net abo b lav'
                 , 'nettarif b lav'
                 ,' b '
                 ,'b2'],
        'Description': ['0,4 kv-siden af en 10-20',
                        '0,4 kV-siden af en 10-20/0,4 kV-station',
                        '0,4 kV-siden af en 10-20/0,4 kV-transformerstation',
                        '0,4 kV-siden af en 10-30/0,4 kV transformerstation'
                        ],
        'ChargeTypeCode': ['e-54', 'e-67', 'e-71', 'e-81']
    },
    'C': {
        'Note': ['net abo c'
                 ,'nettarif c'
                 , 'type c'
                 , 'kunde c'
                 , 'kategori c'
                 ,'C-Kunde'
                 , ' c '
                 ,'net C'],
        'Description': ['0,4 kv-nettet',
                        '0,4 kV-nettet', 
                        ' 0.4 kv ', 
                        ' 0,4 kv ',
                        'Clav', # Det her er nok noget med produktion?
                        'Chøj', # Det her er nok noget med produktion?
                        'C-Kunde',
                        ' c '],
        'ChargeTypeCode': ['e-50', 'e-51', 'e-66', 'e-70', 'e-80', 'e-85'
                           ,'50001']# ud fra observation... Ikke sikkert
    }
}

# Type patterns
pris_element_priority = ['ChargeType',  'Note', 'Description','ChargeTypeCode']
pris_element_patterns = {
    'Tarif': {
        'ChargeType': ['D03'],
        
        'Note': ['nettarif'
                ,'Net tarif'
                ,'timetarif'
                ,'Netarif '
                ,'Nettarrif' # Stavefejl  i datasæt
                ,'Nettarit'   # Stavefejl  i datasæt
                ],
        'Description': ['Nettarif'
                        ,'Tarif, '
                        ,'Tarif '
                        ,' tarif'
                        ,'tarifmodel 3.0'],
        'ChargeTypeCode': ['50001'] # Ud fra observation..
    },
    'abonnement': {
        'ChargeType': ['D01'],
        'Note': ['abonnement', 'abo', 'net abo','Netabonnement','Abb '],
        'Description': ['Abonnement '],
        'ChargeTypeCode': ['NT15002','NT15003']
    },
    'rådighedstarif': {
        'ChargeType': ['D01','D03'],  # Kan både være Abonnement og tarif
        'Note': ['rådighedstarif','rådighedstarif','rådighedstarif','rådighedstarif'],
        'Description': ['Rådighedstarif','Rådighedstarif','Rådighedstarif','Rådighedstarif',
                        'egenproducenten har produktionsmåler'],
        'ChargeTypeCode': []
    },
        'rådighedsbetaling': {
        'ChargeType': ['D01','D03'],  # Kan både være Abonnement og tarif
        'Note': ['rådighedsbetaling','rådighedsbetaling','rådighedsbetaling','rådighedsbetaling','Egenproducentbidrag'],
        'Description': ['rådighedsbetaling','rådighedsbetaling','rådighedsbetaling','rådighedsbetaling','Egenproducentbidrag'],
        'ChargeTypeCode': []
    },
    'indfødning': {
        'ChargeType': ['D03'],  # Changed from D01 to D03
        'Note': ['indfødning','indfødning','indfødning', 'producent', 'vindmølle', 'indfødningsnettarif'
                 ,'Nettarif indfødning'
                 ,'Netarif indfødning'
                 ,'uden aftagepligt',' produktion '],
        'Description': ['indfødningspunktet','Indfødningstarif','indfødningsnettarif',' produktion'],
        'ChargeTypeCode': []
    },
    'effektbetaling': {
        'ChargeType': ['D01','D03'],
        'Note': ['effektbetaling','effektbetaling','effektbetaling'
                 , 'effekt', 'effektbidrag',
                 'effekttarif','effekttarif','effekttarif'],
        'Description': ['effektbetaling',
                        ' effektbetaling',
                        'Effektbidrag',
                        'Abonnement for effektbetaling'],
        'ChargeTypeCode': []
    },
    'Gebyr': {
        'ChargeType': ['D02'],
        'Note': [ 'gebyr'],
        'Description': ['gebyr'],
        'ChargeTypeCode': []
    },
    'Elafgift': {
        'ChargeType': [],
        'Note': [ 'Elafgift'],
        'Description': ['Elafgiften'],
        'ChargeTypeCode': []
    },
    'Balancetarif': {
        'ChargeType': [],
        
        'Note': ['Balancetarif '
                ],
        'Description': ['Balancetarif'],
        'ChargeTypeCode': ['45012']
    },
        'PSO-tarif': {
        'ChargeType': [],
        
        'Note': ['PSO-tarif'
                ],
        'Description': ['PSO tarif'],
        'ChargeTypeCode': []
    },
    'Systemtarif': {
        'ChargeType': [],
        
        'Note': ['Systemtarif'
                ],
        'Description': ['Systemafgiften'],
        'ChargeTypeCode': []
    }
}

# NEEDS TO BE IMPLEMENTED!!!
# afregning patterns
afregning_priority = ['Note', 'Description','ChargeTypeCode']
afregning_patterns = {
    'E01': { # Skabelonafregnet
        'Note': ['skabelon'],
        'Description': ['årsaflæst','skabelon'],
        'ChargeType': ['AAL-NTR01'] # Rabat
        
    },
    'E02': { # Timeafregnet
        'Note': [' time','(time)'],
        'Description': [' timeaflæst ', 'årsaflæst','(time)','time'],
        'ChargeTypeCode': []
    },
    'D01': { # Fleksafregnet
        'Note': [' flex','flexafregning','(flex)','Flex'],
        'Description': [' flex', 'timeaflæst',' Flexaflæst','(flex)','flex'],
        'ChargeTypeCode': []
    }
}


# bruger patterns
bruger_priority = ['Note', 'Description']
bruger_fallback = 'Forbrug'
bruger_patterns = {
    'Forbrug': { # E17
        'Note': ['forbrug','elkedel','elpatron'],
        'Description': ['forbrug','forbrug','elkedel','elpatron']
        
    },
    'Produktion': { # E18
        'Note': ['Produktion','Indfødningstarif','vindmølle','kraftværk','solcelle','VE-','Affald'],
        'Description': ['Produktion','Indfødningstarif',' producent,','vindmølle','kraftværk','solcelle','VE-','Affald']
    },
    'Egenproduktion': { # 
        'Note': ['Egenproduktion','egenproduktion','egenproduction','egenproducent'
                 ,'egenproducent','Rådighed','egen produktion','egenprod','Egenproducentbidrag'],
        'Description': ['Egenproduktion','egenproduktion',
                        'egenproducent','Rådighed','egen produktion','egenprod','Egenproducentbidrag']
    }
}

Rabat_priority = ['Note', 'Description']
Rabat_patterns = {
    "Rabat": { # 
        'Note': ['Rabat'],
        'Description': ['Rabat']
    }
}
net_priority = ['Note', 'Description']
net_patterns = {
    "Overliggende net": { # 
        'Note': ['Overliggende','Overordnet','mellemliggende'],
        'Description': ['Overliggende','Overordnet','mellemliggende']
    }
}



# System configuration




OUTPUT_COLUMN_ORDER = [
    'KundeType',
    'PrisElement',
    'Bruger',
    'OverliggendeNet',
    'Rabat',
    #'Afregningstype',
    'ChargeOwner',
    'ValidFrom',
    'ValidTo'
]

GRID_MAPPING_FILENAME = 'Netselskabs_koder.xlsx'
DEFAULT_OUTPUT_FILENAME = 'tariff_categorization_results.xlsx'

use_temp_file = False
