// LOGDTW2002 Web Edition - Main Game Logic

class GameEngine {
    constructor() {
        this.player = {};
        this.world = {};
        this.terminal = null;
        this.ui = null;
        this.lastUpdate = Date.now();
        this.gameLoop = null;
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing LOGDTW2002 Web Edition...');
        
        // Initialize subsystems
        this.terminal = new TerminalManager();
        this.ui = new UIManager();
        
        // Load initial game state
        this.loadGameState();
        
        // Start game loop
        this.startGameLoop();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ Game initialized successfully');
    }
    
    loadGameState() {
        // Load player and world state from server
        this.sendRequest('get_status')
            .then(response => {
                if (response.success) {
                    this.player = response.player;
                    this.world = response.world;
                    this.ui.updatePlayerDisplay();
                    this.terminal.addLine('SYSTEM', 'Game state loaded successfully', 'success');
                } else {
                    this.terminal.addLine('ERROR', 'Failed to load game state', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to load game state:', error);
                this.terminal.addLine('ERROR', 'Connection error', 'error');
            });
    }
    
    startGameLoop() {
        this.gameLoop = setInterval(() => {
            this.update();
        }, 1000); // Update every second
    }
    
    update() {
        const now = Date.now();
        const deltaTime = now - this.lastUpdate;
        this.lastUpdate = now;
        
        // Update game systems
        this.updateSystems(deltaTime);
        
        // Update UI
        this.ui.update();
    }
    
    updateSystems(deltaTime) {
        // Update any time-based systems here
        // For example: fuel consumption, energy regeneration, etc.
    }
    
    setupEventListeners() {
        // Terminal command input
        document.getElementById('terminal-command').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand();
            }
        });
        
