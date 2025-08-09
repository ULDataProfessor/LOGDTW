<?php
session_start();

// Initialize game session if not exists
if (!isset($_SESSION['game_data'])) {
    $_SESSION['game_data'] = [
        'player' => [
            'name' => 'Captain',
            'ship_name' => 'Starfarer',
            'level' => 1,
            'credits' => 1000,
            'health' => 100,
            'max_health' => 100,
            'energy' => 100,
            'max_energy' => 100,
            'fuel' => 100,
            'max_fuel' => 100,
            'experience' => 0,
            'current_sector' => 1
        ],
        'world' => [
            'current_location' => 'Alpha Station',
            'discovered_sectors' => [1],
            'turn_counter' => 0
        ],
        'inventory' => [],
        'skills' => [
            'Combat' => 1,
            'Piloting' => 1,
            'Trading' => 1,
            'Engineering' => 1
        ],
        'missions' => [
            'active' => [],
            'completed' => [],
            'available' => []
        ]
    ];
}

// Handle AJAX requests
if (isset($_POST['action'])) {
    header('Content-Type: application/json');
    
    switch ($_POST['action']) {
        case 'get_status':
            echo json_encode([
                'success' => true,
                'player' => $_SESSION['game_data']['player'],
                'world' => $_SESSION['game_data']['world']
            ]);
            exit;
            
        case 'travel':
            $sector = intval($_POST['sector']);
            if ($sector > 0 && $sector <= 20) {
                $_SESSION['game_data']['player']['current_sector'] = $sector;
                $_SESSION['game_data']['player']['fuel'] -= 10;
                $_SESSION['game_data']['world']['turn_counter']++;
                
                if (!in_array($sector, $_SESSION['game_data']['world']['discovered_sectors'])) {
                    $_SESSION['game_data']['world']['discovered_sectors'][] = $sector;
                }
                
                echo json_encode([
                    'success' => true,
                    'message' => "Jumped to Sector $sector",
                    'player' => $_SESSION['game_data']['player']
                ]);
            } else {
                echo json_encode([
                    'success' => false,
                    'message' => 'Invalid sector'
                ]);
            }
            exit;
            
        case 'trade':
            $item = $_POST['item'];
            $quantity = intval($_POST['quantity']);
            $action = $_POST['trade_action']; // buy or sell
            
            $market_prices = [
                'Food' => 50,
                'Iron' => 100,
                'Electronics' => 300,
                'Weapons' => 800,
                'Medicine' => 400,
                'Fuel' => 75
            ];
            
            if (isset($market_prices[$item])) {
                $price = $market_prices[$item] * $quantity;
                
                if ($action === 'buy') {
                    if ($_SESSION['game_data']['player']['credits'] >= $price) {
                        $_SESSION['game_data']['player']['credits'] -= $price;
                        
                        // Add to inventory
                        $found = false;
                        foreach ($_SESSION['game_data']['inventory'] as &$inv_item) {
                            if ($inv_item['name'] === $item) {
                                $inv_item['quantity'] += $quantity;
                                $found = true;
                                break;
                            }
                        }
                        
                        if (!$found) {
                            $_SESSION['game_data']['inventory'][] = [
                                'name' => $item,
                                'quantity' => $quantity
                            ];
                        }
                        
                        echo json_encode([
                            'success' => true,
                            'message' => "Bought $quantity $item for $price credits",
                            'credits' => $_SESSION['game_data']['player']['credits']
                        ]);
                    } else {
                        echo json_encode([
                            'success' => false,
                            'message' => 'Insufficient credits'
                        ]);
                    }
                } else { // sell
                    // Find item in inventory
                    foreach ($_SESSION['game_data']['inventory'] as &$inv_item) {
                        if ($inv_item['name'] === $item && $inv_item['quantity'] >= $quantity) {
                            $inv_item['quantity'] -= $quantity;
                            $_SESSION['game_data']['player']['credits'] += $price;
                            
                            // Remove item if quantity is 0
                            if ($inv_item['quantity'] <= 0) {
                                $_SESSION['game_data']['inventory'] = array_filter(
                                    $_SESSION['game_data']['inventory'],
                                    function($i) use ($item) { return $i['name'] !== $item; }
                                );
                            }
                            
                            echo json_encode([
                                'success' => true,
                                'message' => "Sold $quantity $item for $price credits",
                                'credits' => $_SESSION['game_data']['player']['credits']
                            ]);
                            exit;
                        }
                    }
                    
                    echo json_encode([
                        'success' => false,
                        'message' => 'Insufficient inventory'
                    ]);
                }
            } else {
                echo json_encode([
                    'success' => false,
                    'message' => 'Invalid item'
                ]);
            }
            exit;
            
        case 'save_game':
            $save_name = $_POST['save_name'] ?? 'quicksave';
            $save_data = json_encode($_SESSION['game_data']);
            file_put_contents("saves/{$save_name}.json", $save_data);
            
            echo json_encode([
                'success' => true,
                'message' => 'Game saved successfully'
            ]);
            exit;
            
        case 'load_game':
            $save_name = $_POST['save_name'] ?? 'quicksave';
            $save_file = "saves/{$save_name}.json";
            
            if (file_exists($save_file)) {
                $save_data = file_get_contents($save_file);
                $_SESSION['game_data'] = json_decode($save_data, true);
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Game loaded successfully',
                    'player' => $_SESSION['game_data']['player']
                ]);
            } else {
                echo json_encode([
                    'success' => false,
                    'message' => 'Save file not found'
                ]);
            }
            exit;
    }
}

