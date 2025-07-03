from enum import Enum
from typing import Dict, List, NamedTuple

class TravelRegion(str, Enum):
    NORTH_AMERICA = "NORTH_AMERICA"
    LATAM = "LATAM"
    EMEA = "EMEA"
    ASIA = "ASIA"
    INDIA = "INDIA"
    ANZ = "ANZ"

class CityInfo(NamedTuple):
    full_name: str
    short_code: str
    point_id: str

# Regional mapping with full city info
REGIONAL_CITY_MAPPING: Dict[TravelRegion, List[CityInfo]] = {
    TravelRegion.NORTH_AMERICA: [
        # United States
        CityInfo("SEATTLE", "SEA", "C_121001"),
        CityInfo("BELLEVUE", "BFI", "C_125342"),
        CityInfo("NEW YORK", "NYC", "C_120937"),
        CityInfo("BOSTON", "BOS", "C_120973"),
        CityInfo("ATLANTA", "ATL", "C_121422"),
        CityInfo("CHICAGO", "CHI", "C_121292"),
        CityInfo("MOUNTAIN VIEW", "SJC", "C_131035"),
        CityInfo("SAN DIEGO", "SAN", "C_122118"),
        CityInfo("SAN FRANCISCO", "SFO", "C_121373"),
        CityInfo("DENVER", "DEN", "C_121494"),
        CityInfo("MCLEAN", "DCA", "C_132161"),
        CityInfo("PLANO", "DFW", "C_129121"),
        
        # Canada
        CityInfo("TORONTO", "YYZ", "C_121601"),
        CityInfo("VANCOUVER", "YVR", "C_120854"),
        CityInfo("MONTREAL", "YUL", "C_120873"),
        CityInfo("CALGARY", "YYC", "C_121726"),
    ],
    
    TravelRegion.LATAM: [
        CityInfo("MONTEVIDEO", "MVD", "C_121003"),
        CityInfo("BOGOTA", "BOG", "C_121722"),
        CityInfo("BRASILIA", "BSB", "C_121543"),
        CityInfo("MEXICO CITY", "MEX", "C_121336"),
        CityInfo("BUENOS AIRES", "EZE", "C_121141"),
        CityInfo("LIMA", "LIM", "C_124743"),
        CityInfo("SAO PAULO", "SAO", "C_120980"),
        CityInfo("SANTO DOMINGO", "SDQ", "C_121338"),
        CityInfo("MANAGUA", "MGA", "C_121291"),
        CityInfo("SAN JOSE", "SJO", "C_122423"),
        CityInfo("BELMOPAN", "BZE", "C_122514"),
    ],
    
    TravelRegion.EMEA: [
        # Western Europe
        CityInfo("LONDON", "LON", "C_120812"),
        CityInfo("PARIS", "PAR", "C_120941"),
        CityInfo("MUNICH", "MUC", "C_122215"),
        CityInfo("BERLIN", "BER", "C_120978"),
        CityInfo("STOCKHOLM", "STO", "C_120917"),
        CityInfo("MILANO", "MIL", "C_120928"),
        CityInfo("ZURICH", "ZRH", "C_121663"),
        CityInfo("LISBON", "LIS", "C_120834"),
        CityInfo("MADRID", "MAD", "C_121457"),
        CityInfo("HELSINKI", "HEL", "C_120999"),
        CityInfo("ATHENS", "ATH", "C_121346"),
        CityInfo("AARHUS", "AAR", "C_121341"),
        CityInfo("OSLO", "OSL", "C_120770"),
        CityInfo("DUBLIN", "DUB", "C_120746"),
        CityInfo("AMSTERDAM", "AMS", "C_121511"),
        CityInfo("BRUSSELS", "BRU", "C_121514"),
        
        # Eastern Europe
        CityInfo("RIGA", "RIX", "C_121139"),
        CityInfo("PRAGUE", "PRG", "C_121233"),
        CityInfo("KYIV", "KBP", "C_121308"),
        CityInfo("SARAJEVO", "SJJ", "C_122467"),
        CityInfo("TBILISI", "TBS", "C_121372"),
        CityInfo("LJUBLJANA", "LJU", "C_121224"),
        CityInfo("BRASTISLAVA", "BTS", "C_121144"),
        CityInfo("BEOGRAD", "BEG", "C_121035"),
        CityInfo("CHISINAU", "KIV", "C_123588"),
        CityInfo("SOFIA", "SOF", "C_120895"),
        CityInfo("BUCHAREST", "BUH", "C_121359"),
        CityInfo("WARSAW", "WAW", "C_121150"),
        CityInfo("NICOSIA", "LCA", "C_122262"),
        CityInfo("ZAGREB", "ZAG", "C_124777"),
        CityInfo("BUDAPEST", "BUD", "C_121361"),
        
        # Middle East & Africa
        CityInfo("RIYADH", "RUH", "C_121241"),
        CityInfo("ANKARA", "ANK", "C_120858"),
        CityInfo("DUBAI", "DXB", "C_120817"),
        CityInfo("CAIRO", "CAI", "C_120756"),
        CityInfo("AMMAN", "AMM", "C_121638"),
        CityInfo("HERZLIYA", "TLV", "C_126260"),
    ],
    
    TravelRegion.ASIA: [
        CityInfo("HONG KONG", "HKG", "C_120786"),
        CityInfo("JAKARTA", "JKT", "C_122274"),
        CityInfo("SEOUL", "SEL", "C_120871"),
        CityInfo("TOKYO", "TYO", "C_120899"),
        CityInfo("HO CHI MINH", "SGN", "C_121008"),
        CityInfo("SINGAPORE", "SIN", "C_120758"),
        CityInfo("BANGKOK", "BKK", "C_120903"),
        CityInfo("KUALA LUMPUR", "KUL", "C_121313"),
        CityInfo("ISLAMABAD", "ISB", "C_123443"),
    ],
    
    TravelRegion.INDIA: [
        CityInfo("BENGALURU", "BLR", "C_121636"),
        CityInfo("MUMBAI", "BOM", "C_120759"),
        CityInfo("PUNE", "PNQ", "C_122041"),
    ],
    
    TravelRegion.ANZ: [
        # Australia
        CityInfo("CANBERRA", "CBR", "C_127908"),
        CityInfo("SYDNEY", "SYD", "C_122815"),
        CityInfo("BRISBANE", "BNE", "C_121648"),
        CityInfo("MELBOURNE", "MEL", "C_121881"),
        CityInfo("PERTH", "PER", "C_124850"),
        
        # New Zealand & Pacific
        CityInfo("AUCKLAND", "AKL", "C_121298"),
        CityInfo("NOUMEA", "NOU", "C_121300"),
    ]
}

