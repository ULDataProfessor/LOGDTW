<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOGDTW2002 - Web Edition</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/terminal.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
</head>
<body>
    <div id="game-container">
        <!-- Header -->
        <header class="game-header">
            <div class="header-content">
                <h1 class="game-title">
                    <span class="title-main">LOGDTW2002</span>
                    <span class="title-sub">Legend of the Green Dragon meets TW2002</span>
                </h1>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="saveGame()">💾 Save</button>
                    <button class="btn btn-secondary" onclick="loadGame()">📁 Load</button>
                    <button class="btn btn-info" onclick="showHelp()">❓ Help</button>
                </div>
            </div>
        </header>

        <!-- Main Game Interface -->
        <div class="game-interface">
            <!-- Left Panel - Player Status -->
            <aside class="left-panel">
                <div class="panel status-panel">
                    <h3>🚀 Ship Status</h3>
                    <div class="status-grid">
                        <div class="status-item">
                            <span class="status-label">Captain:</span>
                            <span class="status-value" id="player-name">-</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Ship:</span>
                            <span class="status-value" id="ship-name">-</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Credits:</span>
                            <span class="status-value credits" id="credits">0</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Sector:</span>
                            <span class="status-value" id="current-sector">0</span>
                        </div>
                    </div>
                    
                    <!-- Resource Bars -->
                    <div class="resource-bars">
                        <div class="resource-bar">
                            <label>Health</label>
                            <div class="bar-container">
                                <div class="bar health-bar" id="health-bar" style="width: 0%"></div>
                                <span class="bar-text" id="health-text">0/0</span>
                            </div>
                        </div>
                        
                        <div class="resource-bar">
                            <label>Energy</label>
                            <div class="bar-container">
                                <div class="bar energy-bar" id="energy-bar" style="width: 0%"></div>
                                <span class="bar-text" id="energy-text">0/0</span>
                            </div>
                        </div>
                        
                        <div class="resource-bar">
                            <label>Fuel</label>
                            <div class="bar-container">
                                <div class="bar fuel-bar" id="fuel-bar" style="width: 0%"></div>
                                <span class="bar-text" id="fuel-text">0/0</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Skills Panel -->
                <div class="panel skills-panel">
                    <h3>📊 Skills</h3>
                    <div class="skills-grid" id="skills-grid">
                        <!-- Skills will be populated by JavaScript -->
                    </div>
                </div>

                <!-- Inventory Panel -->
                <div class="panel inventory-panel">
                    <h3>📦 Cargo Hold</h3>
                    <div class="inventory-grid" id="inventory-grid">
                        <div class="inventory-empty">Cargo hold is empty</div>
                    </div>
                </div>
            </aside>

            <!-- Center Panel - Main Game View -->
            <main class="center-panel">
                <div class="terminal-container">
                    <div class="terminal-header">
                        <div class="terminal-buttons">
                            <span class="terminal-button close"></span>
                            <span class="terminal-button minimize"></span>
                            <span class="terminal-button maximize"></span>
                        </div>
                        <div class="terminal-title">Ship Computer Terminal</div>
                    </div>
                    
                    <div class="terminal-screen" id="terminal-screen">
                        <div class="terminal-line">
                            <span class="prompt">SHIP_COMPUTER></span>
                            <span class="terminal-text" id="welcome-text">Welcome aboard, Captain!</span>
                        </div>
                        <div class="terminal-line">
                            <span class="prompt">SHIP_COMPUTER></span>
                            <span class="terminal-text" id="dock-text">Currently docked at Alpha Station.</span>
                        </div>
                        <div class="terminal-line">
                            <span class="prompt">SHIP_COMPUTER></span>
                            <span class="terminal-text">Use the navigation panel to travel to other sectors.</span>
                        </div>
                    </div>
                    
                    <div class="terminal-input">
                        <span class="prompt">CAPTAIN></span>
                        <input type="text" id="terminal-command" placeholder="Enter command..." autocomplete="off">
                        <button onclick="executeCommand()">▶</button>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="action-panel">
                    <div class="action-group">
                        <h4>🚀 Navigation</h4>
                        <div class="action-buttons">
                            <button class="action-btn" onclick="showSectorMap()">Sector Map</button>
                            <button class="action-btn" onclick="showTravelMenu()">Jump to Sector</button>
                            <button class="action-btn" onclick="scanSector()">Scan Area</button>
                        </div>
                    </div>
                    
                    <div class="action-group">
                        <h4>💰 Trading</h4>
                        <div class="action-buttons">
                            <button class="action-btn" onclick="showMarket()">Market</button>
                            <button class="action-btn" onclick="showTradingPost()">Trading Post</button>
                            <button class="action-btn" onclick="showPriceAnalysis()">Price Analysis</button>
                        </div>
                    </div>
                    
                    <div class="action-group">
                        <h4>⚔️ Combat</h4>
                        <div class="action-buttons">
                            <button class="action-btn" onclick="scanForEnemies()">Scan for Hostiles</button>
                            <button class="action-btn" onclick="showWeapons()">Weapons</button>
                            <button class="action-btn" onclick="emergencyJump()">Emergency Jump</button>
                        </div>
                    </div>
                    
                    <div class="action-group">
                        <h4>📋 Missions</h4>
                        <div class="action-buttons">
                            <button class="action-btn" onclick="showMissions()">Available Missions</button>
                            <button class="action-btn" onclick="showActiveMissions()">Active Missions</button>
                            <button class="action-btn" onclick="contactNPCs()">Contact NPCs</button>
                            <button class="action-btn" onclick="showLore()">Lore &amp; History</button>
                        </div>
                    </div>
                </div>
            </main>

            <!-- Right Panel - Context Information -->
            <aside class="right-panel">
                <div class="panel sector-info-panel">
                    <h3>🌌 Sector Information</h3>
                    <div id="sector-info">
                        <div class="info-item">
                            <strong>Current Sector:</strong> <span id="sector-info-current">0</span>
                        </div>
                        <div class="info-item">
                            <strong>Location:</strong> Alpha Station
                        </div>
                        <div class="info-item">
                            <strong>Faction:</strong> Federation
                        </div>
                        <div class="info-item">
                            <strong>Danger Level:</strong> <span class="danger-low">Low</span>
                        </div>
                        <div class="info-item">
                            <strong>Services:</strong> Trading, Repairs, Fuel
                        </div>
                    </div>
                </div>

                <div class="panel news-panel">
                    <h3>📰 Galactic News</h3>
                    <div class="news-feed">
                        <div class="news-item">
                            <div class="news-date">Turn <span id="turn-counter">0</span></div>
                            <div class="news-text">Trade routes to Sector 7 experiencing increased pirate activity.</div>
                        </div>
                        <div class="news-item">
                            <div class="news-date">Turn <span id="turn-counter-1">0</span></div>
                            <div class="news-text">New mining operation discovered rare minerals in Sector 12.</div>
                        </div>
                        <div class="news-item">
                            <div class="news-date">Turn <span id="turn-counter-2">0</span></div>
                            <div class="news-text">Federation patrol increases security in core sectors.</div>
                        </div>
                    </div>
                </div>

                <div class="panel quick-actions-panel">
                    <h3>⚡ Quick Actions</h3>
                    <div class="quick-actions">
                        <button class="quick-btn" onclick="refuel()" title="Refuel Ship">⛽ Refuel</button>
                        <button class="quick-btn" onclick="repair()" title="Repair Ship">🔧 Repair</button>
                        <button class="quick-btn" onclick="restockSupplies()" title="Restock Supplies">📦 Restock</button>
                        <button class="quick-btn" onclick="checkMail()" title="Check Messages">✉️ Mail</button>
                        <button class="quick-btn" onclick="showMap()" title="Galaxy Map">🗺️ Map</button>
                        <button class="quick-btn" onclick="showStats()" title="Statistics">📈 Stats</button>
                    </div>
                </div>
            </aside>
        </div>
    </div>

    <!-- Modal Dialogs -->
    <div id="modal-overlay" class="modal-overlay" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="modal-title">Modal Title</h3>
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            <div class="modal-body" id="modal-body">
                Modal content goes here
            </div>
            <div class="modal-footer" id="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">Close</button>
            </div>
        </div>
    </div>

    <script src="js/game.js"></script>
    <script src="js/terminal.js"></script>
    <script src="js/ui.js"></script>
</body>
</html>
