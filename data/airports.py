"""Airport database organized by continent and country."""

AIRPORTS = {
    'Europa': {
        'România': {
            'București (Otopeni)': 'OTP',
            'Cluj-Napoca': 'CLJ',
            'Timișoara': 'TSR',
            'Iași': 'IAS',
            'Sibiu': 'SBZ',
            'Bacău': 'BCM',
            'Oradea': 'OMR',
            'Suceava': 'SCV',
            'Târgu Mureș': 'TGM',
            'Craiova': 'CRA',
            'Constanța': 'CND',
            'Satu Mare': 'SUJ',
            'Baia Mare': 'BAY',
            'Arad': 'ARW'
        },
        'Regatul Unit': {
            'London Heathrow': 'LHR',
            'London Gatwick': 'LGW',
            'London Stansted': 'STN',
            'London Luton': 'LTN',
            'London City': 'LCY',
            'Manchester': 'MAN',
            'Birmingham': 'BHX',
            'Edinburgh': 'EDI',
            'Glasgow': 'GLA',
            'Bristol': 'BRS',
            'Liverpool': 'LPL',
            'Newcastle': 'NCL',
            'Belfast': 'BFS'
        },
        'Franța': {
            'Paris Charles de Gaulle': 'CDG',
            'Paris Orly': 'ORY',
            'Paris Beauvais': 'BVA',
            'Nice': 'NCE',
            'Lyon': 'LYS',
            'Marseille': 'MRS',
            'Toulouse': 'TLS',
            'Bordeaux': 'BOD',
            'Nantes': 'NTE',
            'Strasbourg': 'SXB'
        },
        'Germania': {
            'Frankfurt': 'FRA',
            'München': 'MUC',
            'Berlin Brandenburg': 'BER',
            'Düsseldorf': 'DUS',
            'Hamburg': 'HAM',
            'Köln/Bonn': 'CGN',
            'Stuttgart': 'STR',
            'Dortmund': 'DTM',
            'Nürnberg': 'NUE',
            'Leipzig': 'LEJ'
        },
        'Italia': {
            'Roma Fiumicino': 'FCO',
            'Roma Ciampino': 'CIA',
            'Milano Malpensa': 'MXP',
            'Milano Linate': 'LIN',
            'Milano Bergamo': 'BGY',
            'Veneția Marco Polo': 'VCE',
            'Veneția Treviso': 'TSF',
            'Napoli': 'NAP',
            'Bologna': 'BLQ',
            'Pisa': 'PSA',
            'Catania': 'CTA',
            'Palermo': 'PMO',
            'Bari': 'BRI',
            'Torino': 'TRN',
            'Florența': 'FLR'
        },
        'Spania': {
            'Madrid Barajas': 'MAD',
            'Barcelona El Prat': 'BCN',
            'Palma de Mallorca': 'PMI',
            'Málaga': 'AGP',
            'Sevilla': 'SVQ',
            'Alicante': 'ALC',
            'Valencia': 'VLC',
            'Bilbao': 'BIO',
            'Ibiza': 'IBZ',
            'Las Palmas': 'LPA',
            'Tenerife Sud': 'TFS',
            'Granada': 'GRX'
        },
        'Țările de Jos': {
            'Amsterdam Schiphol': 'AMS',
            'Rotterdam': 'RTM',
            'Eindhoven': 'EIN',
            'Maastricht': 'MST'
        },
        'Belgia': {
            'Bruxelles': 'BRU',
            'Bruxelles Charleroi': 'CRL',
            'Antwerpen': 'ANR',
            'Liège': 'LGG'
        },
        'Austria': {
            'Viena': 'VIE',
            'Salzburg': 'SZG',
            'Innsbruck': 'INN',
            'Graz': 'GRZ'
        },
        'Elveția': {
            'Zürich': 'ZRH',
            'Geneva': 'GVA',
            'Basel': 'BSL',
            'Berna': 'BRN'
        },
        'Grecia': {
            'Atena': 'ATH',
            'Thessaloniki': 'SKG',
            'Heraklion': 'HER',
            'Rhodos': 'RHO',
            'Corfu': 'CFU',
            'Santorini': 'JTR',
            'Mykonos': 'JMK',
            'Zakynthos': 'ZTH'
        },
        'Portugalia': {
            'Lisabona': 'LIS',
            'Porto': 'OPO',
            'Faro': 'FAO',
            'Funchal (Madeira)': 'FNC',
            'Ponta Delgada': 'PDL'
        },
        'Irlanda': {
            'Dublin': 'DUB',
            'Cork': 'ORK',
            'Shannon': 'SNN',
            'Kerry': 'KIR'
        },
        'Danemarca': {
            'Copenhaga': 'CPH',
            'Billund': 'BLL',
            'Aalborg': 'AAL'
        },
        'Suedia': {
            'Stockholm Arlanda': 'ARN',
            'Göteborg': 'GOT',
            'Malmö': 'MMX',
            'Stockholm Skavsta': 'NYO'
        },
        'Norvegia': {
            'Oslo Gardermoen': 'OSL',
            'Bergen': 'BGO',
            'Stavanger': 'SVG',
            'Trondheim': 'TRD'
        },
        'Finlanda': {
            'Helsinki': 'HEL',
            'Turku': 'TKU',
            'Tampere': 'TMP'
        },
        'Polonia': {
            'Varșovia Chopin': 'WAW',
            'Cracovia': 'KRK',
            'Gdansk': 'GDN',
            'Wrocław': 'WRO',
            'Katowice': 'KTW',
            'Poznań': 'POZ'
        },
        'Cehia': {
            'Praga': 'PRG',
            'Brno': 'BRQ',
            'Ostrava': 'OSR'
        },
        'Ungaria': {
            'Budapesta': 'BUD',
            'Debrecen': 'DEB'
        },
        'Bulgaria': {
            'Sofia': 'SOF',
            'Varna': 'VAR',
            'Burgas': 'BOJ',
            'Plovdiv': 'PDV'
        },
        'Turcia': {
            'Istanbul': 'IST',
            'Istanbul Sabiha Gökçen': 'SAW',
            'Ankara': 'ESB',
            'Antalya': 'AYT',
            'Izmir': 'ADB',
            'Bodrum': 'BJV',
            'Dalaman': 'DLM'
        },
        'Croația': {
            'Zagreb': 'ZAG',
            'Split': 'SPU',
            'Dubrovnik': 'DBV',
            'Pula': 'PUY',
            'Zadar': 'ZAD'
        },
        'Republica Moldova': {
            'Chișinău': 'KIV'
        },
        'Ucraina': {
            'Kiev Boryspil': 'KBP',
            'Odesa': 'ODS',
            'Lviv': 'LWO'
        }
    },
    'America de Nord': {
        'SUA': {
            'New York JFK': 'JFK',
            'New York Newark': 'EWR',
            'New York LaGuardia': 'LGA',
            'Los Angeles': 'LAX',
            'Chicago O\'Hare': 'ORD',
            'Chicago Midway': 'MDW',
            'San Francisco': 'SFO',
            'Miami': 'MIA',
            'Boston': 'BOS',
            'Las Vegas': 'LAS',
            'Orlando': 'MCO',
            'Seattle': 'SEA',
            'Atlanta': 'ATL',
            'Dallas/Fort Worth': 'DFW',
            'Houston': 'IAH',
            'Washington Dulles': 'IAD',
            'Washington Reagan': 'DCA',
            'Philadelphia': 'PHL',
            'Phoenix': 'PHX',
            'Denver': 'DEN',
            'San Diego': 'SAN',
            'Detroit': 'DTW',
            'Minneapolis': 'MSP',
            'Tampa': 'TPA',
            'Portland': 'PDX',
            'Austin': 'AUS',
            'Nashville': 'BNA',
            'New Orleans': 'MSY',
            'Honolulu': 'HNL'
        },
        'Canada': {
            'Toronto Pearson': 'YYZ',
            'Vancouver': 'YVR',
            'Montreal': 'YUL',
            'Calgary': 'YYC',
            'Edmonton': 'YEG',
            'Ottawa': 'YOW',
            'Winnipeg': 'YWG',
            'Halifax': 'YHZ'
        },
        'Mexic': {
            'Ciudad de México': 'MEX',
            'Cancún': 'CUN',
            'Guadalajara': 'GDL',
            'Monterrey': 'MTY',
            'Tijuana': 'TIJ',
            'Puerto Vallarta': 'PVR',
            'Los Cabos': 'SJD'
        }
    },
    'Asia': {
        'Emiratele Arabe Unite': {
            'Dubai': 'DXB',
            'Dubai Al Maktoum': 'DWC',
            'Abu Dhabi': 'AUH',
            'Sharjah': 'SHJ'
        },
        'Qatar': {
            'Doha': 'DOH'
        },
        'Arabia Saudită': {
            'Riyadh': 'RUH',
            'Jeddah': 'JED',
            'Dammam': 'DMM'
        },
        'Israel': {
            'Tel Aviv': 'TLV',
            'Eilat': 'ETM',
            'Haifa': 'HFA'
        },
        'Japonia': {
            'Tokyo Narita': 'NRT',
            'Tokyo Haneda': 'HND',
            'Osaka Kansai': 'KIX',
            'Osaka Itami': 'ITM',
            'Nagoya': 'NGO',
            'Fukuoka': 'FUK',
            'Sapporo': 'CTS'
        },
        'China': {
            'Beijing Capital': 'PEK',
            'Beijing Daxing': 'PKX',
            'Shanghai Pudong': 'PVG',
            'Shanghai Hongqiao': 'SHA',
            'Guangzhou': 'CAN',
            'Shenzhen': 'SZX',
            'Chengdu': 'CTU',
            'Hong Kong': 'HKG'
        },
        'Coreea de Sud': {
            'Seoul Incheon': 'ICN',
            'Seoul Gimpo': 'GMP',
            'Busan': 'PUS',
            'Jeju': 'CJU'
        },
        'Singapore': {
            'Singapore Changi': 'SIN'
        },
        'Thailanda': {
            'Bangkok Suvarnabhumi': 'BKK',
            'Bangkok Don Mueang': 'DMK',
            'Phuket': 'HKT',
            'Chiang Mai': 'CNX',
            'Krabi': 'KBV',
            'Koh Samui': 'USM'
        },
        'Vietnam': {
            'Hanoi': 'HAN',
            'Ho Chi Minh City': 'SGN',
            'Da Nang': 'DAD'
        },
        'Indonezia': {
            'Jakarta': 'CGK',
            'Bali Denpasar': 'DPS',
            'Surabaya': 'SUB'
        },
        'Malaezia': {
            'Kuala Lumpur': 'KUL',
            'Penang': 'PEN',
            'Langkawi': 'LGK'
        },
        'Filipine': {
            'Manila': 'MNL',
            'Cebu': 'CEB',
            'Clark': 'CRK'
        },
        'India': {
            'Delhi': 'DEL',
            'Mumbai': 'BOM',
            'Bangalore': 'BLR',
            'Chennai': 'MAA',
            'Kolkata': 'CCU',
            'Hyderabad': 'HYD',
            'Goa': 'GOI'
        },
        'Maldive': {
            'Malé': 'MLE'
        },
        'Sri Lanka': {
            'Colombo': 'CMB'
        }
    },
    'Africa': {
        'Egipt': {
            'Cairo': 'CAI',
            'Hurghada': 'HRG',
            'Sharm el-Sheikh': 'SSH',
            'Luxor': 'LXR',
            'Marsa Alam': 'RMF'
        },
        'Maroc': {
            'Marrakech': 'RAK',
            'Casablanca': 'CMN',
            'Agadir': 'AGA',
            'Fes': 'FEZ',
            'Tangier': 'TNG'
        },
        'Tunisia': {
            'Tunis': 'TUN',
            'Monastir': 'MIR',
            'Djerba': 'DJE'
        },
        'Africa de Sud': {
            'Johannesburg': 'JNB',
            'Cape Town': 'CPT',
            'Durban': 'DUR'
        },
        'Kenya': {
            'Nairobi': 'NBO',
            'Mombasa': 'MBA'
        },
        'Mauritius': {
            'Port Louis': 'MRU'
        },
        'Seychelles': {
            'Mahé': 'SEZ'
        }
    },
    'America de Sud': {
        'Brazilia': {
            'São Paulo Guarulhos': 'GRU',
            'Rio de Janeiro': 'GIG',
            'Brasília': 'BSB',
            'Salvador': 'SSA',
            'Fortaleza': 'FOR'
        },
        'Argentina': {
            'Buenos Aires': 'EZE',
            'Buenos Aires Aeroparque': 'AEP',
            'Córdoba': 'COR',
            'Mendoza': 'MDZ'
        },
        'Chile': {
            'Santiago': 'SCL',
            'Easter Island': 'IPC'
        },
        'Peru': {
            'Lima': 'LIM',
            'Cusco': 'CUZ'
        },
        'Colombia': {
            'Bogotá': 'BOG',
            'Medellín': 'MDE',
            'Cartagena': 'CTG'
        }
    },
    'Oceania': {
        'Australia': {
            'Sydney': 'SYD',
            'Melbourne': 'MEL',
            'Brisbane': 'BNE',
            'Perth': 'PER',
            'Adelaide': 'ADL',
            'Gold Coast': 'OOL',
            'Cairns': 'CNS',
            'Canberra': 'CBR'
        },
        'Noua Zeelandă': {
            'Auckland': 'AKL',
            'Wellington': 'WLG',
            'Christchurch': 'CHC',
            'Queenstown': 'ZQN'
        },
        'Fiji': {
            'Nadi': 'NAN'
        }
    }
}


def get_continents():
    """Get list of all continents"""
    return sorted(AIRPORTS.keys())


def get_countries_by_continent(continent):
    """Get list of countries in a continent"""
    if continent in AIRPORTS:
        return sorted(AIRPORTS[continent].keys())
    return []


def get_airports_by_country(continent, country):
    """Get list of airports in a country"""
    if continent in AIRPORTS and country in AIRPORTS[continent]:
        return AIRPORTS[continent][country]
    return {}


def search_airport(query):
    """Search airport by name or IATA code"""
    query = query.upper()
    results = []
    
    for continent, countries in AIRPORTS.items():
        for country, airports in countries.items():
            for airport_name, iata_code in airports.items():
                if query in airport_name.upper() or query in iata_code:
                    results.append({
                        'continent': continent,
                        'country': country,
                        'airport': airport_name,
                        'iata': iata_code
                    })
    
    return results


def get_airport_name(iata_code):
    """Get airport full name from IATA code"""
    iata_code = iata_code.upper()
    
    for continent, countries in AIRPORTS.items():
        for country, airports in countries.items():
            for airport_name, code in airports.items():
                if code == iata_code:
                    return f"{airport_name}, {country}"
    
    return iata_code
