# ---------------------- IMPORTS ---------------------- #
from pokemon import Pokemon
from trainer import Trainer
from battle_simulation import pokemon_battle

# ---------------------- COPY POKEMON ---------------------- #

def copy_pokemon(pokemon):
    return Pokemon(
        name=pokemon.name,
        typing=pokemon.typing,
        level=pokemon.level,
        base_stats=pokemon.base_stats,
        ability=pokemon.ability,
        nature=pokemon.nature,
        evs=pokemon.evs,
        ivs=pokemon.ivs,
        item=pokemon.item,
        moves={move_name: move.copy() for move_name, move in pokemon.moves.items()},  # Avoid shared references
        status=None,  # Reset status on switch-in
        accuracy=1.0,
        evasion=1.0,
        critical_hit=1
    )


# ---------------------- MOVE DEFINITIONS ---------------------- #
moves = {
    "flamethrower": {
        "name": "Flamethrower", "type": "fire", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [True, "burn", 0.1], "effective_state": "special", "heals": [False]
    },
    "ice beam": {
        "name": "Ice beam", "type": "ice", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [True, "freeze", 0.1], "effective_state": "special", "heals": [False]
    },
    "will o wisp": {
        "name": "Will o Wisp", "type": "fire", "power": 0, "accuracy": 0.9, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [True, "burn", 0.9], "effective_state": "special", "heals": [False]
    },
    "thunderbolt": {
        "name": "Thunderbolt", "type": "electric", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [True, "paralyze", 0.1], "effective_state": "special", "heals": [False]
    },
    "surf": {
        "name": "Surf", "type": "water", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [False], "effective_state": "special", "heals": [False]
    },
    "toxic": {
        "name": "Toxic", "type": "poison", "power": 0, "accuracy": 0.9, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [True, "badly_poison", 0.9], "effective_state": "special", "heals": [False]
    },
    "recover": {
        "name": "Recover", "type": "normal", "power": 0, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "heals": [True, 0.5], "statusChange": [False], "effective_state": "special"
    },
    "earthquake": {
        "name": "Earthquake", "type": "ground", "power": 100, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False],
        "statusChange": [False], "effective_state": "physical", "heals": [False]
    }
}


# ---------------------- POKEMON DEFINITIONS ---------------------- #
charizard = Pokemon(
    name="Charizard",
    typing=["fire", "flying"],
    level=50,
    base_stats={"hp": 78, "attack": 84, "defense": 78, "sp_attack": 109, "sp_defense": 85, "speed": 100},
    ability="blaze",
    nature={"attack": 1.0, "sp_attack": 1.1, "defense": 0.9, "sp_defense": 1.0, "speed": 1.0},
    evs={"hp": 85, "attack": 80, "defense": 70, "sp_attack": 120, "sp_defense": 75, "speed": 90},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "life orb"},
    moves={"flamethrower": moves["flamethrower"], "thunderbolt": moves["thunderbolt"], "will o wisp":moves["will o wisp"]},
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

blastoise = Pokemon(
    name="Blastoise",
    typing=["water"],
    level=50,
    base_stats={"hp": 79, "attack": 83, "defense": 100, "sp_attack": 85, "sp_defense": 105, "speed": 78},
    ability="torrent",
    nature={"attack": 1.0, "sp_attack": 1.1, "defense": 1.0, "sp_defense": 1.0, "speed": 0.9},
    evs={"hp": 100, "attack": 70, "defense": 90, "sp_attack": 80, "sp_defense": 120, "speed": 80},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "leftovers"},
    moves={"surf": moves["surf"], "toxic": moves["toxic"], "recover": moves["recover"], "ice beam": moves["ice beam"]},
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

garchomp = Pokemon(
    name="Garchomp",
    typing=["dragon", "ground"],
    level=50,
    base_stats={"hp": 108, "attack": 130, "defense": 95, "sp_attack": 80, "sp_defense": 85, "speed": 102},
    ability="rough skin",
    nature={"attack": 1.1, "sp_attack": 0.9, "defense": 1.0, "sp_defense": 1.0, "speed": 1.0},
    evs={"hp": 80, "attack": 120, "defense": 90, "sp_attack": 60, "sp_defense": 90, "speed": 120},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "rocky helmet"},
    moves={"earthquake": moves["earthquake"], "toxic": moves["toxic"]},
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

# ---------------------- TRAINER DEFINITIONS ---------------------- #

trainer1 = Trainer("Ash", [copy_pokemon(charizard), copy_pokemon(garchomp)])
trainer2 = Trainer("Misty", [copy_pokemon(blastoise), copy_pokemon(charizard), copy_pokemon(garchomp)])


# ---------------------- START BATTLE ---------------------- #
if __name__ == "__main__":
    pokemon_battle(trainer1, trainer2)