# Helper functions for easy lookups
def get_cities_by_region(region: TravelRegion) -> List[CityInfo]:
    """Get all cities in a specific region"""
    return REGIONAL_CITY_MAPPING.get(region, [])

def get_region_by_city_name(city_name: str) -> TravelRegion | None:
    """Find which region a city belongs to by full name"""
    city_name_upper = city_name.upper()
    for region, cities in REGIONAL_CITY_MAPPING.items():
        if any(city.full_name == city_name_upper for city in cities):
            return region
    return None

def get_city_info_by_name(city_name: str) -> CityInfo | None:
    """Get city info by full name"""
    city_name_upper = city_name.upper()
    for cities in REGIONAL_CITY_MAPPING.values():
        for city in cities:
            if city.full_name == city_name_upper:
                return city
    return None

def get_city_info_by_short_code(short_code: str) -> CityInfo | None:
    """Get city info by short code"""
    short_code_upper = short_code.upper()
    for cities in REGIONAL_CITY_MAPPING.values():
        for city in cities:
            if city.short_code == short_code_upper:
                return city
    return None

def get_all_cities_flat() -> List[CityInfo]:
    """Get all cities as a flat list"""
    all_cities = []
    for cities in REGIONAL_CITY_MAPPING.values():
        all_cities.extend(cities)
    return all_cities

# Legacy compatibility - simple region to IATA codes mapping
REGIONAL_IATA_CODES: Dict[TravelRegion, List[str]] = {
    region: [city.short_code for city in cities]
    for region, cities in REGIONAL_CITY_MAPPING.items()
}

# Legacy compatibility - simple region to city names mapping
REGIONAL_CITY_NAMES: Dict[TravelRegion, List[str]] = {
    region: [city.full_name for city in cities]
    for region, cities in REGIONAL_CITY_MAPPING.items()
} 