import sqlite3
import requests

def create_pokemon_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pokemon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type1 TEXT NOT NULL,
        type2 TEXT,  
        base_hp INTEGER NOT NULL,
        base_attack INTEGER NOT NULL,
        base_defense INTEGER NOT NULL,
        base_sp_attack INTEGER NOT NULL,
        base_sp_defense INTEGER NOT NULL,
        base_speed INTEGER NOT NULL,
        ability1 TEXT NOT NULL,   -- First possible ability
        ability2 TEXT,            -- Second possible ability (optional)
        ability3 TEXT       -- Hidden ability (optional)
    );
    """)
    conn.commit()


def fetch_pokemon_data(pokemon_no):
    """Fetch Pokémon data from PokéAPI and pretty print the JSON."""
    url = f"https://pokeapi.co/api/v2/pokemon/{str(pokemon_no)}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # print(json.dumps(data, indent=4))  # Pretty print the JSON
        return data
    else:
        print(f"Error: {response.status_code} - Could not fetch data for {pokemon_no}")
        return None


def insert_pokemon_into_db(poke_no):
    """Extract relevant data and insert Pokémon into the database."""
    
    # Example Usage:
    pokemon_data = fetch_pokemon_data(poke_no)
    if not pokemon_data:
        return
    
    name = pokemon_data["name"]

    type1 = pokemon_data["types"][0]["type"]["name"]
    type2 = pokemon_data["types"][1]["type"]["name"] if len(pokemon_data["types"]) == 2 else None

    base_hp = pokemon_data["stats"][0]["base_stat"]
    base_attack = pokemon_data["stats"][1]["base_stat"]
    base_defense = pokemon_data["stats"][2]["base_stat"]
    base_sp_attack = pokemon_data["stats"][3]["base_stat"]
    base_sp_defense = pokemon_data["stats"][4]["base_stat"]
    base_speed = pokemon_data["stats"][5]["base_stat"]

    ability1 = pokemon_data["abilities"][0]["ability"]["name"]
    ability2 = pokemon_data["abilities"][1]["ability"]["name"] if len(pokemon_data["abilities"]) > 1   else None
    ability3 = pokemon_data["abilities"][2]["ability"]["name"] if len(pokemon_data["abilities"]) > 2   else None

    try:
        cursor.execute("""
            INSERT INTO Pokemon (name, type1, type2, base_hp, base_attack, base_defense, base_sp_attack, 
                                base_sp_defense, base_speed, ability1, ability2, ability3) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, type1, type2, base_hp, base_attack, base_defense, base_sp_attack, 
              base_sp_defense, base_speed, ability1, ability2, ability3))

        conn.commit()
        print(f"Inserted {name} into database successfully!")

    except sqlite3.IntegrityError:
        print(f"Pokemon {name} already exists in the database. Skipping...")


if __name__ == "__main__":
    # Connect to SQLite (or create the database if it doesn't exist)
    conn = sqlite3.connect("pokemon_db.sqlite")
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    create_pokemon_table()

    for i in range(1, 152):
        insert_pokemon_into_db(i)
    
    # create_pokemon_moves_table()

    print("Database and tables created successfully!")