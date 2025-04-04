import sqlite3
import requests

def create_pokemon_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pokemon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pokedex_no INTEGER NOT NULL,
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
        ability1_text TEXT NOT NULL, -- First ability text
        ability2 TEXT,            -- Second possible ability (optional)
        ability2_text TEXT, -- second ability text
        ability2_isHidden TEXT,  -- True of False
        ability3 TEXT,  -- third ability (optional)
        ability3_text TEXT -- third ability text
        ability3_isHidden TEXT,  -- True of False
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
    

def fetch_ability_text(url):
    response = requests.get(url)

    if response.status_code == 200:
        abilities_data = response.json()
        abilities_data = abilities_data["effect_entries"]
        for ability_data in abilities_data:
            if ability_data["language"]["name"] == "en":
                return ability_data["effect"]
        
        print("Couldn't fetch ability info in english.")
        return None
    
    else:
        print(f"Error: {response.status_code} - Could not fetch data for this ability.")
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
    ability1_text = fetch_ability_text(pokemon_data["abilities"][0]["ability"]["url"])
    ability2 = pokemon_data["abilities"][1]["ability"]["name"] if len(pokemon_data["abilities"]) > 1 else None
    ability2_text = fetch_ability_text(pokemon_data["abilities"][1]["ability"]["url"]) if ability2 else None
    ability3 = pokemon_data["abilities"][2]["ability"]["name"] if len(pokemon_data["abilities"]) > 2 else None
    ability3_text = fetch_ability_text(pokemon_data["abilities"][2]["ability"]["url"]) if ability3 else None

    try:
        cursor.execute("""
            INSERT INTO Pokemon (name, type1, type2, base_hp, base_attack, base_defense, base_sp_attack, base_sp_defense, base_speed, ability1, ability1_text, ability2, ability2_text,  ability3, ability3_text) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, type1, type2, base_hp, base_attack, base_defense, base_sp_attack, base_sp_defense, base_speed, ability1, ability1_text, ability2, ability2_text, ability3, ability3_text))

        conn.commit()
        print(f"Inserted {name} into database successfully!")

    except sqlite3.IntegrityError:
        print(f"Pokemon {name} already exists in the database. Skipping...")


if __name__ == "__main__":
    # Connect to SQLite (or create the database if it doesn't exist)
    conn = sqlite3.connect("database/pokemon_db.sqlite")
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    create_pokemon_table()

    for i in range(1, 152):
        insert_pokemon_into_db(i)
    
    # Print first 5 rows
    cursor.execute("SELECT * FROM pokemon LIMIT 5")
    rows = cursor.fetchall()

    print("First 5 rows:")
    for row in rows:
        print(row)

    # Get total count of entries
    cursor.execute("SELECT COUNT(*) FROM pokemon")
    total_count = cursor.fetchone()[0]

    print(f"Total entries in pokemon: {total_count}")

    print("Database and tables created successfully!")