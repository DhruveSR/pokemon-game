from pokemon import Pokemon
from trainer import Trainer
from battle_simulation import pokemon_battle
import sqlite3

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

# ---------------------- MOVE RETRIVEVAL FROM DATABASE ---------------------- #

def retrieve_and_format_moves(name):
    conn = sqlite3.connect("database/move_db.sqlite")
    cursor = conn.cursor()

    # print(name)

    #  print first 5 rows
    cursor.execute("SELECT * FROM Moves WHERE name = ?", (name,))
    rows = cursor.fetchall()
    #  print(rows)
    if not rows:
        print(f"{name.capitalize()} is not in the database")
        return 
    
    row = rows[0]
    # print(row)

    name = row[1]
    types = row[2]
    power = row[3]
    accuracy = row[4] if row[4] else 1.0
    priority = row[6]
    multihit = False if row[7]==0 else True

    stat_change = False
    for i in range(8, 18):
        if row[i] != 1.0:
            stat_change = True
            break
    
    if stat_change:
        stat_change_list = [row[8:18]]
    else:
        stat_change_list = None

    status = None if row[18] == "none" else row[18]
    status_chance = 1 if row[19] == 0.0 else row[19]

    statusChange = [status, status_chance] if status else None

    effectiveState = row[20]

    heals = None if row[21] == 0.0 else row[21]

    if row[1] == "rest":
        heals = 1.0

    damageHeals = False if row[22] == 0 else True

    move = {
        "name": name,
        "type": types,
        "power": power,
        "accuracy" : accuracy,
        "priority": priority,
        "multi_hit": multihit,
        "StatChange" : stat_change_list,
        "statusChange": statusChange,
        "effectiveState": effectiveState,
        "heals": heals,
        "damageHeals": damageHeals
    }
    
    return move

# ---------------------- MOVE DEFINITIONS ---------------------- #
moves = {
    "flamethrower": {
        "name": "Flamethrower", "type": "fire", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": None, "statusChange": ["burn", 0.1], "effective_state": "special", "heals": [False]
    },
    "ice beam": {
        "name": "Ice beam", "type": "ice", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False], "statusChange": [True, "freeze", 0.1], "effective_state": "special", "heals": [False]
    },
    "will o wisp": {
        "name": "Will o Wisp", "type": "fire", "power": 0, "accuracy": 0.9, "priority": 1, "multi_hit": False, "doesStatChange": [False], "statusChange": [True, "burn", 0.9], "effective_state": "special", "heals": [False]
    },
    "thunderbolt": {
        "name": "Thunderbolt", "type": "electric", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False], "statusChange": [True, "paralyze", 0.1], "effective_state": "special", "heals": [False]
    },
    "surf": {
        "name": "Surf", "type": "water", "power": 90, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False], "statusChange": [False], "effective_state": "special", "heals": [False]
    },
    "toxic": {
        "name": "Toxic", "type": "poison", "power": 0, "accuracy": 0.9, "priority": 1, "multi_hit": False, "doesStatChange": [False], "statusChange": [True, "badly_poison", 0.9], "effective_state": "special", "heals": [False]
    },
    "recover": {
        "name": "Recover", "type": "normal", "power": 0, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False], "heals": [True, 0.5], "statusChange": [False], "effective_state": "special"
    },
    "earthquake": {
        "name": "Earthquake", "type": "ground", "power": 100, "accuracy": 1.0, "priority": 1, "multi_hit": False, "doesStatChange": [False], "statusChange": [False], "effective_state": "physical", "heals": [False]
    }
}


# ---------------------- POKEMON DEFINITIONS ---------------------- #
charizard = Pokemon(
    name="Charizard",
    typing=["fire", "flying"],
    level=50,
    base_stats={"hp": 78, "attack": 84, "defense": 78, "sp_attack": 109, "sp_defense": 85, "speed": 100},
    ability="blaze",
    nature="jolly",
    evs={"hp": 85, "attack": 80, "defense": 70, "sp_attack": 120, "sp_defense": 75, "speed": 90},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "life-orb"},
    moves={
        "fire-blast": retrieve_and_format_moves("fire-blast"), 
        "earthquake": retrieve_and_format_moves("earthquake"), 
        "body-slam":retrieve_and_format_moves("body-slam"),
        "slash":retrieve_and_format_moves("slash")
        },
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
    nature="quirky",
    evs={"hp": 100, "attack": 70, "defense": 90, "sp_attack": 80, "sp_defense": 120, "speed": 80},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "leftovers"},
    moves={
        "surf": retrieve_and_format_moves("surf"),
        "ice-beam": retrieve_and_format_moves("ice-beam"),
        "body-slam": retrieve_and_format_moves("body-slam"),
        "toxic": retrieve_and_format_moves("toxic")
        },
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

