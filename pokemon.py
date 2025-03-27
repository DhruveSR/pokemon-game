import random
from collections import defaultdict

class Pokemon:
    """
    Represents a Pokémon in a battle, including its stats, abilities, items, and battle mechanics.

    Attributes:
        name (str): Name of the Pokémon.
        typing (list of str): The Pokémon's type(s) (e.g., ["Fire"], ["Water", "Flying"]).
        level (int): The level of the Pokémon.
        base_stats (dict): The base stats of the Pokémon (HP, Attack, Defense, etc.).
        ability (str): The Pokémon's ability (e.g., "Levitate", "Intimidate").
        nature (dict): The nature of the Pokémon, which affects stat growth (e.g., {"attack": 1.1, "sp_attack": 0.9}).
        evs (dict): Effort Values (EVs) that affect stat growth.
        ivs (dict): Individual Values (IVs) that determine stat potential.
        item (dict or None): The held item (if any) that provides battle effects.
        moves (dict): A dictionary of available moves with details like power, priority, accuracy, etc.
        status (str or None): The current status condition (e.g., "burn", "paralyze", None if healthy).
        accuracy (float): The Pokémon’s accuracy multiplier.
        evasion (float): The Pokémon’s evasion multiplier.
        critical_hit (int): The Pokémon’s critical hit multiplier (higher values mean more crits).
        toxic_counter: Counter for badly_poison status
        current_stats (dict): The Pokémon's real-time stats during battle.
        max_hp (int): The Pokémon's maximum HP.
        hp (int): The Pokémon’s current HP.
    """
    def __init__(self, name, typing, level, base_stats, ability, nature, evs, ivs, item, moves, status, accuracy, evasion, critical_hit):
        """Initialize a Pokémon with its attributes, including stats, items, and battle-related properties."""
        self.name = name
        self.level = level
        self.typing = typing
        self.base_stats = base_stats
        self.ability = ability
        self.nature = nature
        self.nature_effect = self.nature_effect_calc(self.nature)
        self.evs = evs
        self.ivs = ivs
        self.item = item
        self.moves = moves
        self.status = status
        self.accuracy = accuracy
        self.evasion = evasion
        self.critical_hit = critical_hit
        self.toxic_counter=0
        self.current_stats = self.calc_initial_stats()  # Calculate battle stats
        self.max_hp = self.calc_max_hp()  # Set maximum HP
        self.hp = self.max_hp  # Current HP starts at max
        self.check_ability_use(None, "initialize")


    def nature_effect_calc(self, nature):
        """Applies the nature's effect to the Pokémon's stats using a defaultdict (default = 1.0)."""

        # Nature multipliers
        nature_modifiers = {
            "adamant":  {"attack": 1.1, "sp_attack": 0.9},
            "modest":   {"sp_attack": 1.1, "attack": 0.9},
            "jolly":    {"speed": 1.1, "sp_attack": 0.9},
            "bold":     {"defense": 1.1, "attack": 0.9},
            "calm":     {"sp_defense": 1.1, "attack": 0.9},
            "careful":  {"sp_defense": 1.1, "sp_attack": 0.9},
            "timid":    {"speed": 1.1, "attack": 0.9},
            "relaxed":  {"defense": 1.1, "speed": 0.9},
            "naive":    {"speed": 1.1, "sp_defense": 0.9},
            "brave":    {"attack": 1.1, "speed": 0.9},
            "quiet":    {"sp_attack": 1.1, "speed": 0.9},
            "rash":     {"sp_attack": 1.1, "sp_defense": 0.9},
            "gentle":   {"sp_defense": 1.1, "defense": 0.9},
            "hasty":    {"speed": 1.1, "defense": 0.9},
            "sassy":    {"sp_defense": 1.1, "speed": 0.9},
            "docile":   {},  # Neutral
            "hardy":    {},  # Neutral
            "serious":  {},  # Neutral
            "bashful":  {},  # Neutral
            "quirky":   {}   # Neutral
        }

        # Default all stats to 1.0 (no change)
        effect = defaultdict(lambda: 1.0, nature_modifiers.get(nature.lower(), {}))

        # Apply multipliers to stats
        return {stat: effect[stat] for stat in ["attack", "defense", "sp_attack", "sp_defense", "speed"]}

    def calc_max_hp(self):
        """Calculate and return the maximum HP of the Pokémon."""
        if self.name == "Shedinja":
            return 1  # Shedinja always has 1 HP due to its ability
        return int(((2 * self.base_stats["hp"] + self.ivs["hp"] + (self.evs["hp"] // 4)) * self.level / 100) + self.level + 10)

    def calc_initial_stats(self):
        """Calculate and return the Pokémon's initial stats based on its base stats, EVs, IVs, level, and nature."""
        
        def calculate_stat(stat, nature_modifier):
            return int(((2 * self.base_stats[stat] + self.ivs[stat] + (self.evs[stat] // 4)) * self.level / 100 + 5) * nature_modifier)

        stats = {
            "attack": calculate_stat("attack", self.nature_effect["attack"]),  
            "sp_attack": calculate_stat("sp_attack", self.nature_effect["sp_attack"]),
            "defense": calculate_stat("defense", self.nature_effect["defense"]),
            "sp_defense": calculate_stat("sp_defense", self.nature_effect["sp_defense"]),
            "speed": calculate_stat("speed", self.nature_effect["speed"]),
        }
        return stats

    def stats_change(self, stat, change):
        """Modify a Pokémon's battle stats (attack, defense, speed, etc.) with a given multiplier."""
        self.current_stats[stat] = max(1, int(self.current_stats[stat]*change))  # Ensures the stat doesn't drop below 1

    def other_stats_change(self, other_stat, change):
        """Modify non-basic stats (accuracy, evasion, critical hit chance)."""
        if other_stat == "accuracy":
            self.accuracy *= change
        elif other_stat == "evasion":
            self.evasion *= change
        elif other_stat == "critical_hit":
            self.critical_hit = {2: 3, 3: 12, 4: 24}.get(change, self.critical_hit)  # Adjust critical hit\

    def take_damage(self, damage):
        """Reduce the Pokémon's HP when taking damage, ensuring it doesn't drop below 0."""
        self.hp = max(0, self.hp - damage)

    def is_fainted(self):
        """Check if the Pokémon has fainted (i.e., its HP has reached 0)."""
        return self.hp == 0

    def __str__(self):
        """Return a string representation of the Pokémon, displaying its name and current HP."""
        return f"{self.name} (HP: {self.hp}/{self.max_hp})"

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
