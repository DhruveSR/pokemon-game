import random
import sqlite3
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from move import Move
from pokemon_dex_info import PokemonDexInfo

def generate_unique_pokemon_id():
    """Generate a unique Pokémon ID that does not exist in the database."""
    conn = sqlite3.connect("game_database.db")  # Connect to your SQLite database
    cursor = conn.cursor()
    
    while True:
        new_id = random.randint(100000, 999999)  # Generate a random ID

        # Check if this ID already exists in the Pokémon table
        cursor.execute("SELECT pokemon_id FROM ingame_pokemon WHERE pokemon_id = ?", (new_id,))
        if not cursor.fetchone():  # If the ID is not found, it's unique
            conn.close()
            return new_id

@dataclass
class PokemonInGame:
    """Represents an individual Pokémon encountered or owned by a trainer."""
    pokemon_dex_info: PokemonDexInfo # Reference to the static species data
    level: int
    nature: str
    ability: str
    item: Optional[str] = None
    evs: Dict[str, int] = field(default_factory=lambda: {stat: 0 for stat in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]})
    original_trainer: str = "Wild"
    exp: int = 0
    status: Optional[str] = None

    pokemon_id: int = field(default_factory=generate_unique_pokemon_id)  # Ensures a unique ID
    moves: List[Move] = field(init=False)
    ivs: Dict[str, int] = field(init=False)
    shiny: bool = field(init=False)
    actual_stats: Dict[str, int] = field(init=False)
    current_hp: int

    def calculate_stats(self) -> Dict[str, int]:
        """Calculates this Pokémon's actual stats."""
        def calc_stat(stat):
            nature_effect = 1.1 if stat in ["Atk", "SpA", "Spe"] else 0.9 if stat in ["Def", "SpD"] else 1.0
            return int(((2 * self.species.base_stats[stat] + self.ivs[stat] + (self.evs[stat] // 4)) * self.level / 100 + 5) * nature_effect)
        
        return {stat: calc_stat(stat) for stat in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]}

    def get_max_hp(self) -> int:
        """Calculates maximum HP."""
        return int(((2 * self.species.base_stats["HP"] + self.ivs["HP"] + (self.evs["HP"] // 4)) * self.level / 100) + self.level + 10)
