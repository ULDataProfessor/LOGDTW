// LOGDTW2002 Web Edition - Main Game Logic

class TerminalManager {
    constructor() {
        this.screen = document.getElementById('terminal-screen');
        this.maxLines = 100;
        this.lineCount = 0;
        
        // Clear initial loading lines
        setTimeout(() => {
            this.clear();
            this.addLine('SYSTEM', 'Terminal initialized successfully', 'success');
        }, 1000);
    }
    
    addLine(prefix, text, type = 'info') {
        if (!this.screen) return;
        
        const line = document.createElement('div');
        line.className = `terminal-line ${type}`;
        
        const prompt = document.createElement('span');
        prompt.className = 'prompt';
        prompt.textContent = `${prefix}>`;
        
        const content = document.createElement('span');
        content.className = 'terminal-text';
        content.textContent = text;
        
        line.appendChild(prompt);
        line.appendChild(content);
        
        this.screen.appendChild(line);
        this.lineCount++;
        
        // Remove old lines if we have too many
        if (this.lineCount > this.maxLines) {
            const firstLine = this.screen.firstChild;
            if (firstLine) {
                this.screen.removeChild(firstLine);
                this.lineCount--;
            }
        }
        
        // Scroll to bottom
        this.screen.scrollTop = this.screen.scrollHeight;
        
        // Add typing effect for system messages
        if (type === 'system') {
            content.classList.add('typing-effect');
        }
    }
    
    addTable(headers, rows) {
        if (!this.screen) return;
        
        const table = document.createElement('table');
        table.className = 'terminal-table';
        
        // Headers
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Rows
        const tbody = document.createElement('tbody');
        rows.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        
        this.screen.appendChild(table);
        this.screen.scrollTop = this.screen.scrollHeight;
    }
    
    addProgressBar(label, percentage) {
        if (!this.screen) return;
        
        const container = document.createElement('div');
        container.innerHTML = `
            <div style="margin: 8px 0; color: var(--accent-text);">${label}</div>
            <div class="terminal-progress">
                <div class="terminal-progress-bar" style="width: ${percentage}%"></div>
                <div class="terminal-progress-text">${percentage}%</div>
            </div>
        `;
        
        this.screen.appendChild(container);
        this.screen.scrollTop = this.screen.scrollHeight;
    }
    
    clear() {
        if (this.screen) {
            this.screen.innerHTML = '';
            this.lineCount = 0;
        }
    }
}

class UIManager {
    constructor() {
        this.lastUpdate = 0;
        this.connectionStatus = 'online';
        this.init();
    }
    
    init() {
        // Update connection status indicator
        this.updateConnectionStatus(true);
        
        // Initialize with loading state
        this.showLoadingState();
    }
    
    showLoadingState() {
        document.getElementById('player-name').textContent = 'Loading...';
        document.getElementById('ship-name').textContent = 'Loading...';
        document.getElementById('credits').textContent = '0';
        document.getElementById('current-sector').textContent = '1';
        
        // Show loading in panels
        const skillsGrid = document.getElementById('skills-grid');
        const inventoryGrid = document.getElementById('inventory-grid');
        
        if (skillsGrid) {
            skillsGrid.innerHTML = '<div class="loading">Loading skills...</div>';
        }
        
        if (inventoryGrid) {
            inventoryGrid.innerHTML = '<div class="inventory-empty">Loading cargo...</div>';
        }
    }
    
