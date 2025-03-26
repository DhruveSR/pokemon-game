import sqlite3
import requests

def create_item_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        info TEXT NOT NULL
    );
    """)
    conn.commit()


def fetch_item_info(item_url):
    response = requests.get(item_url)
    
    if response.status_code == 200:
        item_data = response.json()
        return item_data["effect_entries"][0]["effect"]
    else:
        print(f"Error: {response.status_code} - Could not fetch data for the item")
        return None
    

def fetch_item_data(i):
    url = "https://pokeapi.co/api/v2/item-attribute/7"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        item_url = data["items"][i]["url"]
        item_name = data["items"][i]["name"]
        item_info = fetch_item_info(item_url)
        return item_name, item_info
    
    else:
        print(f"Error: {response.status_code} - Could not fetch data for this ability.")
        return None


def insert_item_into_db(i):
    
    # Example Usage:
    item_name, item_info = fetch_item_data(i)
    if not item_name:
        return
    
    name = item_name
    info = item_info

    try:
        cursor.execute("""
            INSERT INTO item (name, info) 
            VALUES (?, ?)
        """, (name, info))

        conn.commit()
        print(f"Inserted {name} into database successfully!")

    except sqlite3.IntegrityError:
        print(f"item {name} already exists in the database. Skipping...")


if __name__ == "__main__":
    # Connect to SQLite (or create the database if it doesn't exist)
    conn = sqlite3.connect("database/item_db.sqlite")
    cursor = conn.cursor()

    create_item_table()
    url = "https://pokeapi.co/api/v2/item-attribute/7"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        no_of_items = len(data["items"])
        for i in range(no_of_items):
            insert_item_into_db(i)

        # Print first 5 rows
        cursor.execute("SELECT * FROM item LIMIT 5")
        rows = cursor.fetchall()

        print("First 5 rows:")
        for row in rows:
            print(row)

        # Get total count of entries
        cursor.execute("SELECT COUNT(*) FROM item")
        total_count = cursor.fetchone()[0]

        print(f"Total entries in item: {total_count}")

        print("Database and tables created successfully!")