        // Auto-save every 5 minutes
        setInterval(() => {
            this.autoSave();
        }, 5 * 60 * 1000);
    }
    
    executeCommand() {
        const input = document.getElementById('terminal-command');
        const command = input.value.trim();
        
        if (command) {
            this.terminal.addLine('CAPTAIN', command, 'command');
            this.processCommand(command);
            input.value = '';
        }
    }
    
    processCommand(command) {
        const args = command.toLowerCase().split(' ');
        const cmd = args[0];
        
        switch (cmd) {
            case 'help':
            case '?':
                this.showHelp();
                break;
                
            case 'status':
            case 'stat':
                this.showStatus();
                break;
                
            case 'jump':
            case 'travel':
                if (args[1]) {
                    this.travelToSector(parseInt(args[1]));
                } else {
                    this.terminal.addLine('ERROR', 'Usage: jump <sector_number>', 'error');
                }
                break;
                
            case 'scan':
                this.scanSector();
                break;
                
            case 'market':
            case 'trade':
                this.showMarket();
                break;
                
            case 'buy':
                if (args[1] && args[2]) {
                    this.buyItem(args[1], parseInt(args[2]));
                } else {
                    this.terminal.addLine('ERROR', 'Usage: buy <item> <quantity>', 'error');
                }
                break;
                
            case 'sell':
                if (args[1] && args[2]) {
                    this.sellItem(args[1], parseInt(args[2]));
                } else {
                    this.terminal.addLine('ERROR', 'Usage: sell <item> <quantity>', 'error');
                }
                break;
                
            case 'inventory':
            case 'inv':
                this.showInventory();
                break;
                
            case 'map':
                this.showMap();
                break;
                
            case 'save':
                this.saveGame();
                break;
                
            case 'load':
                this.loadGame();
                break;
                
            case 'clear':
                this.terminal.clear();
                break;
                
            default:
                this.terminal.addLine('ERROR', `Unknown command: ${cmd}. Type 'help' for available commands.`, 'error');
        }
    }
    
    showHelp() {
        const commands = [
            'Navigation Commands:',
            '  jump <sector>    - Jump to specified sector',
            '  scan            - Scan current sector',
            '  map             - Show galaxy map',
            '',
            'Trading Commands:',
            '  market          - Show market prices',
            '  buy <item> <qty> - Buy items',
            '  sell <item> <qty> - Sell items',
            '  inventory       - Show cargo hold',
            '',
            'System Commands:',
            '  status          - Show ship status',
            '  save            - Save game',
            '  load            - Load game',
            '  clear           - Clear terminal',
            '  help            - Show this help'
        ];
        
        commands.forEach(line => {
            this.terminal.addLine('HELP', line, 'info');
        });
    }
    
    showStatus() {
        const status = [
            `Captain: ${this.player.name}`,
            `Ship: ${this.player.ship_name}`,
            `Credits: ${this.player.credits.toLocaleString()}`,
            `Health: ${this.player.health}/${this.player.max_health}`,
            `Energy: ${this.player.energy}/${this.player.max_energy}`,
            `Fuel: ${this.player.fuel}/${this.player.max_fuel}`,
            `Current Sector: ${this.player.current_sector}`,
            `Level: ${this.player.level}`
        ];
        
        status.forEach(line => {
            this.terminal.addLine('STATUS', line, 'info');
        });
    }
    
    travelToSector(sector) {
        if (isNaN(sector) || sector < 1 || sector > 20) {
            this.terminal.addLine('ERROR', 'Invalid sector number (1-20)', 'error');
            return;
        }
        
        if (this.player.fuel < 10) {
            this.terminal.addLine('ERROR', 'Insufficient fuel for jump', 'error');
            return;
        }
        
        this.terminal.addLine('SYSTEM', `Initiating jump to Sector ${sector}...`, 'info');
        
        this.sendRequest('travel', { sector: sector })
            .then(response => {
                if (response.success) {
                    this.player = response.player;
                    this.terminal.addLine('SYSTEM', response.message, 'success');
                    this.ui.updatePlayerDisplay();
                    this.scanSector();
                } else {
                    this.terminal.addLine('ERROR', response.message, 'error');
                }
            })
            .catch(error => {
                this.terminal.addLine('ERROR', 'Jump failed: Communication error', 'error');
            });
    }
    
    scanSector() {
        this.terminal.addLine('SYSTEM', 'Scanning sector...', 'info');
        
        // Simulate scan results
        const discoveries = [
            'Trade station detected',
            'No hostile signatures',
            'Asteroid field present',
            'Safe passage confirmed'
        ];
        
        discoveries.forEach(discovery => {
            this.terminal.addLine('SCAN', discovery, 'success');
        });
    }
    
    showMarket() {
        this.terminal.addLine('MARKET', '=== MARKET PRICES ===', 'info');
        
        const market = {
            'Food': 50,
            'Iron': 100,
            'Electronics': 300,
            'Weapons': 800,
            'Medicine': 400,
            'Fuel': 75
        };
        
        Object.entries(market).forEach(([item, price]) => {
            this.terminal.addLine('MARKET', `${item.padEnd(12)} ${price} credits`, 'info');
        });
        
        this.terminal.addLine('MARKET', 'Use: buy <item> <quantity> or sell <item> <quantity>', 'info');
    }
    
    buyItem(item, quantity) {
        const itemName = this.capitalizeFirst(item);
        
        this.sendRequest('trade', {
            item: itemName,
            quantity: quantity,
            trade_action: 'buy'
        })
        .then(response => {
            if (response.success) {
                this.player.credits = response.credits;
                this.terminal.addLine('TRADE', response.message, 'success');
                this.ui.updatePlayerDisplay();
                this.ui.updateInventory();
            } else {
                this.terminal.addLine('ERROR', response.message, 'error');
            }
        })
        .catch(error => {
            this.terminal.addLine('ERROR', 'Trade failed: Communication error', 'error');
        });
    }
    
    sellItem(item, quantity) {
        const itemName = this.capitalizeFirst(item);
        
        this.sendRequest('trade', {
            item: itemName,
            quantity: quantity,
            trade_action: 'sell'
        })
        .then(response => {
            if (response.success) {
                this.player.credits = response.credits;
                this.terminal.addLine('TRADE', response.message, 'success');
                this.ui.updatePlayerDisplay();
                this.ui.updateInventory();
            } else {
                this.terminal.addLine('ERROR', response.message, 'error');
            }
        })
        .catch(error => {
            this.terminal.addLine('ERROR', 'Trade failed: Communication error', 'error');
        });
    }
    
    showInventory() {
        this.terminal.addLine('INVENTORY', '=== CARGO HOLD ===', 'info');
        
        // This would be loaded from server in a real implementation
        const inventory = JSON.parse(localStorage.getItem('inventory') || '[]');
        
        if (inventory.length === 0) {
            this.terminal.addLine('INVENTORY', 'Cargo hold is empty', 'info');
        } else {
            inventory.forEach(item => {
                this.terminal.addLine('INVENTORY', `${item.name} x${item.quantity}`, 'info');
            });
        }
    }
    
    showMap() {
        this.terminal.addLine('MAP', '=== GALAXY MAP ===', 'info');
        
        const map = [
            '    [1]--[2]--[3]',
            '     |    |    |',
            '    [4]--[5]--[6]',
            '     |    |    |',
            '    [7]--[8]--[9]',
            '',
            `Current Position: Sector ${this.player.current_sector}`,
            'Use: jump <sector> to travel'
        ];
        
        map.forEach(line => {
            this.terminal.addLine('MAP', line, 'info');
        });
    }
    
    saveGame(saveName = 'quicksave') {
        this.sendRequest('save_game', { save_name: saveName })
            .then(response => {
                if (response.success) {
                    this.terminal.addLine('SYSTEM', response.message, 'success');
                } else {
                    this.terminal.addLine('ERROR', 'Failed to save game', 'error');
                }
            })
            .catch(error => {
                this.terminal.addLine('ERROR', 'Save failed: Communication error', 'error');
            });
    }
    
    loadGame(saveName = 'quicksave') {
        this.sendRequest('load_game', { save_name: saveName })
            .then(response => {
                if (response.success) {
                    this.player = response.player;
                    this.terminal.addLine('SYSTEM', response.message, 'success');
                    this.ui.updatePlayerDisplay();
                } else {
                    this.terminal.addLine('ERROR', response.message, 'error');
                }
            })
            .catch(error => {
                this.terminal.addLine('ERROR', 'Load failed: Communication error', 'error');
            });
    }
    
    autoSave() {
        this.saveGame('autosave');
        this.terminal.addLine('SYSTEM', 'Auto-save completed', 'info');
    }
    
    sendRequest(action, data = {}) {
        const endpoints = {
            get_status: 'status',
            travel: 'travel',
            trade: 'trade'
        };

        const endpoint = endpoints[action];
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        };

        if (action === 'get_status') {
            options.method = 'GET';
            delete options.body;
        }

        return fetch(`/api/${endpoint}`, options)
            .then(response => response.json())
            .catch(error => {
                console.error('Request failed:', error);
                throw error;
            });
    }
    
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// --- Advanced NPC System for Web Version ---
class WebNPC {
    constructor(name, type, personality, dialogue) {
        this.name = name;
        this.type = type;
        this.personality = personality;
        this.dialogue = dialogue;
        this.relationships = {};
    }

