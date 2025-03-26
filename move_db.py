import requests
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("move_db.sqlite")
cursor = conn.cursor()

def create_moves_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        power INTEGER,
        accuracy REAL,
        priority INTEGER NOT NULL DEFAULT 0,
        multi_hit INTEGER NOT NULL DEFAULT 0,

        -- User stat multipliers
        stat_user_attack REAL NOT NULL DEFAULT 1,
        stat_user_defense REAL NOT NULL DEFAULT 1,
        stat_user_sp_attack REAL NOT NULL DEFAULT 1,
        stat_user_sp_defense REAL NOT NULL DEFAULT 1,
        stat_user_speed REAL NOT NULL DEFAULT 1,

        -- Opponent stat multipliers
        stat_opp_attack REAL NOT NULL DEFAULT 1,
        stat_opp_defense REAL NOT NULL DEFAULT 1,
        stat_opp_sp_attack REAL NOT NULL DEFAULT 1,
        stat_opp_sp_defense REAL NOT NULL DEFAULT 1,
        stat_opp_speed REAL NOT NULL DEFAULT 1,

        -- Status effects
        status_change TEXT,
        status_chance REAL NOT NULL DEFAULT 0,

        -- Move category
        effective_state TEXT NOT NULL,

        -- Healing percentage
        heals REAL NOT NULL DEFAULT 0,
        
        damage_heals INTEGER NOT NULL DEFAULT 0
    );
    """)

    conn.commit()


def fetch_move_data(move_no):
    """Fetch Pokémon data from PokéAPI and pretty print the JSON."""
    url = f"https://pokeapi.co/api/v2/move/{str(move_no)}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # print(json.dumps(data, indent=4))  # Pretty print the JSON
        return data
    else:
        print(f"Error: {response.status_code} - Could not fetch data for move {move_no}")
        return None


def insert_move_into_db(move_no):
    """Extract relevant data and insert Pokémon into the database."""
    
    # Example Usage:
    move_data = fetch_move_data(move_no)
    if not move_data:
        return
    
    name = move_data["name"]

    move_type = move_data["type"]["name"]

    power = move_data["power"] if move_data["power"] is not None else None

    accuracy = move_data["accuracy"]/100 if move_data["accuracy"] is not None else None

    priority = move_data["priority"]

    multi_hit = 1 if move_data.get("meta", {}).get("max_hits") else 0

    # Initialize stat multipliers for user and opponent
    stat_multipliers = {
        "attack": 1,
        "defense": 1,
        "special-attack": 1,
        "special-defense": 1,
        "speed": 1
    }

    opp_stat_multipliers = {
        "attack": 1,
        "defense": 1,
        "special-attack": 1,
        "special-defense": 1,
        "speed": 1
    }

    # Function to get stat change multiplier
    def get_stat_multiplier(change):
        stat_boosts = {1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0, 5: 3.5, 6: 4.0}
        stat_drops = {1: 2/3, 2: 2/4, 3: 2/5, 4: 2/6, 5: 2/7, 6: 2/8}
        return stat_boosts.get(change, 1.0) if change > 0 else stat_drops.get(abs(change), 1.0)

    # Check if move changes stats
    if "stat_changes" in move_data and move_data["stat_changes"]:
        category = move_data.get("meta", {}).get("category", {}).get("name", "")

        for stat_change in move_data["stat_changes"]:
            stat_name = stat_change["stat"]["name"]
            change_value = stat_change["change"]

            if stat_name in stat_multipliers:
                multiplier = get_stat_multiplier(change_value)

                if category == "net-good-stats":
                    if change_value > 0:
                        stat_multipliers[stat_name] = multiplier
                    else:
                        opp_stat_multipliers[stat_name] = multiplier

                elif category == "damage+raise":
                    stat_multipliers[stat_name] = multiplier

                elif category == "damage+lower":
                    if change_value < 0:
                        opp_stat_multipliers[stat_name] = multiplier  # Opponent stat decrease

    # Unpack variables if needed
    stat_user_attack = stat_multipliers["attack"]
    stat_user_defense = stat_multipliers["defense"]
    stat_user_sp_attack = stat_multipliers["special-attack"]
    stat_user_sp_defense = stat_multipliers["special-defense"]
    stat_user_speed = stat_multipliers["speed"]

    stat_opp_attack = opp_stat_multipliers["attack"]
    stat_opp_defense = opp_stat_multipliers["defense"]
    stat_opp_sp_attack = opp_stat_multipliers["special-attack"]
    stat_opp_sp_defense = opp_stat_multipliers["special-defense"]
    stat_opp_speed = opp_stat_multipliers["speed"]

    # Extract status change if available
    status_change = move_data.get("meta", {}).get("ailment", {}).get("name", None)

    # Override status for "toxic"
    if move_data.get("name") == "toxic":
        status_change = "badly_poison"

    # Extract ailment chance if available
    status_chance = move_data.get("meta", {}).get("ailment_chance", 0)/100
    
    effective_state = move_data["damage_class"]["name"]

    heals = move_data.get("meta", {}).get("healing", 0) / 100
    
    damage_heals = 1 if move_data.get("meta",{}).get("category", {}).get("name", None) == "damage+heal" else 0

    try:
        cursor.execute("""
            INSERT INTO Moves (
                name, type, power, accuracy, priority, multi_hit, stat_user_attack, stat_user_defense, stat_user_sp_attack, stat_user_sp_defense, stat_user_speed, stat_opp_attack, stat_opp_defense, stat_opp_sp_attack, stat_opp_sp_defense, stat_opp_speed, status_change, status_chance, effective_state, heals, damage_heals
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, move_type, power, accuracy, priority, multi_hit, stat_user_attack, stat_user_defense, stat_user_sp_attack, stat_user_sp_defense, stat_user_speed, stat_opp_attack, stat_opp_defense, stat_opp_sp_attack, stat_opp_sp_defense, stat_opp_speed, status_change, status_chance, effective_state, heals, damage_heals
        ))
        conn.commit()
        print(f"Inserted {name} into database successfully!")

    except sqlite3.IntegrityError:
        print(f"move {name} already exists in the database. Skipping...")


if __name__ == "__main__":
    # Connect to SQLite (or create the database if it doesn't exist)
    conn = sqlite3.connect("move_db.sqlite")
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    create_moves_table()

    # Fetch and insert first 100 moves
    for i in range(1, 166):  
        insert_move_into_db(i)

    print("Move database populated successfully!")