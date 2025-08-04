# LOGDTW2002 - Legend of the Green Dragon meets TW2002

A text-based adventure game that combines the RPG elements of Legend of the Green Dragon with the space exploration and resource management of TW2002.

## Features

- **Character Progression**: Level up, gain experience, and improve your skills
- **Combat System**: Turn-based combat with various weapons and abilities
- **Space Exploration**: Navigate through different sectors and planets
- **Resource Management**: Manage credits, fuel, and supplies
- **Trading System**: Buy and sell goods between planets
- **Quest System**: Complete missions and earn rewards
- **ASCII Art**: Beautiful text-based graphics and animations

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Game Controls

- **Movement**: Use cardinal directions (north, south, east, west) or shortcuts (n, s, e, w)
- **Actions**: Type commands like "look", "inventory", "status", "help"
- **Combat**: Use "attack", "defend", "use [item]", "flee"
- **Trading**: Use "buy", "sell", "trade"
- **Navigation**: Use "travel", "land", "takeoff"

## Game Structure

- `main.py` - Main game entry point
- `game/` - Core game modules
  - `player.py` - Player character and stats
  - `world.py` - Game world and locations
  - `combat.py` - Combat system
  - `trading.py` - Trading and economy system
  - `quests.py` - Quest and mission system
- `data/` - Game data files
- `utils/` - Utility functions and helpers

## Contributing

Feel free to contribute by adding new features, fixing bugs, or improving the game mechanics!

## License

MIT License - feel free to use and modify as you wish.