    adjustRelationship(target, amount) {
        this.relationships[target] = (this.relationships[target] || 0) + amount;
    }

    getLine(category) {
        const lines = this.dialogue[category] || [];
        return lines[Math.floor(Math.random() * lines.length)] || '';
    }
}

const npcDatabase = {
    commander: new WebNPC('Station Commander', 'official', 'neutral', {
        greeting: ['Welcome to Alpha Station, Captain.'],
        rumors: ['Federation patrols have increased in the core sectors.'],
        farewell: ['Stay vigilant out there.']
    }),
    trader: new WebNPC('Trader McKenzie', 'trader', 'friendly', {
        greeting: ['Looking for good deals on rare materials?'],
        rumors: ['I have some rare Tritium crystals, but they do not come cheap.'],
        farewell: ['Safe travels, friend.']
    }),
    mechanic: new WebNPC('Mechanic Jones', 'engineer', 'neutral', {
        greeting: ['Your ship could use some upgrades.'],
        rumors: ['Your engines are running a bit rough. Want me to tune them up?'],
        farewell: ['Come back if you need more work done.']
    })
};

function updateNPCsForEvents(events) {
    events.forEach(event => {
        Object.values(npcDatabase).forEach(npc => {
            if (event === 'market_crash' && npc.type === 'trader') {
                npc.dialogue.rumors.push('The market crash has traders nervous.');
            }
        });
    });
}

// initialize with a sample world event
updateNPCsForEvents(['market_crash']);

// Story content for web version
const storyContent = {
    lore: [
        { topic: 'Genesis Torpedo', content: 'A mythical weapon said to create worlds.' },
        { topic: 'Old Earth', content: 'The birthplace of humanity and center of the Federation.' }
    ]
};

// UI Action Functions (called from buttons)
function executeCommand() {
    if (window.game) {
        window.game.executeCommand();
    }
}

function saveGame() {
    if (window.game) {
        window.game.saveGame();
    }
}

function loadGame() {
    if (window.game) {
        window.game.loadGame();
    }
}

