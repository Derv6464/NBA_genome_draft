import os
import json
import get_data

JSON_FILE = "nba_players.json"

def fetch_data():
    if os.path.exists(JSON_FILE):
        print(f"{JSON_FILE} already exists. Skipping data fetch.")
        return
    
    print("Fetching NBA player data...")
    get_data.run()
    print("Data fetch complete.")

def read_data():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def main():
    fetch_data()
    data = read_data()
    
    print(f"Total players fetched: {len(data)}")
    for player in data[:5]:  
        print(player)


if __name__ == "__main__":
    main()
