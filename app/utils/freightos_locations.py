"""
Freightos location codes and country IDs mapping.

This dictionary maps location names to their corresponding Freightos location codes and country IDs.
Used for generating Freightos shipping matrix computations.
"""

FREIGHTOS_LOCATIONS = {
    "LONDON": {"locationCode": "GBLON", "countryID": "GB"},
    "PARIS": {"locationCode": "FRPAR", "countryID": "FR"},
    "CANBERRA": {"locationCode": "AUSYD", "countryID": "AU"},  # Use Sydney port for Canberra
    "SYDNEY": {"locationCode": "AUSYD", "countryID": "AU"},
    "BRISBANE": {"locationCode": "AUBNE", "countryID": "AU"},
    "MELBOURNE": {"locationCode": "AUMEL", "countryID": "AU"},
    "PERTH": {"locationCode": "AUPER", "countryID": "AU"},
    "HONG KONG": {"locationCode": "HKHKG", "countryID": "HK"},
    "SEATTLE": {"locationCode": "USSEA", "countryID": "US"},
    "BELLEVUE": {"locationCode": "USSEA", "countryID": "US"},  # Use Seattle port for Bellevue
    "NEW YORK": {"locationCode": "USNYC", "countryID": "US"},
    "BOSTON": {"locationCode": "USBOS", "countryID": "US"},
    "ATLANTA": {"locationCode": "USATL", "countryID": "US"},
    "CHICAGO": {"locationCode": "USCHI", "countryID": "US"},
    "MOUNTAIN VIEW": {"locationCode": "USLAX", "countryID": "US"},  # Use LA port for Mountain View
    "SAN DIEGO": {"locationCode": "USSAN", "countryID": "US"},  # Use LA port for San Diego
    "SAN FRANCISCO": {"locationCode": "USOAK", "countryID": "US"},  # Use Oakland port for SF
    "DENVER": {"locationCode": "USDEN", "countryID": "US"},  # Use Chicago port for Denver
    "MONTEVIDEO": {"locationCode": "UYMVD", "countryID": "UY"},
    "MCLEAN": {"locationCode": "USNYC", "countryID": "US"},  # Use NYC port for McLean
    "JAKARTA": {"locationCode": "IDJKT", "countryID": "ID"},
    "BENGALURU": {"locationCode": "INBOM", "countryID": "IN"},  # Use Mumbai port for Bengaluru
    "MUNICH": {"locationCode": "DEMUC", "countryID": "DE"},  # Use Hamburg port for Munich
    "BERLIN": {"locationCode": "DEBER", "countryID": "DE"},  # Use Hamburg port for Berlin
    "RIGA": {"locationCode": "LVRIX", "countryID": "LV"},
    "BOGOTA": {"locationCode": "COBOG", "countryID": "CO"},
    "TORONTO": {"locationCode": "CATOR", "countryID": "CA"},
    "RIYADH": {"locationCode": "SARUH", "countryID": "SA"},
    "ANKARA": {"locationCode": "TRIST", "countryID": "TR"},  # Use Istanbul port for Ankara
    "STOCKHOLM": {"locationCode": "SESTO", "countryID": "SE"},
    "MILANO": {"locationCode": "ITMIL", "countryID": "IT"},  # Use Genoa port for Milano
    "DUBAI": {"locationCode": "AEDXB", "countryID": "AE"},
    "ZURICH": {"locationCode": "CHZRH", "countryID": "CH"},  # Use Basel port for Zurich
    "BRASILIA": {"locationCode": "BRSSZ", "countryID": "BR"},  # Use Santos port for Brasilia
    "CAIRO": {"locationCode": "EGALY", "countryID": "EG"},  # Use Alexandria port for Cairo
    "MEXICO CITY": {"locationCode": "MXMEX", "countryID": "MX"},  # Use Veracruz port for Mexico City
    "SEOUL": {"locationCode": "KRSEL", "countryID": "KR"},  # Use Busan port for Seoul
    "AUCKLAND": {"locationCode": "NZAKL", "countryID": "NZ"},
    "TOKYO": {"locationCode": "JPTYO", "countryID": "JP"},
    "HO CHI MINH": {"locationCode": "VNSGN", "countryID": "VN"},
    "MUMBAI": {"locationCode": "INBOM", "countryID": "IN"},
    "PRAGUE": {"locationCode": "CZPRG", "countryID": "CZ"},  # Use Hamburg port for Prague
    "SINGAPORE": {"locationCode": "SGSIN", "countryID": "SG"},
    "BUENOS AIRES": {"locationCode": "ARBUE", "countryID": "AR"},
    "LIMA": {"locationCode": "PELIM", "countryID": "PE"},
    "ISLAMABAD": {"locationCode": "PKKAR", "countryID": "PK"},  # Use Karachi port for Islamabad
    "BANGKOK": {"locationCode": "THBKK", "countryID": "TH"},
    "VANCOUVER": {"locationCode": "CAVAN", "countryID": "CA"},
    "LISBON": {"locationCode": "PTLIS", "countryID": "PT"},
    "MONTREAL": {"locationCode": "CAMTR", "countryID": "CA"},
    "MADRID": {"locationCode": "ESMAD", "countryID": "ES"},  # Use Valencia port for Madrid
    "HELSINKI": {"locationCode": "FIHEL", "countryID": "FI"},
    "KUALA LUMPUR": {"locationCode": "MYKUL", "countryID": "MY"},
    "PUNE": {"locationCode": "INBOM", "countryID": "IN"},  # Use Mumbai port for Pune
    "ATHENS": {"locationCode": "GRPIR", "countryID": "GR"},  # Use Piraeus port for Athens
    "AARHUS": {"locationCode": "DKAAR", "countryID": "DK"},
    "OSLO": {"locationCode": "NOOSL", "countryID": "NO"},
    "KYIV": {"locationCode": "UAODS", "countryID": "UA"},  # Use Odessa port for Kyiv
    "SARAJEVO": {"locationCode": "BASJJ", "countryID": "BA"},  # Use Rijeka port for Sarajevo
    "NOUMEA": {"locationCode": "NCNOU", "countryID": "NC"},  # Use Sydney port for Noumea
    "HERZLIYA": {"locationCode": "ILHFA", "countryID": "IL"},  # Use Haifa port for Herzliya
    "TBILISI": {"locationCode": "TRIST", "countryID": "GE"},  # Use Istanbul port for Tbilisi (no valid GE ports)
    "DUBLIN": {"locationCode": "IEDUB", "countryID": "IE"},
    "MANAGUA": {"locationCode": "NIMGA", "countryID": "NI"},  # Use Miami port for Managua (no valid NI ports)
    "SAN JOSE": {"locationCode": "USMIA", "countryID": "CR"},  # Use Miami port for San Jose (no valid CR ports)
    "CALGARY": {"locationCode": "CACAL", "countryID": "CA"},  # Use Vancouver port for Calgary
    "SAO PAULO": {"locationCode": "BRSSZ", "countryID": "BR"},  # Use Santos port for Sao Paulo
    "SANTO DOMINGO": {"locationCode": "DOSDQ", "countryID": "DO"},  # Use Miami port for Santo Domingo
    "BELMOPAN": {"locationCode": "BZBZE", "countryID": "BZ"},  # Use Miami port for Belmopan
    "LJUBLJANA": {"locationCode": "SILJU", "countryID": "SI"},
    "BRASTISLAVA": {"locationCode": "SKBTS", "countryID": "SK"},
    "PLANO": {"locationCode": "USHOU", "countryID": "US"},  # Use Houston port for Plano
    "AMSTERDAM": {"locationCode": "NLAMS", "countryID": "NL"},
    "BEOGRAD": {"locationCode": "RSBEG", "countryID": "RS"},  # Use Constanta port for Belgrade
    "CHISINAU": {"locationCode": "ROBCT", "countryID": "MD"},  # Use Constanta port for Chisinau
    "SOFIA": {"locationCode": "BGSOF", "countryID": "BG"},  # Use Varna port for Sofia
    "BUCHAREST": {"locationCode": "ROBUH", "countryID": "RO"},  # Use Constanta port for Bucharest
    "WARSAW": {"locationCode": "PLWAW", "countryID": "PL"},  # Use Gdansk port for Warsaw
    "AMMAN": {"locationCode": "JOAQJ", "countryID": "JO"},  # Use Aqaba port for Amman
    "BRUSSELS": {"locationCode": "BEANR", "countryID": "BE"},  # Use Antwerp port for Brussels
    "NICOSIA": {"locationCode": "CYLIM", "countryID": "CY"},  # Use Limassol port for Nicosia
    "ZAGREB": {"locationCode": "HRRJK", "countryID": "HR"},  # Use Rijeka port for Zagreb
    "BUDAPEST": {"locationCode": "HUBUD", "countryID": "HU"},  # Use Constanta port for Budapest
    "MANILA": {"locationCode": "PHMNL", "countryID": "PH"},  # Use Manila port for Manila
    "YEREVAN": {"locationCode": "AMYER", "countryID": "AM"},  # Use Yerevan port for Yerevan
    "MINSK": {"locationCode": "BYMNS", "countryID": "BY"},  # Use Minsk port for Minsk
    "MOSCOW": {"locationCode": "RUMOW", "countryID": "RU"},  # Use Moscow port for Moscow
} 