function showHelp() {
    if (window.game) {
        window.game.showHelp();
    }
}

function showSectorMap() {
    if (window.game) {
        window.game.showMap();
    }
}

function showTravelMenu() {
    const modal = new Modal('Travel to Sector', `
        <div class="travel-menu">
            <p>Select destination sector:</p>
            <div class="sector-grid">
                ${Array.from({length: 9}, (_, i) => 
                    `<button class="sector-btn" onclick="travelToSector(${i + 1})">${i + 1}</button>`
                ).join('')}
            </div>
            <p><strong>Fuel Cost:</strong> 10 units per jump</p>
        </div>
    `);
    modal.show();
}

function travelToSector(sector) {
    closeModal();
    if (window.game) {
        window.game.travelToSector(sector);
    }
}

function scanSector() {
    if (window.game) {
        window.game.scanSector();
    }
}

function showMarket() {
    if (window.game) {
        window.game.showMarket();
    }
}

function showTradingPost() {
    const modal = new Modal('Trading Post', `
        <div class="trading-interface">
            <div class="trade-section">
                <h4>Buy Items</h4>
                <div class="trade-controls">
                    <select id="buy-item">
                        <option value="food">Food (50 credits)</option>
                        <option value="iron">Iron (100 credits)</option>
                        <option value="electronics">Electronics (300 credits)</option>
                        <option value="weapons">Weapons (800 credits)</option>
                        <option value="medicine">Medicine (400 credits)</option>
                        <option value="fuel">Fuel (75 credits)</option>
                    </select>
                    <input type="number" id="buy-quantity" value="1" min="1" max="100">
                    <button onclick="buyFromModal()">Buy</button>
                </div>
            </div>
            <div class="trade-section">
                <h4>Sell Items</h4>
                <div class="trade-controls">
                    <select id="sell-item">
                        <option value="food">Food</option>
                        <option value="iron">Iron</option>
                        <option value="electronics">Electronics</option>
                        <option value="weapons">Weapons</option>
                        <option value="medicine">Medicine</option>
                        <option value="fuel">Fuel</option>
                    </select>
                    <input type="number" id="sell-quantity" value="1" min="1" max="100">
                    <button onclick="sellFromModal()">Sell</button>
                </div>
            </div>
        </div>
    `);
    modal.show();
}

function buyFromModal() {
    const item = document.getElementById('buy-item').value;
    const quantity = parseInt(document.getElementById('buy-quantity').value);
    
    if (window.game) {
        window.game.buyItem(item, quantity);
    }
}

function sellFromModal() {
    const item = document.getElementById('sell-item').value;
    const quantity = parseInt(document.getElementById('sell-quantity').value);
    
    if (window.game) {
        window.game.sellItem(item, quantity);
    }
}

function showPriceAnalysis() {
    const modal = new Modal('Price Analysis', `
        <div class="price-analysis">
            <h4>Market Trends</h4>
            <div class="trend-item">
                <span class="item-name">Food</span>
                <span class="price">50 credits</span>
                <span class="trend up">↗ +5%</span>
            </div>
            <div class="trend-item">
                <span class="item-name">Iron</span>
                <span class="price">100 credits</span>
                <span class="trend down">↘ -3%</span>
            </div>
            <div class="trend-item">
                <span class="item-name">Electronics</span>
                <span class="price">300 credits</span>
                <span class="trend stable">→ Stable</span>
            </div>
            <div class="trend-item">
                <span class="item-name">Weapons</span>
                <span class="price">800 credits</span>
                <span class="trend up">↗ +12%</span>
            </div>
        </div>
    `);
    modal.show();
}

function scanForEnemies() {
    if (window.game) {
        window.game.terminal.addLine('SCAN', 'Scanning for hostile contacts...', 'info');
        
        setTimeout(() => {
            const threats = Math.random() > 0.7;
            if (threats) {
                window.game.terminal.addLine('SCAN', '⚠️ Pirates detected in the area!', 'warning');
            } else {
                window.game.terminal.addLine('SCAN', '✅ No hostile contacts detected', 'success');
            }
        }, 2000);
    }
}

function showWeapons() {
    const modal = new Modal('Weapon Systems', `
        <div class="weapons-display">
            <h4>Available Weapons</h4>
            <div class="weapon-item">
                <span class="weapon-name">Laser Cannon</span>
                <span class="weapon-status online">ONLINE</span>
            </div>
            <div class="weapon-item">
                <span class="weapon-name">Plasma Torpedo</span>
                <span class="weapon-status offline">OFFLINE</span>
            </div>
            <div class="weapon-item">
                <span class="weapon-name">Ion Beam</span>
                <span class="weapon-status online">ONLINE</span>
            </div>
        </div>
    `);
    modal.show();
}

