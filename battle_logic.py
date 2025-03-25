import random
import numpy as np
import typeRelation
from collections import defaultdict

# Ensure it's always a defaultdict
typeRelation.type_relation = defaultdict(lambda: defaultdict(lambda: 1), typeRelation.type_relation)

# ---------------------- STATUS DAMAGE FUNCTIONS ---------------------- #

def reset_toxic_counter(self):
    """Reset toxic counter when switching out to avoid stacking damage."""
    if self.status == "badly poison":
        self.toxic_counter = 0

def apply_status_damage(pokemon):
    """Apply residual damage for burn, poison, and badly poisoned status effects."""
    
    if pokemon.status == "burn":
        # Burn deals 1/16 of max HP as damage each turn
        burn_damage = pokemon.max_hp // 16  
        pokemon.take_damage(burn_damage)
        print(f"{pokemon.name} is hurt by its burn! It lost {burn_damage} HP.")

    elif pokemon.status == "poison":
        # Poison deals 1/8 of max HP as damage each turn
        poison_damage = pokemon.max_hp // 8  
        pokemon.take_damage(poison_damage)
        print(f"{pokemon.name} is hurt by poison! It lost {poison_damage} HP.")

    elif pokemon.status == "badly_poison":
        # Badly Poisoned damage increases each turn (1/16 * toxic counter)
        pokemon.toxic_counter += 1  # Increase toxic counter each turn
        toxic_damage = (pokemon.toxic_counter * pokemon.max_hp) // 16  
        pokemon.take_damage(toxic_damage)
        print(f"{pokemon.name} is badly poisoned! It lost {toxic_damage} HP.")


# ---------------------- DAMAGE CALCULATION ---------------------- #

def calculate_damage(attacker, defender, move):
    """Calculate the damage dealt by an attacking Pokémon to a defending Pokémon."""
    
    # Critical hit has a 1/24 base chance, modified by attacker's critical hit stat
    critical = attacker.critical_multiplier if np.random.random() < ((1 / 24) * attacker.critical_hit) else 1
    
    # Determine if move uses physical or special stats
    att_stat = "attack" if move["effective_state"] == "physical" else "sp_attack"
    def_stat = "defense" if move["effective_state"] == "physical" else "sp_defense"
    
    # Calculate attack stat with potential critical hit impact
    A = attacker.current_stats[att_stat] if critical == 1 else attacker.base_stats[att_stat]
    
    # Calculate defense stat with potential critical hit impact
    D = defender.current_stats[def_stat] if critical == 1 else defender.base_stats[def_stat]
    
    # Random damage variation between 0.85x to 1.0x
    random_multiplier = np.random.uniform(0.85, 1.0)

    # STAB (Same Type Attack Bonus) - 1.5x if Pokémon's type matches move's type
    stab = attacker.stab_multiplier if move["type"] in attacker.typing else 1

    # Type effectiveness from typeRelation module
    type_multiplier = 1
    for t in defender.typing:
        type_multiplier *= float(typeRelation.type_relation[move["type"]][t])

    # Burn reduces physical attack damage by 50%
    status = 0.5 if attacker.status == "burn" else 1

    # **Ability Check - Type-Based Boosts (Blaze, Torrent, Overgrow, Swarm)**
    other = 1
    if attacker.hp <= attacker.max_hp // 3:  # If HP is ≤ 1/3
        if (attacker.ability == "blaze" and move["type"] == "fire") or (attacker.ability == "torrent" and move["type"] == "water") or (attacker.ability == "overgrow" and move["type"] == "grass") or (attacker.ability == "swarm" and move["type"] == "bug"):
            other = 1.5
    
    # Final damage calculation
    return int((((((2 * attacker.level)/5) + 2) * move["power"] * (A/D))/50) * critical * random_multiplier * stab * type_multiplier * status * other)


# ---------------------- MOVE EXECUTION ---------------------- #

