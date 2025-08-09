# LOGDTW2002 - Game Guide

## Overview

LOGDTW2002 is a text-based adventure game that combines the RPG elements of Legend of the Green Dragon with the space exploration and resource management of TW2002. You play as a space adventurer exploring the galaxy, trading goods, fighting enemies, and completing quests.

## Getting Started

### Installation

1. **Clone or download the game files**
2. **Install Python 3.7+** (if not already installed)
3. **Run the game:**
   ```bash
   # Option 1: Use the startup script
   python run_game.py
   
   # Option 2: Manual setup
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

### First Steps

1. **Start the game** and you'll see the title screen
2. **Choose "Start New Game"** from the main menu
3. **Explore Earth Station** - your starting location
4. **Type "help"** to see all available commands

## Game Features

### Character Progression

- **Level System**: Gain experience through combat, quests, and exploration
- **Skills**: Improve combat, pilot, trading, engineering, navigation, and diplomacy
- **Stats**: Strength, Agility, Endurance, Intelligence, Charisma, Perception
- **Equipment**: Weapons, armor, shields, and special items

### Space Exploration

- **8 Unique Locations**: From Earth Station to the mysterious Outer Rim
- **Travel System**: Navigate between locations using the travel command
- **Danger Levels**: Each location has a risk rating (1-10)
- **Factions**: Different locations are controlled by various factions

### Combat System

- **Turn-based Combat**: Strategic battles with enemies
- **Multiple Enemy Types**: Pirates, aliens, robots, and space creatures
- **Weapon System**: Different weapons with varying damage
- **Defense Mechanics**: Armor and shields provide protection
- **Item Usage**: Use consumables during combat

### Trading & Economy

- **Dynamic Markets**: Prices vary by location and specialization
- **Trade Goods**: Minerals, technology, luxury items, food, and medical supplies
- **Supply & Demand**: Buy low, sell high for profit
- **Market Specializations**: Each location specializes in different goods

### Quest System

- **Multiple Quest Types**: Delivery, combat, trading, exploration, mining, diplomacy
- **Requirements**: Level, skills, and credits needed for different quests
- **Rewards**: Experience, credits, reputation, and items
- **Faction Reputation**: Build relationships with different groups

## Game Locations

### Earth Station
- **Type**: Space Station
- **Danger Level**: 1/10
- **Services**: Trading, Repair, Fuel, Missions
- **Specialization**: Technology
- **Connections**: Mars Colony, Luna Base

### Mars Colony
- **Type**: Planet
- **Danger Level**: 3/10
- **Services**: Trading, Mining, Fuel
- **Specialization**: Minerals
- **Connections**: Earth Station, Asteroid Belt

### Luna Base
- **Type**: Moon Base
- **Danger Level**: 2/10
- **Services**: Research, Trading, Fuel
- **Specialization**: Research
- **Connections**: Earth Station, Deep Space Lab

### Asteroid Belt
- **Type**: Asteroid Field
- **Danger Level**: 7/10
- **Services**: Mining
- **Specialization**: None
- **Connections**: Mars Colony, Pirate Haven

### Pirate Haven
- **Type**: Space Station
- **Danger Level**: 9/10
- **Services**: Trading, Repair, Missions
- **Specialization**: Luxury
- **Connections**: Asteroid Belt, Outer Rim

### Deep Space Lab
- **Type**: Research Station
- **Danger Level**: 4/10
- **Services**: Research, Fuel
- **Specialization**: Technology
- **Connections**: Luna Base, Nebula Zone

### Outer Rim
- **Type**: Deep Space
- **Danger Level**: 10/10
- **Services**: Exploration
- **Specialization**: None
- **Connections**: Pirate Haven

### Nebula Zone
- **Type**: Nebula
- **Danger Level**: 6/10
- **Services**: Exploration, Research
- **Specialization**: None
- **Connections**: Deep Space Lab

## Commands Reference

### Movement
- `north`, `south`, `east`, `west` (or `n`, `s`, `e`, `w`)
- `up`, `down`, `in`, `out`

### Actions
- `look` - Examine your surroundings
- `inventory` (or `inv`, `i`) - Show your inventory
- `status` (or `stats`, `s`) - Show your status
- `take [item]` - Pick up an item
- `drop [item]` - Drop an item
- `use [item]` - Use an item

### Combat
- `attack` - Attack an enemy
- `defend` - Take defensive stance
- `flee` - Attempt to flee from combat

### Space Travel
- `travel [destination]` - Travel to another location
- `land` - Land on a planet
- `takeoff` - Leave a planet

### Trading
- `buy [item] [quantity]` - Buy items from market
- `sell [item] [quantity]` - Sell items to market
- `market` - Show market information

### System
- `help` (or `h`) - Show help
- `quit` (or `q`, `exit`) - Exit the game

### Special
- `quests` - Show available quests
- `skills` - Show your skills
- `equipment` - Show equipped items

## Tips for Success

### Starting Out
1. **Explore Earth Station** - Get familiar with the interface
2. **Check your inventory** - See what starting equipment you have
3. **Look around** - Examine your surroundings for items and information
4. **Talk to NPCs** - Some locations have characters with quests

### Making Money
1. **Trade between locations** - Buy low, sell high
2. **Complete quests** - Earn credits and experience
3. **Fight enemies** - Defeat enemies for loot and credits
4. **Mine resources** - Extract valuable minerals from asteroids

### Combat Strategy
1. **Equip the best weapons** - Higher damage means faster victories
2. **Use consumables** - Med kits and energy cells can save your life
3. **Defend when needed** - Sometimes it's better to defend than attack
4. **Flee if necessary** - Live to fight another day

### Exploration
1. **Visit all locations** - Each has unique items and opportunities
2. **Check danger levels** - Higher danger means better rewards but more risk
3. **Build reputation** - Different factions offer different benefits
4. **Complete quests** - They often lead to new areas and rewards

## Game Mechanics

### Experience & Leveling
- Gain experience through combat, quests, and exploration
- Each level increases your stats and unlocks new abilities
- Experience requirements increase with each level

### Skills
- **Combat**: Increases damage and combat effectiveness
- **Pilot**: Improves ship handling and travel efficiency
- **Trading**: Better prices and more trading opportunities
- **Engineering**: Ship repairs and upgrades
- **Navigation**: Better travel routes and exploration
- **Diplomacy**: Better relations with factions

### Inventory Management
- Limited inventory space (50 items maximum)
- Items have different types: weapons, armor, consumables, trade goods
- Equip weapons and armor for combat bonuses
- Use consumables for healing and energy restoration

### Ship System
- Your ship has cargo capacity, fuel efficiency, and weapon slots
- Fuel is consumed during travel
- Ship can be upgraded with better components

### Faction Reputation
- **Federation**: Government and military
- **Pirates**: Lawless space dwellers
- **Traders**: Merchant guilds
- **Scientists**: Research organizations

## Troubleshooting

### Common Issues
1. **Game won't start**: Make sure Python 3.7+ is installed
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Virtual environment issues**: Delete `venv` folder and recreate
4. **Display problems**: Try running in a different terminal

### Getting Help
- Type `help` in the game for command reference
- Check the console output for error messages
- Use `status` to check your current state
- Use `look` to examine your surroundings

## Advanced Features

### Quest Types
- **Delivery**: Transport goods between locations
- **Combat**: Defeat specific enemies or clear areas
- **Trading**: Buy and sell for profit
- **Exploration**: Visit new areas and gather data
- **Mining**: Extract resources from asteroids
- **Diplomacy**: Negotiate with factions

### Enemy Types
- **Space Pirates**: Aggressive human enemies
- **Alien Raiders**: Mysterious alien threats
- **Security Drones**: Automated defense systems
- **Space Creatures**: Massive space-dwelling beasts

### Market Dynamics
- Prices fluctuate based on location and demand
- Specialized locations offer better prices for certain goods
- Supply and demand affect profitability
- Some items are only available at specific locations

## Credits

LOGDTW2002 combines elements from:
- **Legend of the Green Dragon**: RPG progression and character development
- **TW2002**: Space exploration and resource management
- **Classic Text Adventures**: Interactive storytelling and exploration

Enjoy your journey through the stars! 🚀 