function emergencyJump() {
    if (window.game) {
        const randomSector = Math.floor(Math.random() * 9) + 1;
        window.game.terminal.addLine('SYSTEM', '🚨 EMERGENCY JUMP INITIATED!', 'warning');
        setTimeout(() => {
            window.game.travelToSector(randomSector);
        }, 1000);
    }
}

function showMissions() {
    const modal = new Modal('Available Missions', `
        <div class="missions-list">
            <div class="mission-item">
                <h5>Trade Route Security</h5>
                <p>Escort merchant convoy through pirate territory</p>
                <div class="mission-reward">Reward: 2,500 credits</div>
            </div>
            <div class="mission-item">
                <h5>Mineral Survey</h5>
                <p>Survey asteroid field in Sector 7 for rare minerals</p>
                <div class="mission-reward">Reward: 1,800 credits</div>
            </div>
            <div class="mission-item">
                <h5>Rescue Operation</h5>
                <p>Rescue stranded crew from disabled research vessel</p>
                <div class="mission-reward">Reward: 3,200 credits</div>
            </div>
        </div>
    `);
    modal.show();
}

function showActiveMissions() {
    const modal = new Modal('Active Missions', `
        <div class="active-missions">
            <p>No active missions</p>
            <p>Visit the mission board to accept new contracts.</p>
        </div>
    `);
    modal.show();
}

function contactNPCs() {
    const content = Object.entries(npcDatabase).map(([key, npc]) => `
            <div class="npc-item">
                <h5>${npc.name}</h5>
                <p>"${npc.getLine('greeting')}"</p>
                <button onclick="talkToNPC('${key}')">Talk</button>
            </div>
    `).join('');
    const modal = new Modal('NPC Communications', `<div class="npc-list">${content}</div>`);
    modal.show();
}

function talkToNPC(npcKey) {
    closeModal();
    if (window.game) {
        const npc = npcDatabase[npcKey];
        const line = npc.getLine('rumors');
        window.game.terminal.addLine(npc.name, line, 'info');
        npc.adjustRelationship('player', 1);
    }
}

function showLore() {
    const entries = storyContent.lore.map(l => `
        <div class="lore-item">
            <h5>${l.topic}</h5>
            <p>${l.content}</p>
        </div>
    `).join('');
    const modal = new Modal('Galactic Lore', `<div class="lore-list">${entries}</div>`);
    modal.show();
}

// Quick action functions
function refuel() {
    if (window.game) {
        window.game.terminal.addLine('SYSTEM', 'Refueling ship... (+50 fuel)', 'success');
        // In a real implementation, this would make a server request
    }
}

function repair() {
    if (window.game) {
        window.game.terminal.addLine('SYSTEM', 'Repairing ship systems... (+25 health)', 'success');
    }
}

function restockSupplies() {
    if (window.game) {
        window.game.terminal.addLine('SYSTEM', 'Restocking emergency supplies...', 'success');
    }
}

function checkMail() {
    const modal = new Modal('Communications', `
        <div class="mail-list">
            <div class="mail-item unread">
                <h5>From: Federation Command</h5>
                <p>New trade opportunities in the Outer Rim</p>
            </div>
            <div class="mail-item">
                <h5>From: Trader's Guild</h5>
                <p>Market report: Dilithium prices rising</p>
            </div>
            <div class="mail-item">
                <h5>From: Unknown Sender</h5>
                <p>Encrypted message detected...</p>
            </div>
        </div>
    `);
    modal.show();
}

function showMap() {
    if (window.game) {
        window.game.showMap();
    }
}

function showStats() {
    const modal = new Modal('Player Statistics', `
        <div class="stats-display">
            <div class="stat-item">
                <span class="stat-label">Sectors Explored:</span>
                <span class="stat-value">5</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Trade Profit:</span>
                <span class="stat-value">12,450 credits</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Missions Completed:</span>
                <span class="stat-value">3</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Combat Victories:</span>
                <span class="stat-value">7</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Playtime:</span>
                <span class="stat-value">2h 34m</span>
            </div>
        </div>
    `);
    modal.show();
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new GameEngine();
});
