"""
Galactic Stock Market and Banking System for LOGDTW2002
Handles investments, banking, and financial services
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from game.player import Player

@dataclass
class Stock:
    """Represents a stock in the galactic market"""
    symbol: str
    name: str
    sector: str  # technology, mining, luxury, etc.
    current_price: float
    base_price: float
    volatility: float  # 0.1 to 2.0
    dividend_yield: float  # percentage
    market_cap: int
    description: str

@dataclass
class BankAccount:
    """Represents a bank account"""
    account_number: str
    balance: float
    account_type: str  # savings, checking, investment
    interest_rate: float
    last_interest: float

class StockMarket:
    """Handles the galactic stock market"""
    
    def __init__(self):
        self.stocks = {}
        self.player_portfolio = {}
        self.market_history = {}
        self.last_update = time.time()
        self._create_stocks()
    
    def _create_stocks(self):
        """Create initial stocks"""
        stocks_data = [
            {
                'symbol': 'TECH',
                'name': 'Galactic Technologies',
                'sector': 'technology',
                'current_price': 150.0,
                'base_price': 150.0,
                'volatility': 0.8,
                'dividend_yield': 2.5,
                'market_cap': 1000000000,
                'description': 'Leading technology corporation'
            },
            {
                'symbol': 'MINING',
                'name': 'Deep Space Mining Corp',
                'sector': 'mining',
                'current_price': 75.0,
                'base_price': 75.0,
                'volatility': 1.2,
                'dividend_yield': 4.0,
                'market_cap': 500000000,
                'description': 'Mining and resource extraction'
            },
            {
                'symbol': 'LUXURY',
                'name': 'Luxury Goods International',
                'sector': 'luxury',
                'current_price': 200.0,
                'base_price': 200.0,
                'volatility': 0.6,
                'dividend_yield': 1.8,
                'market_cap': 800000000,
                'description': 'Premium luxury goods manufacturer'
            },
            {
                'symbol': 'SHIP',
                'name': 'Stellar Shipyards',
                'sector': 'manufacturing',
                'current_price': 120.0,
                'base_price': 120.0,
                'volatility': 0.9,
                'dividend_yield': 3.2,
                'market_cap': 600000000,
                'description': 'Starship construction and repair'
            },
            {
                'symbol': 'ENERGY',
                'name': 'Quantum Energy Systems',
                'sector': 'energy',
                'current_price': 90.0,
                'base_price': 90.0,
                'volatility': 1.1,
                'dividend_yield': 3.8,
                'market_cap': 400000000,
                'description': 'Advanced energy technology'
            },
            {
                'symbol': 'MEDICAL',
                'name': 'Interstellar Medical',
                'sector': 'healthcare',
                'current_price': 180.0,
                'base_price': 180.0,
                'volatility': 0.7,
                'dividend_yield': 2.1,
                'market_cap': 1200000000,
                'description': 'Medical technology and pharmaceuticals'
            },
            {
                'symbol': 'ENTERTAIN',
                'name': 'Galactic Entertainment',
                'sector': 'entertainment',
                'current_price': 60.0,
                'base_price': 60.0,
                'volatility': 1.3,
                'dividend_yield': 1.5,
                'market_cap': 300000000,
                'description': 'Entertainment and media company'
            },
            {
                'symbol': 'SECURITY',
                'name': 'Federation Security',
                'sector': 'defense',
                'current_price': 250.0,
                'base_price': 250.0,
                'volatility': 0.5,
                'dividend_yield': 2.8,
                'market_cap': 2000000000,
                'description': 'Defense and security systems'
            }
        ]
        
        for stock_data in stocks_data:
            stock = Stock(**stock_data)
            self.stocks[stock_data['symbol']] = stock
            self.market_history[stock_data['symbol']] = [stock_data['current_price']]
    
    def update_market(self):
        """Update stock prices based on market conditions"""
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        # Update prices every 5 minutes
        if time_diff < 300:  # 5 minutes
            return
        
        for symbol, stock in self.stocks.items():
            # Calculate price change based on volatility
            change_percent = random.gauss(0, stock.volatility * 0.1)
            new_price = stock.current_price * (1 + change_percent)
            
            # Ensure price doesn't go below 1.0
            stock.current_price = max(1.0, new_price)
            
            # Store price history
            self.market_history[symbol].append(stock.current_price)
            if len(self.market_history[symbol]) > 100:
                self.market_history[symbol].pop(0)
        
        self.last_update = current_time
    
    def get_stock_info(self, symbol: str) -> Optional[Stock]:
        """Get information about a specific stock"""
        return self.stocks.get(symbol)
    
    def get_all_stocks(self) -> List[Stock]:
        """Get all available stocks"""
        return list(self.stocks.values())
    
    def buy_stock(self, player: Player, symbol: str, shares: int) -> Dict:
        """Buy shares of a stock"""
        if symbol not in self.stocks:
            return {'success': False, 'message': 'Stock not found'}
        
        stock = self.stocks[symbol]
        total_cost = stock.current_price * shares
        
        if player.credits < total_cost:
            return {'success': False, 'message': f'Not enough credits. Need {total_cost}, have {player.credits}'}
        
        # Deduct credits
        player.spend_credits(total_cost)
        
        # Add to portfolio
        if symbol not in self.player_portfolio:
            self.player_portfolio[symbol] = 0
        self.player_portfolio[symbol] += shares
        
        return {
            'success': True,
            'message': f'Bought {shares} shares of {symbol} for {total_cost} credits',
            'total_cost': total_cost,
            'shares': shares
        }
    
    def sell_stock(self, player: Player, symbol: str, shares: int) -> Dict:
        """Sell shares of a stock"""
        if symbol not in self.stocks:
            return {'success': False, 'message': 'Stock not found'}
        
        if symbol not in self.player_portfolio or self.player_portfolio[symbol] < shares:
            return {'success': False, 'message': f'Not enough shares. Have {self.player_portfolio.get(symbol, 0)}, need {shares}'}
        
        stock = self.stocks[symbol]
        total_value = stock.current_price * shares
        
        # Add credits
        player.add_credits(total_value)
        
        # Remove from portfolio
        self.player_portfolio[symbol] -= shares
        if self.player_portfolio[symbol] <= 0:
            del self.player_portfolio[symbol]
        
        return {
            'success': True,
            'message': f'Sold {shares} shares of {symbol} for {total_value} credits',
            'total_value': total_value,
            'shares': shares
        }
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        total_value = 0
        for symbol, shares in self.player_portfolio.items():
            if symbol in self.stocks:
                stock = self.stocks[symbol]
                total_value += stock.current_price * shares
        return total_value
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        summary = {
            'total_shares': 0,
            'total_value': 0,
            'holdings': []
        }
        
        for symbol, shares in self.player_portfolio.items():
            if symbol in self.stocks:
                stock = self.stocks[symbol]
                value = stock.current_price * shares
                summary['total_shares'] += shares
                summary['total_value'] += value
                summary['holdings'].append({
                    'symbol': symbol,
                    'name': stock.name,
                    'shares': shares,
                    'current_price': stock.current_price,
                    'total_value': value
                })
        
        return summary

class BankingSystem:
    """Handles banking and financial services"""
    
    def __init__(self):
        self.accounts = {}
        self.branches = self._create_branches()
        self.last_interest_update = time.time()
    
    def _create_branches(self) -> Dict:
        """Create bank branches"""
        return {
            'Earth Station': {
                'name': 'Federation Central Bank',
                'services': ['savings', 'checking', 'investment', 'loans'],
                'interest_rate': 0.025
            },
            'Mars Colony': {
                'name': 'Mars Colonial Bank',
                'services': ['savings', 'checking', 'investment'],
                'interest_rate': 0.03
            },
            'Luna Base': {
                'name': 'Lunar Credit Union',
                'services': ['savings', 'checking'],
                'interest_rate': 0.02
            },
            'Pirate Haven': {
                'name': 'Offshore Banking Corp',
                'services': ['savings', 'investment'],
                'interest_rate': 0.05
            }
        }
    
    def create_account(self, player: Player, account_type: str, location: str) -> Dict:
        """Create a new bank account"""
        if location not in self.branches:
            return {'success': False, 'message': 'No bank branch at this location'}
        
        branch = self.branches[location]
        if account_type not in branch['services']:
            return {'success': False, 'message': f'{account_type} accounts not available at this branch'}
        
        # Generate account number
        account_number = f"{location[:3].upper()}{random.randint(100000, 999999)}"
        
        account = BankAccount(
            account_number=account_number,
            balance=0.0,
            account_type=account_type,
            interest_rate=branch['interest_rate'],
            last_interest=time.time()
        )
        
        self.accounts[account_number] = account
        
        return {
            'success': True,
            'message': f'Created {account_type} account: {account_number}',
            'account_number': account_number
        }
    
    def deposit(self, player: Player, account_number: str, amount: float) -> Dict:
        """Deposit money into account"""
        if account_number not in self.accounts:
            return {'success': False, 'message': 'Account not found'}
        
        if player.credits < amount:
            return {'success': False, 'message': f'Not enough credits. Have {player.credits}, need {amount}'}
        
        account = self.accounts[account_number]
        account.balance += amount
        player.spend_credits(amount)
        
        return {
            'success': True,
            'message': f'Deposited {amount} credits into account {account_number}',
            'new_balance': account.balance
        }
    
    def withdraw(self, player: Player, account_number: str, amount: float) -> Dict:
        """Withdraw money from account"""
        if account_number not in self.accounts:
            return {'success': False, 'message': 'Account not found'}
        
        account = self.accounts[account_number]
        if account.balance < amount:
            return {'success': False, 'message': f'Insufficient funds. Balance: {account.balance}, requested: {amount}'}
        
        account.balance -= amount
        player.add_credits(amount)
        
        return {
            'success': True,
            'message': f'Withdrew {amount} credits from account {account_number}',
            'new_balance': account.balance
        }
    
    def get_account_info(self, account_number: str) -> Optional[BankAccount]:
        """Get account information"""
        return self.accounts.get(account_number)
    
    def get_all_accounts(self) -> List[BankAccount]:
        """Get all player accounts"""
        return list(self.accounts.values())
    
    def update_interest(self):
        """Update interest on savings accounts"""
        current_time = time.time()
        time_diff = current_time - self.last_interest_update
        
        # Update interest every hour
        if time_diff < 3600:  # 1 hour
            return
        
        for account in self.accounts.values():
            if account.account_type == 'savings':
                # Calculate interest (simple interest)
                interest = account.balance * account.interest_rate * (time_diff / 3600)
                account.balance += interest
                account.last_interest = current_time
        
        self.last_interest_update = current_time
    
    def get_branch_info(self, location: str) -> Dict:
        """Get information about a bank branch"""
        if location not in self.branches:
            return {'available': False}
        
        branch = self.branches[location]
        return {
            'available': True,
            'name': branch['name'],
            'services': branch['services'],
            'interest_rate': branch['interest_rate']
        } 