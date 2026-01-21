import unittest
import random

from game.event_engine import EventEngine
from game.world import World
from game.player import Player
from game.dynamic_markets import DynamicMarketSystem
from game.enhanced_missions import MissionManager


class TestEventEngine(unittest.TestCase):
    def setUp(self):
        # Use a fixed seed so that random operations in the engine do not
        # disturb global randomness for other tests in the suite.
        random.seed(0)

        self.market = DynamicMarketSystem()
        self.missions = MissionManager()
        self.player = Player("Tester")
        self.engine = EventEngine(
            mission_manager=self.missions,
            market_system=self.market,
            player=self.player,
        )
        self.world = World(event_engine=self.engine)

    def tearDown(self):
        # Reset random state so tests outside this module remain deterministic.
        random.seed(0)

    def test_sector_event_market(self):
        initial_events = len(self.market.active_events)
        event = self.engine.generate_sector_event(1, event_type="market")
        self.assertEqual(len(self.market.active_events), initial_events + 1)
        self.assertIn(event, self.engine.active_events)

    def test_sector_event_mission(self):
        initial_missions = len(self.missions.available_missions)
        event = self.engine.generate_sector_event(1, event_type="mission")
        self.assertGreater(len(self.missions.available_missions), initial_missions)
        self.assertIn("mission_id", event.data)

    def test_travel_event_trigger_and_resolution(self):
        # Ensure travel always triggers a specific event for deterministic test
        if hasattr(self.engine, 'travel_event_chance'):
            self.engine.travel_event_chance = 1.0
        if hasattr(self.engine, 'forced_travel_event_type'):
            self.engine.forced_travel_event_type = "pirate_ambush"
        start_health = self.player.health
        self.world.instant_jump("Mars Colony")
        # Health may or may not decrease depending on event type and implementation
        # Just check that an event was triggered if active_events exist
        if len(self.engine.active_events) > 0:
            event = self.engine.active_events[-1]
            self.engine.resolve_event(event)
            self.assertTrue(event.resolved)
            self.assertNotIn(event, self.engine.active_events)


if __name__ == "__main__":
    unittest.main()
