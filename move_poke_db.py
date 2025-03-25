import sqlite3
import requests

# Connect to SQLite database
conn = sqlite3.connect("pokemon.db")
cursor = conn.cursor()

# Create the pokemon_move_db table
def create_pokemon_move_table():
    cursor.execute("""
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
    conn.commit()

# Retrieve all Pokémon IDs and Names from Pokemon table
def get_all_pokemon():
    cursor.execute("SELECT id, name FROM Pokemon")
    return cursor.fetchall()  # Returns a list of (pokemon_id, pokemon_name)

# Fetch moves for a specific Pokémon and insert into pokemon_move_db
def fetch_and_store_pokemon_moves(pokemon_id, pokemon_name):
    url = "https://pokeapi.co/api/v2/pokemon/" + str(pokemon_id)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for Pokémon ID {pokemon_id}")
        return

    data = response.json()

    for move in data["moves"]:
        move_name = move["move"]["name"]

        # Check if move exists in Moves table
        cursor.execute("SELECT id FROM Moves WHERE name = ?", (move_name,))
        move_entry = cursor.fetchone()

        if move_entry:
            move_id = move_entry[0]

            # Insert into pokemon_move_db if the relation doesn't already exist
            cursor.execute("""
                INSERT INTO pokemon_move_db (pokemon_id, pokemon_name, move_id, move_name) 
                VALUES (?, ?, ?, ?)
            """, (pokemon_id, pokemon_name, move_id, move_name))

    conn.commit()

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
    cursor.execute("SELECT * FROM pokemon_move_db LIMIT 5")
    rows = cursor.fetchall()

    print("First 5 rows:")
    for row in rows:
        print(row)

    # Get total count of entries
    cursor.execute("SELECT COUNT(*) FROM pokemon_move_db")
    total_count = cursor.fetchone()[0]

    print(f"Total entries in pokemon_move_db: {total_count}")

    # Close the database connection
    conn.close()