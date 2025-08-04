"""
Trading system for LOGDTW2002
Handles economy, trading, and market mechanics
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from game.player import Player, Item

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
        self.trade_goods = {}
        self.market_prices = {}
        self.location_markets = {}
        
        # Initialize trade goods
        self._create_trade_goods()
        
        # Initialize markets at different locations
        self._create_markets()
    
    def _create_trade_goods(self):
        """Create available trade goods"""
        goods_data = [
            # Minerals
            {'name': 'Iron Ore', 'base_price': 10, 'description': 'Basic industrial metal', 'category': 'minerals'},
            {'name': 'Gold', 'base_price': 100, 'description': 'Precious metal', 'category': 'minerals'},
            {'name': 'Platinum', 'base_price': 200, 'description': 'Rare industrial metal', 'category': 'minerals'},
            {'name': 'Uranium', 'base_price': 500, 'description': 'Radioactive material', 'category': 'minerals'},
            
            # Technology
            {'name': 'Computer Chips', 'base_price': 50, 'description': 'Electronic components', 'category': 'technology'},
            {'name': 'Quantum Processors', 'base_price': 1000, 'description': 'Advanced computing technology', 'category': 'technology'},
            {'name': 'Energy Cells', 'base_price': 25, 'description': 'Power storage units', 'category': 'technology'},
            {'name': 'Shield Generators', 'base_price': 300, 'description': 'Defensive technology', 'category': 'technology'},
            
            # Luxury Goods
            {'name': 'Space Wine', 'base_price': 150, 'description': 'Fine alcoholic beverage', 'category': 'luxury'},
            {'name': 'Alien Artifacts', 'base_price': 800, 'description': 'Mysterious alien objects', 'category': 'luxury'},
            {'name': 'Rare Gems', 'base_price': 400, 'description': 'Precious stones', 'category': 'luxury'},
            
            # Food
            {'name': 'Synthetic Food', 'base_price': 5, 'description': 'Basic nutrition', 'category': 'food'},
            {'name': 'Fresh Vegetables', 'base_price': 20, 'description': 'Grown on hydroponic farms', 'category': 'food'},
            {'name': 'Exotic Spices', 'base_price': 75, 'description': 'Rare flavorings', 'category': 'food'},
            
            # Medical
            {'name': 'Med Kits', 'base_price': 100, 'description': 'Medical supplies', 'category': 'medical'},
            {'name': 'Stimulants', 'base_price': 200, 'description': 'Performance enhancers', 'category': 'medical'},
            {'name': 'Nanobots', 'base_price': 1500, 'description': 'Advanced medical technology', 'category': 'medical'}
        ]
        
        for good_data in goods_data:
            good = TradeGood(
                name=good_data['name'],
                base_price=good_data['base_price'],
                description=good_data['description'],
                category=good_data['category']
            )
            self.trade_goods[good_data['name']] = good
    
    def _create_markets(self):
        """Create markets at different locations"""
        # Market data for different locations
        markets_data = {
            'Earth Station': {
                'specialization': 'technology',
                'price_modifier': 1.0,
                'available_goods': ['Computer Chips', 'Energy Cells', 'Synthetic Food', 'Med Kits']
            },
            'Mars Colony': {
                'specialization': 'minerals',
                'price_modifier': 0.8,
                'available_goods': ['Iron Ore', 'Gold', 'Platinum', 'Synthetic Food']
            },
            'Luna Base': {
                'specialization': 'research',
                'price_modifier': 1.2,
                'available_goods': ['Computer Chips', 'Quantum Processors', 'Energy Cells', 'Med Kits']
            },
            'Pirate Haven': {
                'specialization': 'luxury',
                'price_modifier': 1.5,
                'available_goods': ['Alien Artifacts', 'Rare Gems', 'Space Wine', 'Stimulants']
            },
            'Deep Space Lab': {
                'specialization': 'technology',
                'price_modifier': 1.3,
                'available_goods': ['Quantum Processors', 'Shield Generators', 'Nanobots', 'Energy Cells']
            }
        }
        
        for location, market_data in markets_data.items():
            self.location_markets[location] = market_data
            self._update_market_prices(location, market_data)
    
    def _update_market_prices(self, location: str, market_data: Dict):
        """Update prices for a specific location"""
        if location not in self.market_prices:
            self.market_prices[location] = {}
        
        for good_name in market_data['available_goods']:
            if good_name in self.trade_goods:
                good = self.trade_goods[good_name]
                base_price = good.base_price
                
                # Apply location modifier
                price_modifier = market_data['price_modifier']
                
                # Apply specialization bonus
                if good.category == market_data['specialization']:
                    price_modifier *= 1.2
                
                # Add some randomness
                random_factor = random.uniform(0.9, 1.1)
                
                final_price = int(base_price * price_modifier * random_factor)
                self.market_prices[location][good_name] = final_price
    
    def get_market_info(self, location: str) -> Dict:
        """Get market information for a location"""
        if location not in self.location_markets:
            return {'available': False}
        
        market_data = self.location_markets[location]
        prices = self.market_prices.get(location, {})
        
        return {
            'available': True,
            'specialization': market_data['specialization'],
            'price_modifier': market_data['price_modifier'],
            'goods': [
                {
                    'name': good_name,
                    'price': prices.get(good_name, 0),
                    'description': self.trade_goods[good_name].description if good_name in self.trade_goods else '',
                    'category': self.trade_goods[good_name].category if good_name in self.trade_goods else ''
                }
                for good_name in market_data['available_goods']
            ]
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
        
        return {
            'success': True,
            'message': f'Sold {quantity} {item_name} for {total_earnings} credits',
            'earnings': total_earnings,
            'item': item_name
        }
    
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
        summary += f"Specialization: {market_info['specialization'].title()}\n"
        summary += f"Price Modifier: {market_info['price_modifier']:.1f}x\n\n"
        
        summary += "[bold yellow]Available Goods:[/bold yellow]\n"
        for good in market_info['goods']:
            summary += f"  {good['name']}: {good['price']} credits\n"
        
        return summary 