venusaur = Pokemon(
    name="Venusaur",
    typing=["grass", "poison"],
    level=50,
    base_stats={"hp": 80, "attack": 82, "defense": 83, "sp_attack": 100, "sp_defense": 100, "speed": 80},
    ability="overgrow",
    nature="calm",
    evs={"hp": 90, "attack": 70, "defense": 85, "sp_attack": 110, "sp_defense": 95, "speed": 70},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "black-sludge"},
    moves={
        "swords-dance": retrieve_and_format_moves("swords-dance"), 
        "razor-leaf": retrieve_and_format_moves("razor-leaf"), 
        "slash": retrieve_and_format_moves("slash"), 
        "sleep-powder": retrieve_and_format_moves("sleep-powder")
        },
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

pikachu = Pokemon(
    name="Pikachu",
    typing=["electric"],
    level=50,
    base_stats={"hp": 35, "attack": 55, "defense": 40, "sp_attack": 50, "sp_defense": 50, "speed": 90},
    ability="static",
    nature="naive",
    evs={"hp": 50, "attack": 100, "defense": 40, "sp_attack": 90, "sp_defense": 40, "speed": 120},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "light-ball"},
    moves={
        "thunderbolt": retrieve_and_format_moves("thunderbolt"),
        "surf": retrieve_and_format_moves("surf"),
        "quick-attack": retrieve_and_format_moves("quick-attack"),
        "body-slam": retrieve_and_format_moves("body-slam")
        },
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

snorlax = Pokemon(
    name="Snorlax",
    typing=["normal"],
    level=50,
    base_stats={"hp": 160, "attack": 110, "defense": 65, "sp_attack": 65, "sp_defense": 110, "speed": 30},
    ability="thick-fat",
    nature="careful",
    evs={"hp": 200, "attack": 80, "defense": 70, "sp_attack": 60, "sp_defense": 120, "speed": 40},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "leftovers"},
    moves={
        "body-slam": retrieve_and_format_moves("body-slam"),
        "earthquake": retrieve_and_format_moves("earthquake"),
        "ice-beam": retrieve_and_format_moves("ice-beam"),
        "rest": retrieve_and_format_moves("rest")
        },
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

mew = Pokemon(
    name="Mew",
    typing=["psychic"],
    level=50,
    base_stats={"hp": 100, "attack": 100, "defense": 100, "sp_attack": 100, "sp_defense": 100, "speed": 100},
    ability="synchronize",
    nature="bold",
    evs={"hp": 100, "attack": 70, "defense": 100, "sp_attack": 80, "sp_defense": 100, "speed": 90},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "leftovers"},
    moves={
        "psychic": retrieve_and_format_moves("psychic"),
        "swords-dance": retrieve_and_format_moves("swords-dance"), 
        "earthquake": retrieve_and_format_moves("earthquake"), 
        "body-slam": retrieve_and_format_moves("body-slam")
        },
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

mewtwo = Pokemon(
    name="Mewtwo",
    typing=["psychic"],
    level=50,
    base_stats={"hp": 106, "attack": 110, "defense": 90, "sp_attack": 154, "sp_defense": 90, "speed": 130},
    ability="pressure",
    nature="timid",
    evs={"hp": 90, "attack": 70, "defense": 80, "sp_attack": 120, "sp_defense": 80, "speed": 120},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "choice-specs"},
    moves={
        "psychic": retrieve_and_format_moves("psychic"), 
        "shadow ball": retrieve_and_format_moves("shadow ball"), 
        "recover": retrieve_and_format_moves("recover"), 
        "ice beam": retrieve_and_format_moves("ice beam")
        },
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

# alakazam = Pokemon(
#     name="Alakazam",
#     typing=["psychic"],
#     level=50,
#     base_stats={"hp": 55, "attack": 50, "defense": 45, "sp_attack": 135, "sp_defense": 95, "speed": 120},
#     ability="synchronize",
#     nature="modest",
#     evs={"hp": 50, "attack": 40, "defense": 50, "sp_attack": 130, "sp_defense": 90, "speed": 120},
#     ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
#     item={"name": "focus-sash"},
#     moves={"psychic": retrieve_and_format_moves("psychic"], "shadow ball": retrieve_and_format_moves("shadow ball"], "calm mind": retrieve_and_format_moves("calm mind"], "energy ball": retrieve_and_format_moves("energy ball"]},
#     status=None,
#     accuracy=1.0,
#     evasion=1.0,
#     critical_hit=1
# )

