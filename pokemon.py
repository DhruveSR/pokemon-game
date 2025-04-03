import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from move import Move


@dataclass
class Pokemon:
    name: str
    typing: List[str]
    level: int
    base_stats: Dict[str, int] = field(default_factory=dict)
    stat_stages: Dict[str, int] = field(default_factory=lambda: {"Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0})
    ability: str
    nature: str
    evs: Dict[str, int] = field(default_factory=lambda: {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0})
    ivs: Dict[str, int] = field(default_factory=lambda: {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0})
    item: Optional[str] = None
    moves: List[Move] = field(default_factory=list)  # Using a list of Move objects instead of a dictionary
    status: Optional[str] = None
    accuracy: float = 1.0
    evasion: float = 1.0
    critical_stage: int = 0
    nature_effect: Dict[str, float] = field(default_factory=dict, init=False)
    initial_stats: Dict[str, int] = field(default_factory=dict, init=False)
    current_stats: Dict[str, int] = field(default_factory=dict, init=False)
    max_hp: int = field(init=False)
    hp: int = field(init=False)


    def __post_init__(self):
        """Runs after initialization to calculate Pokémon stats and HP."""
        self.nature_effect = self.nature_effect_calc(self.nature)  # Apply nature stat effects
        self.initial_stats = self.calc_initial_stats()  # Initial stat calculation
        self.current_stats = self.initial_stats.copy()  # Ensuring separate object
        self.max_hp = self.calc_max_hp()
        self.hp = self.max_hp  # Start with full HP


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


    def calc_max_hp(self):
        """Calculate and return the maximum HP of the Pokémon."""
        if self.name == "Shedinja":
            return 1  # Shedinja always has 1 HP due to its ability
        return int(((2 * self.base_stats["HP"] + self.ivs["HP"] + (self.evs["HP"] // 4)) * self.level / 100) + self.level + 10)


    def calc_initial_stats(self):
        """Calculate and return Pokémon's stats based on base stats, EVs, IVs, level, and nature."""
        def calculate_stat(stat, nature_modifier):
            return int(((2 * self.base_stats[stat] + self.ivs[stat] + (self.evs[stat] // 4)) * self.level / 100 + 5) * nature_modifier)
        
        return {stat: calculate_stat(stat, self.nature_effect[stat]) for stat in ["Atk", "Def", "SpA", "SpD", "Spe"]}


    def stats_change(self, stat, change):
        """Modify a Pokémon's battle stats (attack, defense, speed, etc.) with a given multiplier."""
        self.current_stats[stat] = max(1, int(self.initial_stats[stat]*change))  # Ensures the stat doesn't drop below 1


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


    def take_damage(self, damage):
        """Reduce the Pokémon's HP when taking damage, ensuring it doesn't drop below 0."""
        # Check for Focus Sash (prevents 1-hit KO if at full HP)
        if self.hp == self.max_hp and (self.item == "focus-sash" or (self.item == "focus-band" and random.random() < 0.1)) and damage >= self.hp:
            self.hp = 1
            self.item = None  # Focus Sash is consumed
            print(f"{self.name} held on with its Focus Sash!")
            return
        
        self.hp = max(0, self.hp - damage)
    

    def heal_hp(self, amount: int):
        """Heal the Pokémon, but not beyond its max HP."""
        self.hp = min(self.max_hp, self.hp + amount)
        print(f"{self.name} healed for {amount} HP! Current HP: {self.hp}/{self.max_hp}")


    def is_fainted(self):
        """Check if the Pokémon has fainted (i.e., its HP has reached 0)."""
        return self.hp == 0


    def __str__(self):
            """Return a detailed string representation of the Pokémon."""
            info = f"{self.name} (Level {self.level})\n"
            info += f"Type: {', '.join(self.typing)}\n"
            info += f"HP: {self.hp}/{self.max_hp}\n"
            
            if self.status:
                info += f"Status: {self.status}\n"

            info += "Stats:\n"
            for stat, value in self.current_stats.items():
                info += f"  {stat}: {value}\n"

            info += f"Accuracy: {self.accuracy:.2f}, Evasion: {self.evasion:.2f}, Crit Stage: {self.critical_hit}\n"
            
            if self.item:
                info += f"Item: {self.item}\n"

            if self.moves:
                info += "Moves:\n"
                for move in self.moves:
                    info += f"  {move}\n"

            return info.strip()


    def check_item_use(self, opp, when):
        """Check and apply effects of held items at different battle stages (e.g., switch-in, attack, defend, end of turn)."""
        if self.item:
            if self.item["name"] == "leftovers" and when == "end":
                self.hp = min(self.max_hp, self.hp + self.max_hp // 16)  # Restores 1/16 of max HP at the end of turn

            elif self.item["name"] == "black-sludge" and when == "end":
                if "poison" in self.typing:
                    self.hp = min(self.max_hp, self.hp + self.max_hp // 16)  # Heals if Poison-type
                else:
                    self.take_damage(self.max_hp // 16)  # Damages non-Poison types

            elif self.item["name"] == "choice-band" and when == "switch":
                self.current_stats["attack"] = int(self.current_stats["attack"] * 1.5)  # Boosts Attack by 50%

            elif self.item["name"] == "choice-scarf" and when == "switch":
                self.current_stats["speed"] = int(self.current_stats["speed"] * 1.5)  # Boosts Speed by 50%

            elif self.item["name"] == "choice-specs" and when == "switch":
                self.current_stats["sp_attack"] = int(self.current_stats["sp_attack"] * 1.5)  # Boosts Special Attack by 50%

            elif self.item["name"] == "assault-vest" and when == "switch":
                self.current_stats["sp_defense"] = int(self.current_stats["sp_defense"] * 1.5)  # Boosts Special Defense by 50%

            elif self.item["name"] == "white-herb" and not self.item["used"]:
                # Restores stats that were lowered once
                initial_stat = self.calc_initial_stats()
                for stat in self.current_stats.keys():
                    if self.current_stats[stat] < initial_stat[stat]:  # If a stat is lower than its original value
                        self.current_stats[stat] = initial_stat[stat]
                        self.item["used"] = True
                        break

            elif self.item["name"] == "sitrus-berry" and not self.item["used"]:
                if self.hp < self.max_hp // 2:
                    self.hp = min(self.max_hp, self.hp + self.max_hp // 4)  # Heals 1/4 max HP when below 50% HP
                    self.item["used"] = True

            elif self.item["name"] == "lum-berry" and not self.item["used"]:
                if self.status is not None:
                    self.status = None  # Cures any status condition
                    self.item["used"] = True

            elif self.item["name"] == "clear-amulet":
                # Prevents stat reductions
                initial_stat = self.calc_initial_stats()
                for stat in self.current_stats.keys():
                    if self.current_stats[stat] < initial_stat[stat]:
                        self.current_stats[stat] = initial_stat[stat]

            elif self.item["name"] == "life-orb" and when == "switch":
                for move in self.moves.keys():
                    self.moves[move]["power"] = int(self.moves[move]["power"]*1.3)

            elif self.item["name"] == "rocky-helmet" and when == "defend":
                opp.take_damage(opp.max_hp // 6)  # Deals damage to attackers who use contact moves
                print(f"{opp.name} took {opp.max_hp // 6} damage.")

            elif self.item["name"] == "light-ball" and when == "switch":
                if self.name.lower() == "pikachu":
                    self.current_stats["attack"] = int(self.current_stats["attack"] * 2)  # Doubles Attack for Pikachu
                    self.current_stats["sp_attack"] = int(self.current_stats["sp_attack"] * 2)  # Doubles Special Attack for Pikachu

    def check_ability_use(self, opp, when):
        if when == "initialize":
            self.stab_multiplier = 2  if self.ability == "adaptability" else 1.5  # Boosts STAB (Same-Type Attack Bonus) from 1.5x to 2x  
            self.critical_multiplier = 2.25 if self.ability == "sniper" else 1.5  # Boosts critical hits from 1.5x to 2.25x

            if self.ability == "sheer-force":
                for move in self.moves.keys():
                    self.moves[move]["power"] = int(self.moves[move]["power"]*1.3)

            if self.ability == "technician":
                for move in self.moves.keys():
                    if self.moves[move]["power"] <= 60:
                        self.moves[move]["power"] = int(self.moves[move]["power"]*1.5)

        # Abilities that activate upon switching in
        elif when == "switch":
            if self.ability == "intimidate":
                opp.current_stats["attack"] = max(1, int(opp.current_stats["attack"] * 0.67))  # Lowers enemy Attack by 1 stage

            elif self.ability == "download":
                if opp.current_stats["defense"] < opp.current_stats["sp_defense"]:
                    self.current_stats["attack"] = int(self.current_stats["attack"]*1.5)  # Boosts Attack if opponent has lower Defense
                else:
                    self.current_stats["sp_attack"] = int(self.current_stats["sp_attack"]*1.5)
            
            elif self.ability == "fur coat":
                self.current_stats["defense"] *= 2  # Doubles Defense
        
        # Abilities that activate when defending
        elif when == "defend":
            if self.ability == "rough-skin":
                opp.take_damage(opp.max_hp // 8)  # Deals 1/8 max HP damage if hit by a contact move
                print(f"{opp.name} took {opp.max_hp // 8} damage.")

            elif self.ability == "stamina":
                self.current_stats["defense"] = int(self.current_stats["defense"] * 1.5)  # Boosts Defense when hit

            elif self.ability == "static" and random.random() < 0.3:  # 30% chance to paralyze the attacker
                opp.status = "paralyze"
                opp.current_stats["speed"] = opp.current_stats["spped"]//2
                print(f"{opp.name} was paralyzed due to Static!")

            elif self.ability == "poison-point" and random.random() < 0.3:  # 30% chance to poison the attacker
                opp.status = "poison"
                print(f"{opp.name} was poisoned due to Poison Point!")

        # Abilities that activate at the end of turn
        elif when == "end":
            if self.ability == "self-sufficient":
                self.hp = min(self.max_hp, self.hp + self.max_hp//8)  # Heals 1/3 max HP when switching out

            elif self.ability == "poison-heal" and self.status == "poison":
                self.hp = min(self.max_hp, self.hp + self.max_hp//8)  # Heals instead of taking poison damage

            elif self.ability == "speed-boost":
                self.current_stats["speed"] *= 1.5  # Boosts Speed at the end of each turn  