?>
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
                            <span class="status-value" id="player-name"><?php echo $_SESSION['game_data']['player']['name']; ?></span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Ship:</span>
                            <span class="status-value" id="ship-name"><?php echo $_SESSION['game_data']['player']['ship_name']; ?></span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Credits:</span>
                            <span class="status-value credits" id="credits"><?php echo number_format($_SESSION['game_data']['player']['credits']); ?></span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Sector:</span>
                            <span class="status-value" id="current-sector"><?php echo $_SESSION['game_data']['player']['current_sector']; ?></span>
                        </div>
                    </div>
                    
                    <!-- Resource Bars -->
                    <div class="resource-bars">
                        <div class="resource-bar">
                            <label>Health</label>
                            <div class="bar-container">
                                <div class="bar health-bar" style="width: <?php echo ($_SESSION['game_data']['player']['health'] / $_SESSION['game_data']['player']['max_health']) * 100; ?>%"></div>
                                <span class="bar-text" id="health-text"><?php echo $_SESSION['game_data']['player']['health']; ?>/<?php echo $_SESSION['game_data']['player']['max_health']; ?></span>
                            </div>
                        </div>
                        
                        <div class="resource-bar">
                            <label>Energy</label>
                            <div class="bar-container">
                                <div class="bar energy-bar" style="width: <?php echo ($_SESSION['game_data']['player']['energy'] / $_SESSION['game_data']['player']['max_energy']) * 100; ?>%"></div>
                                <span class="bar-text" id="energy-text"><?php echo $_SESSION['game_data']['player']['energy']; ?>/<?php echo $_SESSION['game_data']['player']['max_energy']; ?></span>
                            </div>
                        </div>
                        
                        <div class="resource-bar">
                            <label>Fuel</label>
                            <div class="bar-container">
                                <div class="bar fuel-bar" style="width: <?php echo ($_SESSION['game_data']['player']['fuel'] / $_SESSION['game_data']['player']['max_fuel']) * 100; ?>%"></div>
                                <span class="bar-text" id="fuel-text"><?php echo $_SESSION['game_data']['player']['fuel']; ?>/<?php echo $_SESSION['game_data']['player']['max_fuel']; ?></span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Skills Panel -->
                <div class="panel skills-panel">
                    <h3>📊 Skills</h3>
                    <div class="skills-grid">
                        <?php foreach ($_SESSION['game_data']['skills'] as $skill => $level): ?>
                        <div class="skill-item">
                            <span class="skill-name"><?php echo $skill; ?></span>
                            <span class="skill-level">Lv. <?php echo $level; ?></span>
                        </div>
                        <?php endforeach; ?>
                    </div>
                </div>

                <!-- Inventory Panel -->
                <div class="panel inventory-panel">
                    <h3>📦 Cargo Hold</h3>
                    <div class="inventory-grid" id="inventory-grid">
                        <?php if (empty($_SESSION['game_data']['inventory'])): ?>
                        <div class="inventory-empty">Cargo hold is empty</div>
                        <?php else: ?>
                        <?php foreach ($_SESSION['game_data']['inventory'] as $item): ?>
                        <div class="inventory-item">
                            <span class="item-name"><?php echo $item['name']; ?></span>
                            <span class="item-quantity">x<?php echo $item['quantity']; ?></span>
                        </div>
                        <?php endforeach; ?>
                        <?php endif; ?>
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
                            <span class="terminal-text">Welcome aboard, Captain <?php echo $_SESSION['game_data']['player']['name']; ?>!</span>
                        </div>
                        <div class="terminal-line">
                            <span class="prompt">SHIP_COMPUTER></span>
                            <span class="terminal-text">Currently docked at Alpha Station, Sector <?php echo $_SESSION['game_data']['player']['current_sector']; ?></span>
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
                            <strong>Current Sector:</strong> <?php echo $_SESSION['game_data']['player']['current_sector']; ?>
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
                            <div class="news-date">Turn <?php echo $_SESSION['game_data']['world']['turn_counter']; ?></div>
                            <div class="news-text">Trade routes to Sector 7 experiencing increased pirate activity.</div>
                        </div>
                        <div class="news-item">
                            <div class="news-date">Turn <?php echo $_SESSION['game_data']['world']['turn_counter'] - 1; ?></div>
                            <div class="news-text">New mining operation discovered rare minerals in Sector 12.</div>
                        </div>
                        <div class="news-item">
                            <div class="news-date">Turn <?php echo $_SESSION['game_data']['world']['turn_counter'] - 2; ?></div>
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
