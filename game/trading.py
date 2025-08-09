"""
Trading system for LOGDTW2002
Handles economy, trading, and market mechanics
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from game.player import Player, Item
from game.dynamic_markets import DynamicMarketSystem

@dataclass
class TradeGood:
    """Represents a trade good with price variations"""
    name: str
    base_price: int
    description: str
    category: str  # minerals, technology, luxury, etc.
    weight: float = 1.0
    rarity: str = "common"  # common, uncommon, rare, legendary

class TradingSystem:
    """Handles trading and economy mechanics"""
    
    def __init__(self):
        # Dynamic market simulation
        self.market_system = DynamicMarketSystem()

        self.trade_goods = {}
        self.market_prices = {}
        self.location_markets = {}
        self.location_sectors = {}
        self.good_to_commodity = {}
        self.trade_history = []
        self.price_history = {}

        # Initialize trade goods and mapping to dynamic market commodities
        self._create_trade_goods()

        # Initialize markets/sector economies
        self._create_markets()

        # Initial price pull from dynamic market
        self._update_all_prices()
    
    def _create_trade_goods(self):
        """Create available trade goods"""
        goods_data = [
            # Minerals
            {'name': 'Iron Ore', 'base_price': 10, 'description': 'Basic raw material', 'category': 'minerals'},
            {'name': 'Gold', 'base_price': 100, 'description': 'Precious metal', 'category': 'minerals'},
            {'name': 'Platinum', 'base_price': 200, 'description': 'Rare industrial metal', 'category': 'minerals'},
            {'name': 'Uranium', 'base_price': 500, 'description': 'Radioactive material', 'category': 'minerals'},
            {'name': 'Raw Minerals', 'base_price': 20, 'description': 'Unprocessed ore', 'category': 'minerals'},
            {'name': 'Ammolite', 'base_price': 350, 'description': 'Rare iridescent gemstone prized by collectors and jewelers', 'category': 'minerals'},
            
            # Technology
            {'name': 'Computer Chips', 'base_price': 50, 'description': 'Electronic components', 'category': 'technology'},
            {'name': 'Quantum Processors', 'base_price': 250, 'description': 'Advanced computing units', 'category': 'technology'},
            {'name': 'Energy Cells', 'base_price': 25, 'description': 'Power storage units', 'category': 'technology'},
            {'name': 'Shield Generators', 'base_price': 300, 'description': 'Defensive technology', 'category': 'technology'},
            {'name': 'Quantum Scanner', 'base_price': 400, 'description': 'Advanced detection device', 'category': 'technology'},
            
            # Luxury Goods
            {'name': 'Space Wine', 'base_price': 150, 'description': 'Fine alcoholic beverage', 'category': 'luxury'},
            {'name': 'Alien Artifacts', 'base_price': 800, 'description': 'Mysterious alien objects', 'category': 'luxury'},
            {'name': 'Rare Gems', 'base_price': 400, 'description': 'Precious stones', 'category': 'luxury'},
            {'name': 'Stolen Cargo', 'base_price': 300, 'description': 'Questionable goods', 'category': 'luxury'},
            
            # Food
            {'name': 'Synthetic Food', 'base_price': 5, 'description': 'Basic nutrition', 'category': 'food'},
            {'name': 'Fresh Vegetables', 'base_price': 20, 'description': 'Grown on hydroponic farms', 'category': 'food'},
            {'name': 'Exotic Spices', 'base_price': 75, 'description': 'Rare flavorings', 'category': 'food'},
            
            # Medical
            {'name': 'Med Kits', 'base_price': 100, 'description': 'Medical supplies', 'category': 'medical'},
            {'name': 'Stimulants', 'base_price': 200, 'description': 'Performance enhancers', 'category': 'medical'},
            {'name': 'Nanobots', 'base_price': 1500, 'description': 'Advanced medical technology', 'category': 'medical'},
            
            # Research
            {'name': 'Research Data', 'base_price': 500, 'description': 'Valuable scientific information', 'category': 'research'},
            {'name': 'Experimental Weapon', 'base_price': 600, 'description': 'Prototype energy weapon', 'category': 'technology'},
            {'name': 'Smuggler\'s Map', 'base_price': 80, 'description': 'Shows secret routes', 'category': 'equipment'}
        ]
        
        for good_data in goods_data:
            good = TradeGood(
                name=good_data['name'],
                base_price=good_data['base_price'],
                description=good_data['description'],
                category=good_data['category']
            )
            self.trade_goods[good_data['name']] = good

        # Mapping of trade good names to DynamicMarketSystem commodity names
        self.good_to_commodity = {
            'Iron Ore': 'Iron',
            'Gold': 'Gold',
            'Platinum': 'Gold',
            'Uranium': 'Rare Compounds',
            'Raw Minerals': 'Copper',
            'Ammolite': 'Ammolite',
            'Computer Chips': 'Computer Chips',
            'Quantum Processors': 'AI Cores',
            'Energy Cells': 'Energy Cells',
            'Shield Generators': 'Military Hardware',
            'Quantum Scanner': 'Electronics',
            'Space Wine': 'Food',
            'Alien Artifacts': 'Rare Compounds',
            'Rare Gems': 'Ammolite',
            'Stolen Cargo': 'Rare Compounds',
            'Synthetic Food': 'Food',
            'Fresh Vegetables': 'Food',
            'Exotic Spices': 'Spices',
            'Med Kits': 'Medicine',
            'Stimulants': 'Medicine',
            'Nanobots': 'Medical Equipment',
            'Research Data': 'Software',
            'Experimental Weapon': 'Weapons',
            "Smuggler's Map": 'Software'
        }
    
    def _create_markets(self):
        """Initialize sector economies for known locations"""

        locations = ['Earth Station', 'Mars Colony', 'Luna Base', 'Pirate Haven', 'Deep Space Lab']
        for idx, location in enumerate(locations, start=1):
            self.location_sectors[location] = idx
            self.location_markets[location] = {}
            # Ensure a sector economy exists in the dynamic market
            self.market_system.initialize_sector_economy(idx)
            # Prime local price cache
            self._update_market_prices(location)

    def _update_market_prices(self, location: str):
        """Retrieve current prices from the dynamic market system"""
        if location not in self.market_prices:
            self.market_prices[location] = {}

        sector_id = self.location_sectors.get(location)
        if sector_id is None:
            return

        info = self.market_system.get_market_info(sector_id)
        prices = info['prices']

        for good_name, commodity_name in self.good_to_commodity.items():
            price = prices.get(commodity_name)
            if price is None:
                continue
            self.market_prices[location][good_name] = int(price)

            # Store price history
            if location not in self.price_history:
                self.price_history[location] = {}
            if good_name not in self.price_history[location]:
                self.price_history[location][good_name] = []
            self.price_history[location][good_name].append(int(price))
    
    def _update_all_prices(self):
        """Update prices for all markets"""
        for location in self.location_markets.keys():
            self._update_market_prices(location)
    
    def get_market_info(self, location: str) -> Dict:
        """Get market information for a location"""
        if location not in self.location_sectors:
            return {'available': False}

        # Refresh prices before returning data
        self._update_market_prices(location)
        prices = self.market_prices.get(location, {})
        sector_id = self.location_sectors[location]
        condition = self.market_system.get_market_info(sector_id)['market_condition']

        goods = []
        for good_name, price in prices.items():
            goods.append({
                'name': good_name,
                'price': price,
                'description': self.trade_goods[good_name].description if good_name in self.trade_goods else '',
                'category': self.trade_goods[good_name].category if good_name in self.trade_goods else ''
            })

        return {
            'available': True,
            'market_condition': condition,
            'goods': goods,
            # Legacy fields for compatibility
            'specialization': '',
            'price_modifier': 1.0,
            'trade_volume': 'medium',
            'security': 'medium'
        }
    
    def buy_item(self, player: Player, location: str, item_name: str, quantity: int = 1) -> Dict:
        """Player buys an item from the market"""
        market_info = self.get_market_info(location)
        if not market_info['available']:
            return {'success': False, 'message': 'No market available here'}
        
        # Find the item in the market
        item_data = None
        for good in market_info['goods']:
            if good['name'].lower() == item_name.lower():
                item_data = good
                break
        
        if not item_data:
            return {'success': False, 'message': f'{item_name} not available here'}

        total_cost = item_data['price'] * quantity
        
        # Check if player has enough credits
        if player.credits < total_cost:
            return {'success': False, 'message': f'Not enough credits. Need {total_cost}, have {player.credits}'}
        
        # Create the item and add to inventory
        item = Item(
            name=item_data['name'],
            description=item_data['description'],
            value=item_data['price'],
            item_type='trade_good'
        )
        
        # Add items to inventory
        for _ in range(quantity):
            if not player.add_item(item):
                return {'success': False, 'message': 'Inventory full'}
        
        # Deduct credits
        player.spend_credits(total_cost)

        # Update dynamic market supply/demand
        sector_id = self.location_sectors.get(location)
        commodity = self.good_to_commodity.get(item_data['name'], item_data['name'])
        if sector_id is not None:
            self.market_system.update_trade(sector_id, commodity, quantity, True)

        # Record trade
        self._record_trade('buy', location, item_data['name'], quantity, total_cost)

        return {
            'success': True,
            'message': f'Bought {quantity} {item_data["name"]} for {total_cost} credits',
            'cost': total_cost,
            'item': item_data['name']
        }
    
    def sell_item(self, player: Player, location: str, item_name: str, quantity: int = 1) -> Dict:
        """Player sells an item to the market"""
        market_info = self.get_market_info(location)
        if not market_info['available']:
            return {'success': False, 'message': 'No market available here'}
        
        # Check if player has the item
        item = player.get_item(item_name)
        if not item:
            return {'success': False, 'message': f'You don\'t have {item_name}'}
        
        # Calculate sell price (usually lower than buy price)
        sell_price = item.value * 0.7  # 70% of base value
        bonus = player.get_crew_bonus('trading') / 100
        sell_price *= (1 + bonus)
        
        # Apply market specialization bonus
        if item.item_type == 'trade_good':
            for good in market_info['goods']:
                if good['name'].lower() == item_name.lower():
                    sell_price = good['price'] * 0.7
                    break
        
        total_earnings = int(sell_price * quantity)
        
        # Remove items from inventory
        for _ in range(quantity):
            removed_item = player.remove_item(item_name)
            if not removed_item:
                return {'success': False, 'message': f'Not enough {item_name} to sell'}
        
        # Add credits
        player.add_credits(total_earnings)

        # Update dynamic market after sale
        sector_id = self.location_sectors.get(location)
        commodity = self.good_to_commodity.get(item_name, item_name)
        if sector_id is not None:
            self.market_system.update_trade(sector_id, commodity, quantity, False)

        # Record trade
        self._record_trade('sell', location, item_name, quantity, total_earnings)

        return {
            'success': True,
            'message': f'Sold {quantity} {item_name} for {total_earnings} credits',
            'earnings': total_earnings,
            'item': item_name
        }
    
    def _record_trade(self, trade_type: str, location: str, item_name: str, quantity: int, amount: int):
        """Record a trade in history"""
        self.trade_history.append({
            'type': trade_type,
            'location': location,
            'item': item_name,
            'quantity': quantity,
            'amount': amount,
            'timestamp': len(self.trade_history)  # Simple timestamp
        })
    
    def get_trade_opportunities(self, player: Player, location: str) -> List[Dict]:
        """Find profitable trade opportunities"""
        market_info = self.get_market_info(location)
        if not market_info['available']:
            return []
        
        opportunities = []
        
        # Check what player can buy
        for good in market_info['goods']:
            if player.credits >= good['price']:
                opportunities.append({
                    'type': 'buy',
                    'item': good['name'],
                    'price': good['price'],
                    'description': f"Buy {good['name']} for {good['price']} credits"
                })
        
        # Check what player can sell
        for item in player.inventory:
            if item.item_type == 'trade_good':
                sell_price = item.value * 0.7
                opportunities.append({
                    'type': 'sell',
                    'item': item.name,
                    'price': sell_price,
                    'description': f"Sell {item.name} for {sell_price} credits"
                })
        
        return opportunities
    
    def get_market_summary(self, location: str) -> str:
        """Get a text summary of the market"""
        market_info = self.get_market_info(location)
        if not market_info['available']:
            return "No market available at this location."

        summary = f"\n[bold cyan]Market at {location}[/bold cyan]\n"
        summary += f"Condition: {market_info['market_condition'].title()}\n\n"

        summary += "[bold yellow]Available Goods:[/bold yellow]\n"
        for good in market_info['goods']:
            summary += f"  • {good['name']}: {good['price']} credits\n"
            summary += f"    {good['description']}\n"
        
        return summary
    
    def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """Get recent trade history"""
        return self.trade_history[-limit:] if self.trade_history else []
    
    def get_price_trends(self, location: str, item_name: str) -> Dict:
        """Get price trends for an item at a location"""
        if location not in self.price_history or item_name not in self.price_history[location]:
            return {'trend': 'stable', 'change': 0}
        
        prices = self.price_history[location][item_name]
        if len(prices) < 2:
            return {'trend': 'stable', 'change': 0}
        
        current_price = prices[-1]
        previous_price = prices[-2]
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
        
        if change_percent > 5:
            trend = 'rising'
        elif change_percent < -5:
            trend = 'falling'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change': change,
            'change_percent': change_percent,
            'current_price': current_price,
            'previous_price': previous_price
        }
    
    def get_best_trade_routes(self, player: Player) -> List[Dict]:
        """Find the most profitable trade routes"""
        routes = []
        
        for location in self.location_markets.keys():
            market_info = self.get_market_info(location)
            if not market_info['available']:
                continue
            
            # Find items to buy here and sell elsewhere
            for good in market_info['goods']:
                if player.credits >= good['price']:
                    # Check if we can sell this item for more elsewhere
                    for other_location in self.location_markets.keys():
                        if other_location != location:
                            other_market = self.get_market_info(other_location)
                            for other_good in other_market['goods']:
                                if other_good['name'] == good['name']:
                                    profit = other_good['price'] - good['price']
                                    if profit > 0:
                                        routes.append({
                                            'buy_location': location,
                                            'sell_location': other_location,
                                            'item': good['name'],
                                            'buy_price': good['price'],
                                            'sell_price': other_good['price'],
                                            'profit': profit,
                                            'profit_margin': (profit / good['price']) * 100
                                        })
        
        # Sort by profit margin
        routes.sort(key=lambda x: x['profit_margin'], reverse=True)
        return routes[:5]  # Return top 5 routes 