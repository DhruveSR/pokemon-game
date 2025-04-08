import random
import sqlite3
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.pokemon.move import Move, create_move
from pokemon_dex_info import PokemonDexInfo
from collections import defaultdict

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
    current_hp: int = field(init=False)


    def __post_init__(self):
        """Post-initialization to set dynamic attributes."""
        # Generate IVs (random 0-31 for each stat)
        self.ivs = {stat: random.randint(0, 31) for stat in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]}

        # Determine if Pokémon is shiny (1% chance)
        self.shiny = random.random() < 0.01  

        # Calculate actual stats
        self.actual_stats = self.calc_initial_stats()

        # Set max HP and current HP
        self.current_hp = self.actual_stats["HP"]

        # Assign moves automatically
        self.assign_moves()


    def nature_effect_calc(self, nature):
        """Applies the nature's effect to the Pokémon's stats using a defaultdict (default = 1.0)."""

        nature_modifiers = {
            "adamant":  defaultdict(lambda: 1.0, {"Atk": 1.1, "SpA": 0.9}),
            "modest":   defaultdict(lambda: 1.0, {"SpA": 1.1, "Atk": 0.9}),
            "jolly":    defaultdict(lambda: 1.0, {"Spe": 1.1, "SpA": 0.9}),
            "bold":     defaultdict(lambda: 1.0, {"Def": 1.1, "Atk": 0.9}),
            "calm":     defaultdict(lambda: 1.0, {"SpD": 1.1, "Atk": 0.9}),
            "careful":  defaultdict(lambda: 1.0, {"SpD": 1.1, "SpA": 0.9}),
            "timid":    defaultdict(lambda: 1.0, {"Spe": 1.1, "Atk": 0.9}),
            "relaxed":  defaultdict(lambda: 1.0, {"Def": 1.1, "Spe": 0.9}),
            "naive":    defaultdict(lambda: 1.0, {"Spe": 1.1, "SpD": 0.9}),
            "brave":    defaultdict(lambda: 1.0, {"Atk": 1.1, "Spe": 0.9}),
            "quiet":    defaultdict(lambda: 1.0, {"SpA": 1.1, "Spe": 0.9}),
            "rash":     defaultdict(lambda: 1.0, {"SpA": 1.1, "SpD": 0.9}),
            "gentle":   defaultdict(lambda: 1.0, {"SpD": 1.1, "Def": 0.9}),
            "hasty":    defaultdict(lambda: 1.0, {"Spe": 1.1, "Def": 0.9}),
            "sassy":    defaultdict(lambda: 1.0, {"SpD": 1.1, "Spe": 0.9}),
            "docile":   defaultdict(lambda: 1.0, {}),
            "hardy":    defaultdict(lambda: 1.0, {}),
            "serious":  defaultdict(lambda: 1.0, {}),
            "bashful":  defaultdict(lambda: 1.0, {}),
            "quirky":   defaultdict(lambda: 1.0, {})
        }

        # Apply multipliers to stats
        nature_effects = nature_modifiers.get(nature, defaultdict(lambda: 1.0, {}))
        return {stat: nature_effects[stat] for stat in ["Atk", "Def", "SpA", "SpD", "Spe"]}

    def calc_initial_stats(self):
        """Calculate and return Pokémon's stats based on base stats, EVs, IVs, level, and nature."""

        def calc_max_hp():
            """Calculate and return the maximum HP of the Pokémon."""
            if self.pokemon_dex_info.name == "Shedinja":
                return 1  # Shedinja always has 1 HP due to its ability
            return int(((2 * self.pokemon_dex_info.base_stats["HP"] + self.ivs["HP"] + (self.evs["HP"] // 4)) * self.level / 100) + self.level + 10)

        def calculate_stat(stat, nature_modifier):
            return int(((2 * self.pokemon_dex_info.base_stats[stat] + self.ivs[stat] + (self.evs[stat] // 4)) * self.level / 100 + 5) * nature_modifier)
        
        nature_effect = self.nature_effect_calc(self.nature)
        initial_stats = {"HP": calc_max_hp()}
        initial_stats.update({stat: calculate_stat(stat, nature_effect[stat]) for stat in ["Atk", "Def", "SpA", "SpD", "Spe"]})
        return initial_stats

    def assign_moves(self):
        """Assigns moves to the Pokémon based on its level and whether it was bred."""
        all_possible_moves = []

        # Ensure moves_list["level_up"] exists before accessing it
        if "level_up" in self.pokemon_dex_info.moves_list:
            for level_up_moves in self.pokemon_dex_info.moves_list["level_up"]:
                if level_up_moves["Lv"] <= self.level:
                    all_possible_moves.append(level_up_moves["move"])

        # Select up to 4 moves at random
        moveset = random.sample(all_possible_moves, min(4, len(all_possible_moves)))

        # Ensure self.moves is initialized before appending
        self.moves = [create_move(move) for move in moveset]