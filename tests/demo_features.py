#!/usr/bin/env python3
"""
Demonstration script for LOGDTW2002 enhanced features
Shows the trading system, travel system, and map functionality
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "game"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from game.player import Player
from game.world import World
from game.trading import TradingSystem
from utils.display import DisplayManager


def demo_trading_system():
    """Demonstrate the enhanced trading system"""
    print("\n" + "=" * 60)
    print("TRADING SYSTEM DEMONSTRATION")
    print("=" * 60)

    # Initialize systems
    player = Player("Demo Trader")
    trading = TradingSystem()
    display = DisplayManager()

    # Show player starting status
    print(f"\nPlayer: {player.name}")
    print(f"Credits: {player.credits}")
    print(f"Fuel: {player.fuel}")

    # Show market at Earth Station
    print("\n" + "-" * 40)
    print("MARKET AT EARTH STATION")
    print("-" * 40)
    market_info = trading.get_market_info("Earth Station")
    display.show_market_info(market_info)

    # Demonstrate buying
    print("\n" + "-" * 40)
    print("BUYING COMPUTER CHIPS")
    print("-" * 40)
    result = trading.buy_item(player, "Earth Station", "Computer Chips", 2)
    print(f"Result: {result['message']}")
    print(f"Credits remaining: {player.credits}")

    # Show trade history
    print("\n" + "-" * 40)
    print("TRADE HISTORY")
    print("-" * 40)
    history = trading.get_trade_history()
    display.show_trade_history(history)

    # Show best trade routes
    print("\n" + "-" * 40)
    print("BEST TRADE ROUTES")
    print("-" * 40)
    routes = trading.get_best_trade_routes(player)
    for i, route in enumerate(routes, 1):
        print(f"{i}. {route['item']}")
        print(f"   Buy at {route['buy_location']}: {route['buy_price']} credits")
        print(f"   Sell at {route['sell_location']}: {route['sell_price']} credits")
        print(f"   Profit: {route['profit']} credits ({route['profit_margin']:.1f}%)")


def demo_travel_system():
    """Demonstrate the enhanced travel system"""
    print("\n" + "=" * 60)
    print("TRAVEL SYSTEM DEMONSTRATION")
    print("=" * 60)

    # Initialize systems
    player = Player("Demo Traveler")
    world = World()
    display = DisplayManager()

    # Show current location
    print(f"\nCurrent Location: {world.current_location}")
    print(f"Player Fuel: {player.fuel}")

    # Show available destinations
    print("\n" + "-" * 40)
    print("AVAILABLE DESTINATIONS")
    print("-" * 40)
    destinations = world.get_available_destinations()
    for dest in destinations:
        travel_info = world.get_travel_info(dest)
        print(f"\n{dest}:")
        print(f"  Fuel Cost: {travel_info['fuel_cost']}")
        print(f"  Travel Time: {travel_info['travel_time']} minutes")
        print(f"  Danger Level: {travel_info['danger_level']}/10")
        print(f"  Faction: {travel_info['faction']}")

    # Show map
    print("\n" + "-" * 40)
    print("SPACE MAP")
    print("-" * 40)
    print(world.get_map_display())

    # Demonstrate travel to Mars Colony
    print("\n" + "-" * 40)
    print("TRAVELING TO MARS COLONY")
    print("-" * 40)
    travel_result = world.start_travel("Mars Colony", player)
    print(f"Travel Result: {travel_result['message']}")

    # Show travel progress (simulated)
    print("\nTravel Progress:")
    for i in range(5):
        travel_status = world.update_travel(player)
        if travel_status.get("arrived"):
            print(f"✓ Arrived at {travel_status['destination']}!")
            break
        else:
            print(
                f"Progress: {travel_status['progress']:.1f}% - {travel_status['remaining_time']:.1f} minutes remaining"
            )

    # Show new location
    print(f"\nNew Location: {world.current_location}")
    print(f"Remaining Fuel: {player.fuel}")


def demo_enhanced_features():
    """Demonstrate all enhanced features"""
    print("\n" + "=" * 60)
    print("LOGDTW2002 - ENHANCED FEATURES DEMO")
    print("=" * 60)

    print("\nThis demonstration shows the enhanced trading and travel systems:")
    print("• Dynamic market prices with specializations")
    print("• Trade history and best trade routes")
    print("• Fuel-based travel with time requirements")
    print("• Visual space map with connections")
    print("• Travel progress tracking")

    # Run demonstrations
    demo_trading_system()
    demo_travel_system()

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nTo play the full game, run: python main.py")
    print("The game now includes:")
    print("• Enhanced trading with market specializations")
    print("• Trade history and route optimization")
    print("• Realistic travel with fuel costs and time")
    print("• Visual map system")
    print("• Progress tracking for all activities")


if __name__ == "__main__":
    demo_enhanced_features()
