from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class PokemonDexInfo:
    """Represents base species data, like a Pokédex entry."""
    name: str
    pokedex_no: int
    typing: List[str]
    species: str
    height: str
    weight: str
    base_stats: Dict[str, int]
    abilities: List[str]
    gender_ratio: Optional[float]
    egg_groups: List[str]
    catch_rate: int
    evolution: Optional[List[Dict[str, str]]] = None  # List of evolution conditions
    legendary: bool = False
