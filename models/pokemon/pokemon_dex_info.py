from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class PokemonDexInfo:
    """Represents base species data, like a Pokédex entry."""
    name: str
    pokedex_no: int
    typing: List[str] = field(default_factory=list)  # Pokémon's typing (e.g., Fire, Water)
    species: str
    height: float
    weight: float
    base_stats: Dict[str, int] = field(default_factory=dict)  # HP, Atk, Def, etc.
    abilities: List[str] = field(default_factory=list)  # Possible abilities
    ev_yield: Dict[str, int] = field(default_factory=dict)  # Effort Value yield
    catch_rate: int
    base_friendship: int
    base_exp: int
    growth_rate: str
    egg_groups: List[str] = field(default_factory=list)
    gender_ratio: Dict[str, float] = field(default_factory=lambda: {"male": 0.5, "female": 0.5})
    egg_cycle: int
    evolution: Optional[List[Dict[str, any]]] = None  # List of evolution conditions