def perform_move(attacker, defender, move):
    """Execute a Pokémon's move, handling damage, status effects, and stat changes."""
    
    # Skip turn if attacker is asleep or frozen
    if attacker.status in ["sleep", "freeze"]:
        print(f"{attacker.name} is {attacker.status} and can't move!")
        
        # Chance to wake up or thaw out
        attacker.status = np.random.choice([attacker.status, None], p=[0.6, 0.4])
        return

    if attacker.status == "paralyze" and np.random.random() <= 0.3:
        print(f"{attacker.name} is {attacker.status} and can't move!")
        return
    
    if move["multi_hit"]:
        hits = np.random.choice([2, 3, 4, 5], p=[0.375, 0.375, 0.125, 0.125])
        for _ in range(hits):
            if defender.ability == "levitate" and move["type"] == "ground":
                print(f"{defender.name} is immune to Ground-type moves due to Levitate!")

            # **Ability Check - Water Absorb (Heals when hit by Water moves)**
            elif defender.ability == "water absorb" and move["type"] == "water":
                heal_amount = calculate_damage(attacker, defender, move)
                defender.hp = min(defender.max_hp, defender.hp+heal_amount)
                print(f"{defender.name} absorbed the Water move and healed {heal_amount} HP!")
            
            else:
                damage = calculate_damage(attacker, defender, move)
                defender.take_damage(damage)
                print(f"{attacker.name} hit {defender.name} for {damage} damage!")
        return

    # Check if move hits based on accuracy
    if np.random.random() < (move["accuracy"] * attacker.accuracy / defender.evasion):
        # **Ability Check - Levitate (Immunity to Ground moves)**
        if move["power"]:  # If move has power, deal damage

            if defender.ability == "levitate" and move["type"] == "ground":
                print(f"{defender.name} is immune to Ground-type moves due to Levitate!")
                return

            # **Ability Check - Water Absorb (Heals when hit by Water moves)**
            if defender.ability == "water absorb" and move["type"] == "water":
                heal_amount = calculate_damage(attacker, defender, move)
                defender.hp = min(defender.max_hp, defender.hp+heal_amount)
                print(f"{defender.name} absorbed the Water move and healed {heal_amount} HP!")
                return  # No damage dealt

            damage = calculate_damage(attacker, defender, move)
            defender.take_damage(damage)
            print(f"{attacker.name} used {move['name']}! It dealt {damage} damage.")

        # If move changes stats, apply stat changes
        if move["StatChange"]:
            stat_changes = ["attack", "sp_attack", "defense", "sp_defense", "speed"]
            for i, stat in enumerate(stat_changes):
                attacker.stats_change(stat, move["StatChange"][i+1])
                defender.stats_change(stat, move["StatChange"][i+6])

        # If move has a healing effect, heal the attacker
        if move["heals"]:  
            heal_amount = int(attacker.max_hp * move["heals"][1])  
            attacker.hp = min(attacker.max_hp, attacker.hp+heal_amount)
            print(f"{attacker.name} healed for {heal_amount} HP!")

        if move["damage_heals"]:
            heal_amount = calculate_damage(attacker, defender, move)  
            attacker.hp = min(attacker.max_hp, attacker.hp+heal_amount)
            print(f"{attacker.name} healed for {heal_amount} HP!")

        # Apply status condition if possible
        if move["statusChange"] and defender.status is None:
            status_effect = move["statusChange"][0]
            success_chance = move["statusChange"][1]

            # Check if the defender is immune to the status effect
            immune = any(status_effect in typeRelation.STATUS_IMMUNITIES.get(t, []) for t in defender.typing)

            if immune:
                print(f"{defender.name} is immune to {status_effect}!")
            elif np.random.random() < success_chance:  # If not immune, apply status
                defender.status = status_effect
                print(f"{defender.name} is now {status_effect}!")
            else:
                print(f"{move['name']} failed to inflict {status_effect} on {defender.name}!")


# ---------------------- SELECT ORDER ---------------------- #

def select_order(priority1, priority2, speed1, speed2, item1, item2):
    # Check if move priorities are different; the Pokémon with the higher priority moves first
    if priority1 != priority2:
        return [1, 2] if priority1 > priority2 else [2, 1]
    
    # Quick Claw Activation - 20% chance for the holder to move first
    if item1 and item1["name"] == "quick claw" and random.random() < 0.2:
        return [1, 2]  # Pokémon 1 moves first
    if item2 and item2["name"] == "quick claw" and random.random() < 0.2:
        return [2, 1]  # Pokémon 2 moves first

    # Speed check - The Pokémon with the higher speed stat moves first
    if speed1 > speed2:
        return [1, 2] 
    elif speed2 > speed1:
        return [2, 1]    

    # If speeds are equal, the move order is randomly chosen
    return random.choice([[1, 2], [2, 1]])