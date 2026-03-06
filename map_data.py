"""
Balanced World Risk Map - Equal representation across all regions.
Unlike traditional Risk, this map gives fair territory counts to all major civilizations.
"""

CONTINENTS = {
    "North America": {
        "bonus": 5,
        "color": "#2E86AB",
        "territories": [
            "Alaska", "Yukon", "Northwest Canada", "Ontario", "Quebec",
            "British Columbia", "Alberta", "Great Plains", "Great Lakes",
            "New England", "California", "Southwest USA", "Southeast USA",
            "Texas", "Mexico North", "Mexico South", "Central America", "Caribbean"
        ]
    },
    "South America": {
        "bonus": 4,
        "color": "#A23B72",
        "territories": [
            "Colombia", "Venezuela", "Guyana", "Ecuador", "Peru",
            "Brazil North", "Brazil Central", "Brazil South", "Bolivia",
            "Paraguay", "Chile North", "Chile South", "Argentina North", "Argentina South", "Uruguay"
        ]
    },
    "Europe": {
        "bonus": 5,
        "color": "#F18F01",
        "territories": [
            "Iceland", "Scotland", "Ireland", "England", "Scandinavia",
            "Finland", "Baltic States", "Poland", "Germany", "Netherlands",
            "France", "Iberia", "Italy", "Austria", "Balkans",
            "Ukraine West", "Romania", "Greece", "Turkey"
        ]
    },
    "Africa": {
        "bonus": 4,
        "color": "#C73E1D",
        "territories": [
            "Morocco", "Algeria", "Libya", "Egypt", "West Africa",
            "Mali", "Sudan", "Ethiopia", "Nigeria", "Congo",
            "Tanzania", "Angola", "Mozambique", "Zimbabwe", "Botswana",
            "South Africa", "Madagascar"
        ]
    },
    "Middle East & Central Asia": {
        "bonus": 4,
        "color": "#D4A017",
        "territories": [
            "Turkey East", "Lebanon Syria", "Israel Jordan", "Iraq", "Iran West",
            "Iran East", "Saudi Arabia", "Yemen", "Oman UAE", "Afghanistan",
            "Pakistan", "Kazakhstan", "Uzbekistan", "Turkmenistan", "Kyrgyzstan"
        ]
    },
    "Asia": {
        "bonus": 7,
        "color": "#3B1F2B",
        "territories": [
            "Russia West", "Russia Central", "Russia East", "Siberia", "Russia Far East",
            "India North", "India South", "India East", "Sri Lanka",
            "China North", "China Central", "China South", "China East", "Tibet",
            "Mongolia", "Manchuria", "Korea", "Japan North", "Japan South",
            "Taiwan", "Vietnam", "Thailand", "Myanmar", "Laos Cambodia",
            "Malaysia", "Philippines", "Indonesia West", "Indonesia East"
        ]
    },
    "Oceania": {
        "bonus": 3,
        "color": "#44BBA4",
        "territories": [
            "Western Australia", "Northern Territory", "Queensland",
            "New South Wales", "Victoria", "South Australia",
            "New Zealand North", "New Zealand South",
            "Papua New Guinea", "Melanesia", "Polynesia"
        ]
    }
}

