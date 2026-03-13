# Risk_Global - Fair Global Distribution
# ~50 territories (vs 42 in classic Risk) with balanced regional representation

CONTINENTS = {
    "North America": {
        "bonus": 5,
        "color": "#E8A838",
        "territories": [
            "Alaska", "Western Canada", "Eastern Canada", "Quebec",
            "Pacific Northwest", "Great Plains", "Eastern USA", "Southern USA",
            "Mexico", "Central America"
        ]
    },
    "South America": {
        "bonus": 3,
        "color": "#44AA44",
        "territories": [
            "Venezuela & Colombia", "Brazil North", "Brazil South",
            "Peru & Bolivia", "Argentina & Chile"
        ]
    },
    "Europe": {
        "bonus": 5,
        "color": "#4488CC",
        "territories": [
            "Iceland", "British Isles", "Scandinavia", "Western Europe",
            "Central Europe", "Southern Europe", "Eastern Europe", "Ukraine & Caucasus"
        ]
    },
    "Africa": {
        "bonus": 3,
        "color": "#CC8844",
        "territories": [
            "North Africa", "West Africa", "Central Africa",
            "East Africa", "South Africa", "Madagascar"
        ]
    },
    "Middle East & Central Asia": {
        "bonus": 3,
        "color": "#CC6644",
        "territories": [
            "Turkey & Levant", "Arabian Peninsula", "Iran & Iraq",
            "Central Asia", "Afghanistan & Pakistan"
        ]
    },
    "South & Southeast Asia": {
        "bonus": 4,
        "color": "#8844CC",
        "territories": [
            "India", "Sri Lanka & South India", "Southeast Asia Mainland",
            "Indonesia & Malaysia", "Philippines", "Indochina"
        ]
    },
    "East Asia": {
        "bonus": 4,
        "color": "#CC4488",
        "territories": [
            "China North", "China South", "Manchuria & Korea",
            "Japan", "Mongolia & Siberia East", "Taiwan"
        ]
    },
    "Russia & North Asia": {
        "bonus": 4,
        "color": "#887755",
        "territories": [
            "Western Russia", "Siberia West", "Siberia Central",
            "Siberia East", "Kamchatka"
        ]
    },
    "Oceania": {
        "bonus": 2,
        "color": "#44AACC",
        "territories": [
            "Western Australia", "Eastern Australia", "New Zealand & Pacific"
        ]
    }
}

# All territories flat list
ALL_TERRITORIES = []
TERRITORY_TO_CONTINENT = {}
for cont, data in CONTINENTS.items():
    for t in data["territories"]:
        ALL_TERRITORIES.append(t)
        TERRITORY_TO_CONTINENT[t] = cont

