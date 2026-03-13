# Risk Global 🌍

A rebalanced global Risk game built with Flask and Python. Featuring fair global territory distribution across 54 territories and 9 continents.

## Quick Start

```bash
# Install dependencies
pip install flask

# Run the game
python app.py

# Open in browser
http://localhost:5000
```

## Game Features

- **54 territories** across 9 continents (vs 42 in classic Risk)
- **Fair global distribution** — Asia, Africa, Middle East, and South/Southeast Asia all get proper representation
- **1 Human vs 2–10 AI opponents**
- **Full Risk rules**: Reinforce → Attack (dice) → Fortify
- **Card trading** for bonus armies
- **Continent bonuses** for holding complete continents
- **Interactive SVG world map** with territory circles and connections

## Continents & Bonuses

| Continent | Territories | Bonus |
|-----------|-------------|-------|
| North America | 10 | +5 |
| South America | 5 | +3 |
| Europe | 8 | +5 |
| Africa | 6 | +3 |
| Middle East & Central Asia | 5 | +3 |
| South & Southeast Asia | 6 | +4 |
| East Asia | 6 | +4 |
| Russia & North Asia | 5 | +4 |
| Oceania | 3 | +2 |

## File Structure

```
risk_global/
├── app.py           # Flask server & routes
├── game_logic.py    # Core game engine
├── game_data.py     # Territories, continents, adjacencies
├── requirements.txt
└── templates/
    ├── index.html   # Setup screen
    └── game.html    # Game board
```