# Define adjacency (borders) between territories
ADJACENCY = {
    # North America internal
    "Alaska": ["Yukon", "British Columbia", "Russia Far East"],
    "Yukon": ["Alaska", "Northwest Canada", "British Columbia"],
    "Northwest Canada": ["Yukon", "Alberta", "Ontario"],
    "Ontario": ["Northwest Canada", "Alberta", "Great Lakes", "Quebec", "Great Plains"],
    "Quebec": ["Ontario", "Great Lakes", "New England"],
    "British Columbia": ["Alaska", "Yukon", "Alberta", "California"],
    "Alberta": ["British Columbia", "Yukon", "Northwest Canada", "Ontario", "Great Plains"],
    "Great Plains": ["Alberta", "Ontario", "Great Lakes", "Southwest USA", "Texas"],
    "Great Lakes": ["Ontario", "Quebec", "Great Plains", "New England", "Southeast USA", "Texas"],
    "New England": ["Quebec", "Great Lakes", "Southeast USA"],
    "California": ["British Columbia", "Southwest USA"],
    "Southwest USA": ["California", "Great Plains", "Texas", "Mexico North"],
    "Southeast USA": ["Great Lakes", "New England", "Texas", "Caribbean"],
    "Texas": ["Southwest USA", "Great Plains", "Great Lakes", "Southeast USA", "Mexico North"],
    "Mexico North": ["Southwest USA", "Texas", "Mexico South"],
    "Mexico South": ["Mexico North", "Central America"],
    "Central America": ["Mexico South", "Colombia", "Caribbean"],
    "Caribbean": ["Southeast USA", "Central America", "Venezuela", "Colombia"],

    # South America internal
    "Colombia": ["Central America", "Caribbean", "Venezuela", "Ecuador", "Peru"],
    "Venezuela": ["Colombia", "Caribbean", "Guyana", "Brazil North"],
    "Guyana": ["Venezuela", "Brazil North"],
    "Ecuador": ["Colombia", "Peru"],
    "Peru": ["Colombia", "Ecuador", "Bolivia", "Brazil Central", "Chile North"],
    "Brazil North": ["Venezuela", "Guyana", "Brazil Central", "Colombia"],
    "Brazil Central": ["Brazil North", "Peru", "Bolivia", "Brazil South", "Paraguay"],
    "Brazil South": ["Brazil Central", "Paraguay", "Uruguay", "Argentina North"],
    "Bolivia": ["Peru", "Brazil Central", "Paraguay", "Argentina North", "Chile North"],
    "Paraguay": ["Brazil Central", "Brazil South", "Bolivia", "Argentina North"],
    "Chile North": ["Peru", "Bolivia", "Chile South", "Argentina North"],
    "Chile South": ["Chile North", "Argentina South"],
    "Argentina North": ["Bolivia", "Paraguay", "Brazil South", "Chile North", "Argentina South", "Uruguay"],
    "Argentina South": ["Argentina North", "Chile South"],
    "Uruguay": ["Brazil South", "Argentina North"],

    # Europe internal
    "Iceland": ["Scotland", "England"],
    "Scotland": ["Iceland", "Ireland", "England", "Scandinavia"],
    "Ireland": ["Scotland", "England"],
    "England": ["Iceland", "Scotland", "Ireland", "Netherlands", "France"],
    "Scandinavia": ["Scotland", "Finland", "Baltic States", "Germany"],
    "Finland": ["Scandinavia", "Baltic States", "Ukraine West"],
    "Baltic States": ["Scandinavia", "Finland", "Poland", "Ukraine West"],
    "Poland": ["Baltic States", "Germany", "Austria", "Ukraine West", "Romania"],
    "Germany": ["Scandinavia", "Netherlands", "France", "Austria", "Poland"],
    "Netherlands": ["England", "Germany", "France"],
    "France": ["England", "Netherlands", "Germany", "Iberia", "Italy", "Austria"],
    "Iberia": ["France", "Morocco"],
    "Italy": ["France", "Austria", "Balkans", "Greece"],
    "Austria": ["Germany", "France", "Poland", "Romania", "Balkans", "Italy"],
    "Balkans": ["Austria", "Italy", "Romania", "Greece", "Turkey"],
    "Ukraine West": ["Finland", "Baltic States", "Poland", "Romania", "Russia West"],
    "Romania": ["Poland", "Austria", "Balkans", "Ukraine West", "Turkey East"],
    "Greece": ["Italy", "Balkans", "Turkey", "Lebanon Syria"],
    "Turkey": ["Balkans", "Greece", "Turkey East", "Romania"],

    # Africa internal
    "Morocco": ["Iberia", "Algeria", "West Africa", "Mali"],
    "Algeria": ["Morocco", "Libya", "Mali", "West Africa"],
    "Libya": ["Algeria", "Egypt", "Sudan", "Mali"],
    "Egypt": ["Libya", "Sudan", "Israel Jordan", "Lebanon Syria"],
    "West Africa": ["Morocco", "Algeria", "Mali", "Nigeria", "Congo"],
    "Mali": ["Morocco", "Algeria", "Libya", "West Africa", "Nigeria", "Sudan"],
    "Sudan": ["Libya", "Egypt", "Mali", "Nigeria", "Ethiopia", "Congo"],
    "Ethiopia": ["Sudan", "Nigeria", "Congo", "Tanzania", "Oman UAE"],
    "Nigeria": ["West Africa", "Mali", "Sudan", "Ethiopia", "Congo"],
    "Congo": ["West Africa", "Nigeria", "Sudan", "Ethiopia", "Tanzania", "Angola", "Zimbabwe"],
    "Tanzania": ["Congo", "Ethiopia", "Angola", "Mozambique", "Zimbabwe"],
    "Angola": ["Congo", "Tanzania", "Zimbabwe", "Botswana"],
    "Mozambique": ["Tanzania", "Zimbabwe", "South Africa"],
    "Zimbabwe": ["Congo", "Tanzania", "Angola", "Botswana", "Mozambique", "South Africa"],
    "Botswana": ["Angola", "Zimbabwe", "South Africa"],
    "South Africa": ["Botswana", "Zimbabwe", "Mozambique"],
    "Madagascar": ["Mozambique", "South Africa"],

    # Middle East & Central Asia
    "Turkey East": ["Turkey", "Romania", "Lebanon Syria", "Iraq", "Iran West", "Kazakhstan"],
    "Lebanon Syria": ["Turkey East", "Greece", "Egypt", "Israel Jordan", "Iraq"],
    "Israel Jordan": ["Lebanon Syria", "Egypt", "Iraq", "Saudi Arabia"],
    "Iraq": ["Turkey East", "Lebanon Syria", "Israel Jordan", "Iran West", "Saudi Arabia", "Kuwait"],
    "Iran West": ["Turkey East", "Iraq", "Saudi Arabia", "Afghanistan", "Iran East"],
    "Iran East": ["Iran West", "Afghanistan", "Pakistan", "Turkmenistan"],
    "Saudi Arabia": ["Israel Jordan", "Iraq", "Iran West", "Yemen", "Oman UAE"],
    "Yemen": ["Saudi Arabia", "Oman UAE", "Ethiopia"],
    "Oman UAE": ["Saudi Arabia", "Yemen", "Iran East", "Ethiopia"],
    "Afghanistan": ["Iran West", "Iran East", "Pakistan", "Uzbekistan", "Kyrgyzstan", "China North"],
    "Pakistan": ["Iran East", "Afghanistan", "India North", "India East"],
    "Kazakhstan": ["Turkey East", "Russia West", "Uzbekistan", "Kyrgyzstan", "China North", "Russia Central"],
    "Uzbekistan": ["Kazakhstan", "Afghanistan", "Turkmenistan", "Kyrgyzstan"],
    "Turkmenistan": ["Iran East", "Uzbekistan", "Kazakhstan"],
    "Kyrgyzstan": ["Kazakhstan", "Uzbekistan", "Afghanistan", "China North"],

    # Asia internal
    "Russia West": ["Ukraine West", "Finland", "Kazakhstan", "Russia Central"],
    "Russia Central": ["Russia West", "Kazakhstan", "Kyrgyzstan", "Mongolia", "Siberia"],
    "Russia East": ["Siberia", "Russia Far East", "Manchuria"],
    "Siberia": ["Russia Central", "Mongolia", "Russia East"],
    "Russia Far East": ["Russia East", "Alaska", "Japan North", "Manchuria"],
    "India North": ["Pakistan", "Afghanistan", "Tibet", "India East", "India South"],
    "India South": ["India North", "India East", "Sri Lanka"],
    "India East": ["Pakistan", "India North", "India South", "Tibet", "Myanmar", "Bangladesh"],
    "Sri Lanka": ["India South"],
    "China North": ["Kazakhstan", "Kyrgyzstan", "Afghanistan", "Mongolia", "Tibet", "China Central"],
    "China Central": ["China North", "Tibet", "China South", "China East", "Manchuria"],
    "China South": ["China Central", "Tibet", "Vietnam", "Laos Cambodia", "Myanmar"],
    "China East": ["China Central", "China South", "Manchuria", "Korea", "Taiwan"],
    "Tibet": ["India North", "India East", "China North", "China Central", "China South", "Myanmar"],
    "Mongolia": ["Russia Central", "Siberia", "China North", "Manchuria"],
    "Manchuria": ["Russia East", "Russia Far East", "Mongolia", "China Central", "China East", "Korea"],
    "Korea": ["Manchuria", "China East", "Japan North"],
    "Japan North": ["Russia Far East", "Korea", "Japan South"],
    "Japan South": ["Japan North", "Taiwan"],
    "Taiwan": ["China East", "Japan South", "Philippines"],
    "Vietnam": ["China South", "Laos Cambodia", "Thailand"],
    "Thailand": ["Vietnam", "Laos Cambodia", "Myanmar", "Malaysia"],
    "Myanmar": ["India East", "Tibet", "China South", "Thailand", "Laos Cambodia"],
    "Laos Cambodia": ["China South", "Vietnam", "Thailand", "Myanmar", "Malaysia"],
    "Malaysia": ["Thailand", "Laos Cambodia", "Indonesia West", "Philippines"],
    "Philippines": ["Taiwan", "Malaysia", "Indonesia West"],
    "Indonesia West": ["Malaysia", "Philippines", "Indonesia East", "Papua New Guinea"],
    "Indonesia East": ["Indonesia West", "Papua New Guinea", "Western Australia"],

    # Oceania internal
    "Western Australia": ["Indonesia East", "Northern Territory", "South Australia"],
    "Northern Territory": ["Western Australia", "Queensland", "South Australia"],
    "Queensland": ["Northern Territory", "New South Wales", "Papua New Guinea"],
    "New South Wales": ["Queensland", "Victoria", "South Australia"],
    "Victoria": ["New South Wales", "South Australia"],
    "South Australia": ["Western Australia", "Northern Territory", "New South Wales", "Victoria"],
    "New Zealand North": ["New Zealand South", "Polynesia"],
    "New Zealand South": ["New Zealand North"],
    "Papua New Guinea": ["Indonesia West", "Queensland", "Melanesia"],
    "Melanesia": ["Papua New Guinea", "Polynesia"],
    "Polynesia": ["Melanesia", "New Zealand North"],
}

# Build flat territory list
ALL_TERRITORIES = []
TERRITORY_TO_CONTINENT = {}
for continent, data in CONTINENTS.items():
    for t in data["territories"]:
        ALL_TERRITORIES.append(t)
        TERRITORY_TO_CONTINENT[t] = continent

def get_continent_bonus(continent_name, owned_territories):
    """Return continent bonus if player owns all territories."""
    cont = CONTINENTS[continent_name]
    if all(t in owned_territories for t in cont["territories"]):
        return cont["bonus"]
    return 0

def calculate_reinforcements(territories_owned):
    """Calculate how many troops a player gets per turn."""
    base = max(3, len(territories_owned) // 3)
    bonus = 0
    owned_set = set(territories_owned)
    for continent, data in CONTINENTS.items():
        if all(t in owned_set for t in data["territories"]):
            bonus += data["bonus"]
    return base + bonus