# gengar = Pokemon(
#     name="Gengar",
#     typing=["ghost", "poison"],
#     level=50,
#     base_stats={"hp": 60, "attack": 65, "defense": 60, "sp_attack": 130, "sp_defense": 75, "speed": 110},
#     ability="levitate",
#     nature="timid",
#     evs={"hp": 50, "attack": 40, "defense": 50, "sp_attack": 130, "sp_defense": 90, "speed": 120},
#     ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
#     item={"name": "black-sludge"},
#     moves={"shadow ball": retrieve_and_format_moves("shadow ball"], "sludge bomb": retrieve_and_format_moves("sludge bomb"], "thunderbolt": retrieve_and_format_moves("thunderbolt"], "will o wisp": retrieve_and_format_moves("will o wisp"]},
#     status=None,
#     accuracy=1.0,
#     evasion=1.0,
#     critical_hit=1
# )

# gyarados = Pokemon(
#     name="Gyarados",
#     typing=["water", "flying"],
#     level=50,
#     base_stats={"hp": 95, "attack": 125, "defense": 79, "sp_attack": 60, "sp_defense": 100, "speed": 81},
#     ability="intimidate",
#     nature="adamant",
#     evs={"hp": 80, "attack": 120, "defense": 80, "sp_attack": 60, "sp_defense": 90, "speed": 90},
#     ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
#     item={"name": "leftovers"},
#     moves={"waterfall": retrieve_and_format_moves("waterfall"], "dragon dance": retrieve_and_format_moves("dragon dance"], "earthquake": retrieve_and_format_moves("earthquake"], "ice fang": retrieve_and_format_moves("ice fang"]},
#     status=None,
#     accuracy=1.0,
#     evasion=1.0,
#     critical_hit=1
# )

# dragonite = Pokemon(
#     name="Dragonite",
#     typing=["dragon", "flying"],
#     level=50,
#     base_stats={"hp": 91, "attack": 134, "defense": 95, "sp_attack": 100, "sp_defense": 100, "speed": 80},
#     ability="inner-focus",
#     nature="adamant",
#     evs={"hp": 100, "attack": 120, "defense": 90, "sp_attack": 80, "sp_defense": 100, "speed": 90},
#     ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
#     item={"name": "lum-berry", "used": False},
#     moves={"outrage": retrieve_and_format_moves("outrage"], "earthquake": retrieve_and_format_moves("earthquake"], "fire punch": retrieve_and_format_moves("fire punch"], "dragon dance": retrieve_and_format_moves("dragon dance"]},
#     status=None,
#     accuracy=1.0,
#     evasion=1.0,
#     critical_hit=1
# )

# tauros = Pokemon(
    name="Tauros",
    typing=["normal"],
    level=50,
    base_stats={"hp": 75, "attack": 100, "defense": 95, "sp_attack": 40, "sp_defense": 70, "speed": 110},
    ability="intimidate",
    nature="jolly",
    evs={"hp": 80, "attack": 110, "defense": 90, "sp_attack": 50, "sp_defense": 80, "speed": 120},
    ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
    item={"name": "choice-band"},
    moves={"body slam": retrieve_and_format_moves("body slam"], "earthquake": retrieve_and_format_moves("earthquake"], "zen headbutt": retrieve_and_format_moves("zen headbutt"], "rock slide": retrieve_and_format_moves("rock slide"]},
    status=None,
    accuracy=1.0,
    evasion=1.0,
    critical_hit=1
)

# garchomp = Pokemon(
#     name="Garchomp",
#     typing=["dragon", "ground"],
#     level=50,
#     base_stats={"hp": 108, "attack": 130, "defense": 95, "sp_attack": 80, "sp_defense": 85, "speed": 102},
#     ability="rough skin",
#     nature="modest",
#     evs={"hp": 80, "attack": 120, "defense": 90, "sp_attack": 60, "sp_defense": 90, "speed": 120},
#     ivs={"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
#     item={"name": "rocky helmet"},
#     moves={"earthquake": moves["earthquake"], "toxic": moves["toxic"]},
#     status=None,
#     accuracy=1.0,
#     evasion=1.0,
#     critical_hit=1
# )

# ---------------------- TRAINER DEFINITIONS ---------------------- #

trainer1 = Trainer("Ash", [copy_pokemon(snorlax), copy_pokemon(mew)])
trainer2 = Trainer("Misty", [copy_pokemon(blastoise), copy_pokemon(charizard), copy_pokemon(venusaur)])


# ---------------------- START BATTLE ---------------------- #
if __name__ == "__main__":
    pokemon_battle(trainer1, trainer2)
    # import sys
    # move = sys.argv[1]
    # print(retrieve_and_format_moves(move.strip()))