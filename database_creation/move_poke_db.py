import sqlite3
import requests

# Connect to both databases
pokemon_conn = sqlite3.connect("database/pokemon_db.sqlite")
pokemon_cursor = pokemon_conn.cursor()

move_conn = sqlite3.connect("database/move_db.sqlite")
move_cursor = move_conn.cursor()

relation_conn = sqlite3.connect("database/pokemon_move_db.sqlite")
relation_cursor = relation_conn.cursor()

# Create the pokemon_move_db table in pokemon_move_db.sqlite
def create_pokemon_move_table():
    relation_cursor.execute("""
    CREATE TABLE IF NOT EXISTS pokemon_move_db (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pokemon_id INTEGER NOT NULL,
        pokemon_name TEXT NOT NULL,
        move_id INTEGER NOT NULL,
        move_name TEXT NOT NULL,
        FOREIGN KEY (pokemon_id) REFERENCES Pokemon(id) ON DELETE CASCADE,
        FOREIGN KEY (move_id) REFERENCES Moves(id) ON DELETE CASCADE
    );
    """)
    relation_conn.commit()

# Retrieve all Pokémon IDs and Names from pokemon_db.sqlite
def get_all_pokemon():
    pokemon_cursor.execute("SELECT id, name FROM Pokemon")
    return pokemon_cursor.fetchall()  # Returns a list of (pokemon_id, pokemon_name)

# Fetch moves for a specific Pokémon and insert into pokemon_move_db
def fetch_and_store_pokemon_moves(pokemon_id, pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for Pokémon ID {pokemon_id}")
        return

    data = response.json()

    for move in data["moves"]:
        move_name = move["move"]["name"]

        # Check if move exists in move_db.sqlite
        move_cursor.execute("SELECT id FROM Moves WHERE name = ?", (move_name,))
        move_entry = move_cursor.fetchone()

        if move_entry:
            move_id = move_entry[0]

            # Insert into pokemon_move_db if the relation doesn't already exist
            relation_cursor.execute("""
                INSERT OR IGNORE INTO pokemon_move_db (pokemon_id, pokemon_name, move_id, move_name) 
                VALUES (?, ?, ?, ?)
            """, (pokemon_id, pokemon_name, move_id, move_name))

    relation_conn.commit()

# Main function to process all Pokémon
def populate_pokemon_moves():
    all_pokemon = get_all_pokemon()
    
    for pokemon_id, pokemon_name in all_pokemon:
        fetch_and_store_pokemon_moves(pokemon_id, pokemon_name)
        print(f"Added moves for {pokemon_name} (ID: {pokemon_id})")

if __name__ == "__main__":
    # Run the functions
    create_pokemon_move_table()
    populate_pokemon_moves()

    # Print first 5 rows
    relation_cursor.execute("SELECT * FROM pokemon_move_db LIMIT 5")
    rows = relation_cursor.fetchall()

    print("First 5 rows:")
    for row in rows:
        print(row)

    # Get total count of entries
    relation_cursor.execute("SELECT COUNT(*) FROM pokemon_move_db")
    total_count = relation_cursor.fetchone()[0]

    print(f"Total entries in pokemon_move_db: {total_count}")

    # Close database connections
    pokemon_conn.close()
    move_conn.close()
    relation_conn.close()