    updatePlayerDisplay() {
        if (!window.game || !window.game.player) return;
        
        const player = window.game.player;
        
        // Update basic info
        this.updateElement('player-name', player.name || 'Captain');
        this.updateElement('ship-name', player.ship_name || 'Starfarer');
        this.updateElement('credits', this.formatNumber(player.credits || 0));
        this.updateElement('current-sector', player.current_sector || 1);
        this.updateElement('sector-number', player.current_sector || 1);
        this.updateElement('sector-location', player.current_location || 'Unknown');
        
        // Update resource bars
        this.updateResourceBar('health', player.health || 100, player.max_health || 100);
        this.updateResourceBar('energy', player.energy || 100, player.max_energy || 100);
        this.updateResourceBar('fuel', player.fuel || 100, player.max_fuel || 100);
        
        // Update skills
        this.updateSkills(player.skills || {});
        
        // Update inventory from game data
        if (window.game.inventory) {
            this.updateInventory(window.game.inventory);
        }
        
        // Update turn counter
        this.updateElement('turn-counter', window.game.world?.turn_counter || 0);
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateResourceBar(type, current, max) {
        const bar = document.getElementById(`${type}-bar`);
        const text = document.getElementById(`${type}-text`);
        
        if (bar && text) {
            const percentage = Math.round((current / max) * 100);
            bar.style.width = `${percentage}%`;
            text.textContent = `${current}/${max}`;
            
            // Add warning colors for low resources
            bar.classList.remove('low', 'critical');
            if (percentage < 25) {
                bar.classList.add('critical');
            } else if (percentage < 50) {
                bar.classList.add('low');
            }
        }
    }
    
    updateSkills(skills) {
        const skillsGrid = document.getElementById('skills-grid');
        if (!skillsGrid) return;
        
        skillsGrid.innerHTML = '';
        
        Object.entries(skills).forEach(([skill, level]) => {
            const skillItem = document.createElement('div');
            skillItem.className = 'skill-item';
            skillItem.innerHTML = `
                <span class="skill-name">${skill}</span>
                <span class="skill-level">Level ${level}</span>
            `;
            skillsGrid.appendChild(skillItem);
        });
    }
    
    updateInventory(inventory = []) {
        const inventoryGrid = document.getElementById('inventory-grid');
        if (!inventoryGrid) return;
        
        inventoryGrid.innerHTML = '';
        
        if (!inventory || inventory.length === 0) {
            inventoryGrid.innerHTML = '<div class="inventory-empty">Cargo hold is empty</div>';
            return;
        }
        
        inventory.forEach(item => {
            const inventoryItem = document.createElement('div');
            inventoryItem.className = 'inventory-item';
            inventoryItem.innerHTML = `
                <span class="item-name">${item.name}</span>
                <span class="item-quantity">×${item.quantity}</span>
            `;
            inventoryGrid.appendChild(inventoryItem);
        });
    }
    
    updateMarketSummary(market) {
        const marketSummary = document.getElementById('market-summary');
        if (!marketSummary || !market) return;
        
        marketSummary.innerHTML = '';
        
        if (market.prices) {
            const topItems = Object.entries(market.prices).slice(0, 4);
            topItems.forEach(([item, price]) => {
                const itemDiv = document.createElement('div');
                itemDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>${item}</span>
                        <span class="text-accent">${price} cr</span>
                    </div>
                `;
                marketSummary.appendChild(itemDiv);
            });
        }
        
        if (market.economy) {
            const economyDiv = document.createElement('div');
            economyDiv.innerHTML = `
                <hr style="margin: 8px 0; border-color: var(--border-color);">
                <div><strong>Market:</strong> ${market.economy.market_condition || 'Normal'}</div>
                <div><strong>Wealth:</strong> ${market.economy.wealth_level || 'Medium'}</div>
            `;
            marketSummary.appendChild(economyDiv);
        }
    }
    
    updateSectorInfo(sectorInfo) {
        if (!sectorInfo) return;
        
        this.updateElement('sector-faction', sectorInfo.faction || 'Unknown');
        this.updateElement('planet-count', sectorInfo.planets || 0);
        this.updateElement('station-count', sectorInfo.stations || 0);
        
        const dangerElement = document.getElementById('danger-level');
        if (dangerElement && sectorInfo.danger_level !== undefined) {
            const level = sectorInfo.danger_level;
            let text = 'Low';
            let className = 'danger-low';
            
            if (level >= 4) {
                text = 'High';
                className = 'danger-high';
            } else if (level >= 2) {
                text = 'Medium';
                className = 'danger-medium';
            }
            
            dangerElement.textContent = text;
            dangerElement.className = className;
        }
    }
    
    addNewsItem(text) {
        const newsFeed = document.getElementById('news-feed');
        if (!newsFeed) return;
        
        const newsItem = document.createElement('div');
        newsItem.className = 'news-item';
        newsItem.innerHTML = `
            <div class="news-date">Turn ${window.game.world?.turn_counter || 0}</div>
            <div class="news-text">${text}</div>
        `;
        
        newsFeed.insertBefore(newsItem, newsFeed.firstChild);
        
        // Keep only last 5 news items
        while (newsFeed.children.length > 5) {
            newsFeed.removeChild(newsFeed.lastChild);
        }
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');
        
        if (indicator && text) {
            indicator.className = connected ? 'status-indicator online' : 'status-indicator offline';
            text.textContent = connected ? 'Connected' : 'Disconnected';
        }
        
        this.connectionStatus = connected ? 'online' : 'offline';
    }
    
    showNotification(message, type = 'info') {
        // Create floating notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: var(--panel-bg);
            border: 2px solid var(--accent-text);
            border-radius: var(--border-radius);
            padding: var(--spacing-md);
            z-index: 9999;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    update() {
        // Regular UI updates can go here
        // For example, updating timestamps, checking connection, etc.
    }
}

class Modal {
    constructor(title, content, footer = null) {
        this.title = title;
        this.content = content;
        this.footer = footer;
        this.overlay = document.getElementById('modal-overlay');
    }
    
    show() {
        if (!this.overlay) return;
        
        // Update modal content
        document.getElementById('modal-title').textContent = this.title;
        document.getElementById('modal-body').innerHTML = this.content;
        
        if (this.footer) {
            document.getElementById('modal-footer').innerHTML = this.footer;
        }
        
        // Show modal
        this.overlay.classList.add('active');
        
        // Focus trap
        const focusableElements = this.overlay.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
    
    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    }
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // ESC to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Quick commands
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 's':
                e.preventDefault();
                saveGame();
                break;
            case 'l':
                e.preventDefault();
                loadGame();
                break;
            case 'm':
                e.preventDefault();
                showGalaxyMap();
                break;
        }
    }
});

class GameEngine {
    constructor() {
        this.player = {};
        this.world = {};
        this.terminal = null;
        this.ui = null;
        this.lastUpdate = Date.now();
        this.gameLoop = null;
        this.token = null;
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing LOGDTW2002 Web Edition...');
        
        // Initialize subsystems
        this.terminal = new TerminalManager();
        this.ui = new UIManager();
        
        // Establish session and load initial game state
        this.ensureSession();
        
        // Start game loop
        this.startGameLoop();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ Game initialized successfully');
    }

    ensureSession() {
        this.token = localStorage.getItem('session_token');
        if (this.token) {
            this.loadGameState();
        } else {
            fetch('/api/session', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    this.token = data.token;
                    localStorage.setItem('session_token', this.token);
                    this.loadGameState();
                })
                .catch(err => {
                    console.error('Failed to establish session', err);
                });
        }
    }
    
    loadGameState() {
        // Load player and world state from server
        this.sendRequest('status', 'GET')
            .then(response => {
                if (response.success) {
                    this.player = response.player;
                    this.world = response.world;
                    this.inventory = response.inventory || [];
                    this.skills = response.skills || {};
                    this.reputation = response.reputation || {};
                    
                    this.ui.updatePlayerDisplay();
                    this.ui.updateInventory(this.inventory);
                    this.ui.updateConnectionStatus(true);
                    
                    this.terminal.addLine('SYSTEM', 'Game state loaded successfully', 'success');
                    this.terminal.addLine('SYSTEM', `Welcome aboard, ${this.player.name}!`, 'info');
                    
                    // Load market data
                    this.loadMarketData();
                } else {
                    this.terminal.addLine('ERROR', 'Failed to load game state', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to load game state:', error);
                this.terminal.addLine('ERROR', 'Connection error', 'error');
                this.ui.updateConnectionStatus(false);
            });
    }
    
    loadMarketData() {
        this.sendRequest('market', 'GET')
            .then(response => {
                if (response.success) {
                    this.ui.updateMarketSummary(response);
                }
            })
            .catch(error => {
                console.error('Failed to load market data:', error);
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
        if (isNaN(sector) || sector < 1 || sector > 1000) {
            this.terminal.addLine('ERROR', 'Invalid sector number (1-1000)', 'error');
            return;
        }
        
        if (this.player.fuel < 10) {
            this.terminal.addLine('ERROR', 'Insufficient fuel for jump', 'error');
            return;
        }
        
        this.terminal.addLine('SYSTEM', `Initiating jump to Sector ${sector}...`, 'info');
        
        this.sendRequest('travel', 'POST', { sector: sector })
            .then(response => {
                if (response.success) {
                    this.player = response.player;
                    this.terminal.addLine('SYSTEM', response.message, 'success');
                    this.ui.updatePlayerDisplay();
                    
                    // Update sector info if provided
                    if (response.sector_info) {
                        this.ui.updateSectorInfo(response.sector_info);
                        this.terminal.addLine('SCAN', `Arrived at ${response.sector_info.name || 'Unknown Sector'}`, 'info');
                        this.terminal.addLine('SCAN', `Faction: ${response.sector_info.faction || 'Unknown'}`, 'info');
                        this.terminal.addLine('SCAN', `Danger Level: ${response.sector_info.danger_level || 'Unknown'}`, 'info');
                    }
                    
                    // Handle random events
                    if (response.random_event) {
                        this.handleRandomEvent(response.random_event);
                    }
                    
                    // Add news about the travel
                    this.ui.addNewsItem(`Jumped to Sector ${sector}`);
                    
                    // Auto-scan sector
                    this.scanSector();
                } else {
                    this.terminal.addLine('ERROR', response.message || 'Jump failed', 'error');
                }
            })
            .catch(error => {
                this.terminal.addLine('ERROR', 'Jump failed: Communication error', 'error');
                this.ui.updateConnectionStatus(false);
            });
    }
    
    handleRandomEvent(event) {
        this.terminal.addLine('EVENT', '🎲 Random Event Triggered!', 'warning');
        this.terminal.addLine('EVENT', event.event_name, 'warning');
        this.terminal.addLine('EVENT', event.event_description, 'info');
        
        if (event.outcome) {
            if (event.outcome.message) {
                this.terminal.addLine('EVENT', event.outcome.message, 'info');
            }
            
            // Show effects/rewards/penalties
            if (event.outcome.effects) {
                Object.entries(event.outcome.effects).forEach(([effect, value]) => {
                    this.terminal.addLine('EVENT', `${effect}: -${value}`, 'warning');
                });
            }
            
            if (event.outcome.rewards) {
                Object.entries(event.outcome.rewards).forEach(([reward, value]) => {
                    this.terminal.addLine('EVENT', `${reward}: +${value}`, 'success');
                });
            }
        }
        
        // Add to news feed
        this.ui.addNewsItem(`Random Event: ${event.event_name}`);
        
        // Show notification
        this.ui.showNotification(`Random Event: ${event.event_name}`, 'warning');
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
        // Request market info from the server so we can show current
        // conditions as well as prices.
        this.sendRequest('market_info')
            .then(response => {
                if (!response.success) {
                    this.terminal.addLine('ERROR', 'Market data unavailable', 'error');
                    return;
                }

                const market = response.market || {};
                const condition = (market.market_condition || 'unknown').toUpperCase();
                this.terminal.addLine('MARKET', `=== MARKET (${condition}) ===`, 'info');

                if (market.goods) {
                    market.goods.forEach(good => {
                        this.terminal.addLine('MARKET', `${good.name.padEnd(12)} ${good.price} credits`, 'info');
                    });
                }

                this.terminal.addLine('MARKET', 'Use: buy <item> <quantity> or sell <item> <quantity>', 'info');
            })
            .catch(() => {
                this.terminal.addLine('ERROR', 'Market request failed', 'error');
            });
    }
    
    buyItem(item, quantity) {
        const itemName = this.capitalizeFirst(item);
        
        this.sendRequest('trade', 'POST', {
            item: itemName,
            quantity: quantity,
            trade_action: 'buy'
        })
        .then(response => {
            if (response.success) {
                this.player.credits = response.credits;
                this.inventory = response.inventory;
                this.terminal.addLine('TRADE', response.message, 'success');
                this.ui.updatePlayerDisplay();
                this.ui.updateInventory(this.inventory);
                this.ui.addNewsItem(`Bought ${quantity} ${itemName}`);
                this.ui.showNotification(`Bought ${quantity} ${itemName}`, 'success');
            } else {
                this.terminal.addLine('ERROR', response.message || 'Trade failed', 'error');
            }
        })
        .catch(error => {
            this.terminal.addLine('ERROR', 'Trade failed: Communication error', 'error');
            this.ui.updateConnectionStatus(false);
        });
    }
    
    sellItem(item, quantity) {
        const itemName = this.capitalizeFirst(item);
        
        this.sendRequest('trade', 'POST', {
            item: itemName,
            quantity: quantity,
            trade_action: 'sell'
        })
        .then(response => {
            if (response.success) {
                this.player.credits = response.credits;
                this.inventory = response.inventory;
                this.terminal.addLine('TRADE', response.message, 'success');
                this.ui.updatePlayerDisplay();
                this.ui.updateInventory(this.inventory);
                this.ui.addNewsItem(`Sold ${quantity} ${itemName}`);
                this.ui.showNotification(`Sold ${quantity} ${itemName}`, 'success');
            } else {
                this.terminal.addLine('ERROR', response.message || 'Trade failed', 'error');
            }
        })
        .catch(error => {
            this.terminal.addLine('ERROR', 'Trade failed: Communication error', 'error');
            this.ui.updateConnectionStatus(false);
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
                    if (response.world) {
                        this.world = response.world;
                    }
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
            trade: 'trade',
            market: 'market',
            combat: 'combat',
            missions: 'missions',
            save_game: 'save',
            load_game: 'load',
            galaxy: 'galaxy'
        };

        const endpoint = endpoints[action] || action;
        const apiBase = window.API_BASE || '/api';
        
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        };

        // GET requests for certain endpoints
        if (['get_status', 'market', 'missions', 'galaxy'].includes(action)) {
            options.method = 'GET';
            delete options.body;
        }

        return fetch(`${apiBase}/${endpoint}`, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('Request failed:', error);
                this.updateConnectionStatus(false);
                throw error;
            });
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');
        
        if (indicator && text) {
            indicator.className = connected ? 'status-indicator online' : 'status-indicator offline';
            text.textContent = connected ? 'Connected' : 'Disconnected';
        }
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
