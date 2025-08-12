#!/usr/bin/env python3
"""
Empire/Colony system for LOGDTW2002
Lets the player capture planets and manage policies (farming, industry, defense, research, tax),
and raise soldiers. Produces yields each turn based on policy balance and population.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class OwnedPlanet:
    name: str
    sector: int
    population: int
    morale: float = 0.7  # 0..1
    garrison: int = 0
    policies: Dict[str, int] = field(default_factory=lambda: {
        'agriculture': 30,
        'industry': 30,
        'defense': 20,
        'research': 20,
        'tax': 10  # percentage, does not count toward 100 cap
    })
    storage: Dict[str, float] = field(default_factory=lambda: {
        'food': 0.0,
        'materials': 0.0
    })

    def normalize_policies(self):
        # agriculture+industry+defense+research should add up to 100
        keys = ['agriculture', 'industry', 'defense', 'research']
        total = sum(max(0, int(self.policies.get(k, 0))) for k in keys)
        if total <= 0:
            for k in keys:
                self.policies[k] = 25
            return
        for k in keys:
            self.policies[k] = int(self.policies[k] * 100 / total)

    def tick(self) -> Dict[str, float]:
        """Advance one game turn and return produced yields."""
        self.normalize_policies()
        ag = self.policies['agriculture'] / 100.0
        ind = self.policies['industry'] / 100.0
        dfn = self.policies['defense'] / 100.0
        rch = self.policies['research'] / 100.0
        tax = max(0, min(90, int(self.policies.get('tax', 10)))) / 100.0

        # Base factors from population and morale
        pop_factor = max(0.1, self.population / 1_000_000.0)
        morale_factor = max(0.3, min(1.2, self.morale + 0.1 * (1 - tax)))

        # Production
        food = 50.0 * ag * pop_factor * morale_factor
        materials = 40.0 * ind * pop_factor * morale_factor
        research = 10.0 * rch * pop_factor * morale_factor
        soldiers = int(2.0 * dfn * pop_factor * morale_factor)

        # Morale shifts: high tax reduces morale; high defense and research slightly reduce, agriculture/industry increase
        self.morale += 0.01 * (ag + ind - dfn - rch) - 0.05 * tax
        self.morale = max(0.0, min(1.0, self.morale))

        # Storage
        self.storage['food'] += food
        self.storage['materials'] += materials
        self.garrison += soldiers

        # Credits from tax on gross domestic production
        gdp = food * 2 + materials * 3 + research * 10
        credits = gdp * tax

        return {
            'food': food,
            'materials': materials,
            'research': research,
            'soldiers': float(soldiers),
            'credits': credits
        }


class EmpireSystem:
    def __init__(self):
        self.owned: Dict[str, OwnedPlanet] = {}

    def capture_current_planet(self, player, world) -> Dict:
        loc = world.get_current_location()
        if not loc or loc.location_type != 'planet':
            return {'success': False, 'message': 'You must be at a planet to capture it.'}
        key = f"{loc.name}|{world.current_sector}"
        if key in self.owned:
            return {'success': False, 'message': 'You already control this planet.'}
        # Minimal capture check (could integrate combat or requirements)
        self.owned[key] = OwnedPlanet(
            name=loc.name,
            sector=world.current_sector,
            population=1_000_000 + (world.current_sector * 5000),
            garrison=25
        )
        # Mark ownership on location if field exists
        try:
            loc.owner = player.name
        except Exception:
            pass
        return {'success': True, 'message': f'You have captured {loc.name} in Sector {world.current_sector}.'}

    def set_policy(self, planet_name: str, sector: int, **kwargs) -> Dict:
        key = f"{planet_name}|{sector}"
        p = self.owned.get(key)
        if not p:
            return {'success': False, 'message': 'Planet not found in your empire.'}
        for k, v in kwargs.items():
            if k in ['agriculture', 'industry', 'defense', 'research', 'tax']:
                try:
                    p.policies[k] = int(v)
                except Exception:
                    pass
        p.normalize_policies()
        return {'success': True, 'message': f'Policies updated for {planet_name}.'}

    def raise_soldiers(self, planet_name: str, sector: int, amount: int, player) -> Dict:
        key = f"{planet_name}|{sector}"
        p = self.owned.get(key)
        if not p:
            return {'success': False, 'message': 'Planet not found.'}
        amount = max(0, int(amount))
        # Cost per soldier
        cost = amount * 20
        if getattr(player, 'credits', 0) < cost:
            return {'success': False, 'message': f'Not enough credits. Need {cost}.'}
        player.credits -= cost
        p.garrison += amount
        player.soldiers = getattr(player, 'soldiers', 0) + amount
        return {'success': True, 'message': f'Raised {amount} soldiers on {planet_name}.'}

    def update(self, player, world) -> Dict:
        """Apply one turn of empire production."""
        total = {'food': 0.0, 'materials': 0.0, 'research': 0.0, 'soldiers': 0.0, 'credits': 0.0}
        for p in self.owned.values():
            y = p.tick()
            for k in total:
                total[k] += y[k]
        # Apply to player
        player.credits += int(total['credits'])
        player.soldiers = getattr(player, 'soldiers', 0) + int(total['soldiers'])
        try:
            player.materials['Food'] = player.materials.get('Food', 0) + int(total['food'])
        except Exception:
            pass
        return total

    def status(self) -> List[Dict]:
        out = []
        for p in self.owned.values():
            out.append({
                'name': p.name,
                'sector': p.sector,
                'population': p.population,
                'morale': round(p.morale, 2),
                'garrison': p.garrison,
                'policies': p.policies.copy(),
                'storage': {k: int(v) for k, v in p.storage.items()}
            })
        return out


