from dataclasses import dataclass, field
from typing import Optional, Dict
from models.pokemon.pokemon_ingame import PokemonInGame
import random

@dataclass
class PokemonInBattle:
    """Represents a Pokémon in an active battle, tracking temporary battle-related stats and conditions."""

    pokemon: PokemonInGame  # Reference to the in-game Pokémon
    stat_stages: Dict[str, int] = field(default_factory=lambda: {stat: 0 for stat in ["Atk", "Def", "SpA", "SpD", "Spe", "Acc", "Eva"]})
    current_stats: Dict[str, int] = field(default_factory=dict, init=False)
    
    # Volatile battle effects
    protect_active: bool = False
    confusion_turns: int = 0
    taunt_turns: int = 0
    encore_turns: int = 0
    choice_locked_move: Optional[str] = None
    flinched: bool = False
    recharging: bool = False
    leech_seeded: bool = False
    substitute_hp: int = 0
    status_turn: int = 0
    accuracy: float = 1.0
    evasion: float = 1.0
    critical_stage: int = 0


    def apply_stat_boost(self, stat: str, stages: int):
        """Apply a stat boost or drop within the -6 to +6 range."""
        if stat in self.stat_stages:
            self.stat_stages[stat] = max(-6, min(6, self.stat_stages[stat] + stages))  # Clamp between -6 and +6


    def take_damage(self, damage):
        """Reduce the Pokémon's HP when taking damage, ensuring it doesn't drop below 0."""
        # Check for Focus Sash (prevents 1-hit KO if at full HP)
        if self.pokemon.current_hp == self.pokemon.actual_stats["HP"] and (self.pokemon.item == "focus-sash" or (self.pokemon.item == "focus-band" and random.random() < 0.1) or self.pokemon.ability == "sturdy") and damage >= self.pokemon.current_hp:
            self.pokemon.current_hp = 1
            self.pokemon.item = None if self.pokemon.item == "focus-sash" else self.pokemon.item
            return
        
        self.hp = max(0, self.hp - damage)
    

    def heal_hp(self, amount: int):
        """Heal HP up to the max limit."""
        max_hp = self.pokemon.actual_stats["HP"]
        self.pokemon.current_hp = min(max_hp, self.pokemon.current_hp + amount)


    def apply_status_condition(self, status: str):
        """Set a non-volatile status condition (Burn, Paralysis, etc.)."""
        if self.pokemon.status is None:  # Prevent overwrite unless cleared by moves like Refresh
            self.pokemon.status = status
    

    def other_stats_change(self, other_stat, change):
        """Modify non-basic stats (accuracy, evasion, critical hit stage)."""
        if other_stat == "accuracy":
            self.accuracy *= change
        elif other_stat == "evasion":
            self.evasion *= change
        elif other_stat == "critical_hit":
            self.critical_stage = min(max(self.critical_stage + change, 0), 3) # Default to 100% for stage 3+

    
    def get_crit_chance(self):
        """Returns the crit chance based on the current crit stage."""
        crit_chances = {0: 1/24, 1: 1/8, 2: 1/2, 3: 1.0}
        return crit_chances[self.critical_stage]


    def reset_battle_effects(self):
        """Reset temporary battle effects at the end of battle."""
        self.stat_stages = {stat: 0 for stat in self.stat_stages}
        self.protect_active = False
        self.confusion_turns = 0
        self.taunt_turns = 0
        self.encore_turns = 0
        self.choice_locked_move = None
        self.flinched = False
        self.recharging = False
        self.leech_seeded = False
        self.status_turn = 0
        self.accuracy = 1.0
        self.evasion = 1.0
        self.critical_stage = 1