import random
from game.dynamic_markets import DynamicMarketSystem, EconomicEvent, EconomicEventData


def test_price_fluctuations():
    random.seed(0)
    market = DynamicMarketSystem()
    market.initialize_sector_economy(1)
    start_price = market.get_sector_prices(1)["Food"]
    for turn in range(1,6):
        market.update_market(turn)
    end_price = market.get_sector_prices(1)["Food"]
    assert start_price != end_price


def test_events_affect_trades():
    random.seed(0)
    market = DynamicMarketSystem()
    market.initialize_sector_economy(1)
    commodity = "Weapons"
    base_price = market.get_sector_prices(1)[commodity]
    template = market.economic_event_templates[EconomicEvent.WAR]
    event = EconomicEventData(
        event_type=EconomicEvent.WAR,
        affected_commodities=template["affected_commodities"],
        price_modifiers=template["price_modifiers"],
        supply_modifiers=template["supply_modifiers"],
        demand_modifiers=template["demand_modifiers"],
        duration=5,
        description=template["description"],
        start_turn=market.current_turn,
    )
    for comm in event.affected_commodities:
        if comm in market.commodities:
            market.commodities[comm].event_modifier = event.price_modifiers.get(comm,1.0)
            market.commodities[comm].supply = int(market.commodities[comm].supply * event.supply_modifiers.get(comm,1.0))
            market.commodities[comm].demand = int(market.commodities[comm].demand * event.demand_modifiers.get(comm,1.0))
    market.active_events.append(event)
    market.update_market(market.current_turn + 1)
    event_price = market.get_sector_prices(1)[commodity]
    assert event_price != base_price
    trade = market.execute_trade(commodity, 1, 1, True)
    # Trade price should reflect increased price due to event
    assert trade["price_per_unit"] > base_price