# Adjacency graph
ADJACENCIES = {
    # North America
    "Alaska": ["Western Canada", "Pacific Northwest", "Kamchatka"],
    "Western Canada": ["Alaska", "Pacific Northwest", "Great Plains", "Eastern Canada"],
    "Eastern Canada": ["Western Canada", "Quebec", "Eastern USA"],
    "Quebec": ["Eastern Canada", "Eastern USA"],
    "Pacific Northwest": ["Alaska", "Western Canada", "Great Plains", "Eastern USA"],
    "Great Plains": ["Western Canada", "Pacific Northwest", "Eastern USA", "Southern USA", "Mexico"],
    "Eastern USA": ["Eastern Canada", "Quebec", "Pacific Northwest", "Great Plains", "Southern USA"],
    "Southern USA": ["Great Plains", "Eastern USA", "Mexico"],
    "Mexico": ["Great Plains", "Southern USA", "Central America"],
    "Central America": ["Mexico", "Venezuela & Colombia"],

    # South America
    "Venezuela & Colombia": ["Central America", "Brazil North", "Peru & Bolivia"],
    "Brazil North": ["Venezuela & Colombia", "Brazil South", "Peru & Bolivia"],
    "Brazil South": ["Brazil North", "Peru & Bolivia", "Argentina & Chile"],
    "Peru & Bolivia": ["Venezuela & Colombia", "Brazil North", "Brazil South", "Argentina & Chile"],
    "Argentina & Chile": ["Brazil South", "Peru & Bolivia"],

    # Europe
    "Iceland": ["British Isles", "Scandinavia"],
    "British Isles": ["Iceland", "Scandinavia", "Western Europe", "Central Europe"],
    "Scandinavia": ["Iceland", "British Isles", "Central Europe", "Eastern Europe", "Western Russia"],
    "Western Europe": ["British Isles", "Central Europe", "Southern Europe", "North Africa"],
    "Central Europe": ["British Isles", "Scandinavia", "Western Europe", "Southern Europe", "Eastern Europe"],
    "Southern Europe": ["Western Europe", "Central Europe", "Eastern Europe", "Turkey & Levant", "North Africa"],
    "Eastern Europe": ["Scandinavia", "Central Europe", "Southern Europe", "Ukraine & Caucasus"],
    "Ukraine & Caucasus": ["Eastern Europe", "Western Russia", "Turkey & Levant", "Central Asia", "Iran & Iraq"],

    # Africa
    "North Africa": ["Western Europe", "Southern Europe", "West Africa", "Central Africa", "East Africa", "Arabian Peninsula"],
    "West Africa": ["North Africa", "Central Africa"],
    "Central Africa": ["North Africa", "West Africa", "East Africa", "South Africa"],
    "East Africa": ["North Africa", "Central Africa", "South Africa", "Madagascar", "Arabian Peninsula"],
    "South Africa": ["Central Africa", "East Africa", "Madagascar"],
    "Madagascar": ["East Africa", "South Africa"],

    # Middle East & Central Asia
    "Turkey & Levant": ["Southern Europe", "Ukraine & Caucasus", "Arabian Peninsula", "Iran & Iraq", "North Africa"],
    "Arabian Peninsula": ["Turkey & Levant", "Iran & Iraq", "North Africa", "East Africa"],
    "Iran & Iraq": ["Turkey & Levant", "Arabian Peninsula", "Ukraine & Caucasus", "Central Asia", "Afghanistan & Pakistan"],
    "Central Asia": ["Ukraine & Caucasus", "Iran & Iraq", "Afghanistan & Pakistan", "China North", "Mongolia & Siberia East", "Siberia West"],
    "Afghanistan & Pakistan": ["Iran & Iraq", "Central Asia", "India", "China North"],

    # South & Southeast Asia
    "India": ["Afghanistan & Pakistan", "China South", "Sri Lanka & South India", "Southeast Asia Mainland", "Indochina"],
    "Sri Lanka & South India": ["India"],
    "Southeast Asia Mainland": ["India", "Indochina", "Indonesia & Malaysia", "China South"],
    "Indonesia & Malaysia": ["Southeast Asia Mainland", "Indochina", "Philippines", "Western Australia"],
    "Philippines": ["Indonesia & Malaysia", "Taiwan", "Japan"],
    "Indochina": ["India", "Southeast Asia Mainland", "Indonesia & Malaysia", "China South", "Manchuria & Korea"],

    # East Asia
    "China North": ["Afghanistan & Pakistan", "Central Asia", "Mongolia & Siberia East", "Manchuria & Korea", "China South"],
    "China South": ["India", "China North", "Manchuria & Korea", "Southeast Asia Mainland", "Indochina", "Taiwan"],
    "Manchuria & Korea": ["China North", "China South", "Indochina", "Japan", "Siberia East"],
    "Japan": ["Manchuria & Korea", "Philippines", "Taiwan", "Siberia East"],
    "Mongolia & Siberia East": ["Central Asia", "China North", "Siberia Central", "Siberia East"],
    "Taiwan": ["China South", "Philippines", "Japan"],

    # Russia & North Asia
    "Western Russia": ["Scandinavia", "Ukraine & Caucasus", "Siberia West"],
    "Siberia West": ["Western Russia", "Central Asia", "Siberia Central"],
    "Siberia Central": ["Siberia West", "Mongolia & Siberia East", "Siberia East"],
    "Siberia East": ["Siberia Central", "Mongolia & Siberia East", "Manchuria & Korea", "Japan", "Kamchatka"],
    "Kamchatka": ["Alaska", "Siberia East"],

    # Oceania
    "Western Australia": ["Indonesia & Malaysia", "Eastern Australia"],
    "Eastern Australia": ["Western Australia", "New Zealand & Pacific"],
    "New Zealand & Pacific": ["Eastern Australia"],
}

PLAYER_COLORS = [
    "#E74C3C",  # Red
    "#3498DB",  # Blue
    "#2ECC71",  # Green
    "#F39C12",  # Orange
    "#9B59B6",  # Purple
    "#1ABC9C",  # Teal
    "#E67E22",  # Dark Orange
    "#2980B9",  # Dark Blue
    "#27AE60",  # Dark Green
    "#C0392B",  # Dark Red
    "#8E44AD",  # Dark Purple
]

AI_NAMES = [
    "General Chen", "Commander Volkov", "Admiral Okafor",
    "Marshal Santos", "General Müller", "Commander Ito",
    "Admiral Patel", "Marshal Al-Rashid", "General Osei", "Commander Torres"
]
