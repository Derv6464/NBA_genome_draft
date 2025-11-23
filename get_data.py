from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import requests
import os
from datetime import datetime, timedelta, timezone

class DataGenerator:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.ensure_data_folder()
        self.nba_fantasy_url = "https://nbafantasy.nba.com/statistics"
        self.espn_v2_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        self.espn_v3_url = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/"
        self.messed_up_names = self.read_messed_up_names()
        self.players = []
        self.teams = []

    def get_all_info(self):
        print("Fetching player data...")
        self.get_player_data()
        print("Fetching game data...")
        self.get_game_data()
        print("Updating player stats...")
        self.get_player_stats()

    def update_player_stats(self):
        print("Reading existing data...")
        self.teams = self.read_game_data()
        self.players = self.read_player_data()
        print("Updating player stats...")
        self.get_player_stats()

    def get_existing_data(self):
        self.players = self.read_player_data()
        self.teams = self.read_game_data()

    def ensure_data_folder(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def read_player_data(self):
        with open(f"{self.folder_path}/nba_players.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def read_game_data(self):
        with open(f"{self.folder_path}/nba_game.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
        
    def read_messed_up_names(self):
        with open(f"{self.folder_path}/messed_up_name.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def get_player_data(self):
        options = Options()

        driver = webdriver.Chrome(options=options)
        driver.get(self.nba_fantasy_url)

        wait = WebDriverWait(driver, 10)

        try:
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            cookie_button.click()
            time.sleep(0.5)
        except:
            pass

        def parse_page():
            soup = BeautifulSoup(driver.page_source, "html.parser")
            rows = soup.select("table tbody tr")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 6:
                    continue

                player_block = cols[1]

                inner_divs = player_block.select("div > div > div")
                if len(inner_divs) >= 2:
                    name = inner_divs[0].get_text(strip=True)
                    team = inner_divs[2].get_text(strip=True)
                else:
                    name = None
                    team = None

                salary = cols[2].get_text(strip=True)
                selected = cols[3].get_text(strip=True)
                form = cols[4].get_text(strip=True)
                total_points = cols[5].get_text(strip=True)

                self.players.append({
                    "name": name,
                    "id": None,
                    "team": team,
                    "position": None,
                    "salary": salary,
                    "selected": selected,
                    "form": form,
                    "total_points": total_points,
                    "weekly_stats": {}
                })

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        while True:
            parse_page()
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next') and not(@disabled)]"))
                )
                next_button.click()
                time.sleep(0.2)
            except:
                break

        driver.quit()

        with open(f"{self.folder_path}/nba_players.json", "w", encoding="utf-8") as f:
            json.dump(self.players, f, ensure_ascii=False, indent=4)

    def get_week_from_date(self, date_str):
        week1_start = datetime.fromisoformat("2025-10-20").replace(tzinfo=timezone.utc)
        game_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        delta_days = (game_dt - week1_start).days
        if delta_days < 0:
            return 1
        
        week_number = (delta_days // 7) + 1

        if week_number > 25:
            week_number = 25

        return week_number

    def get_game_data(self):
        response = requests.get(self.espn_v2_url)
        data = response.json()
        teams_list = data["sports"][0]["leagues"][0]["teams"]

        for team in teams_list:
            team_id = team["team"]["id"]
            print(f"Fetching schedule for team ID: {team_id}")
            response = requests.get(self.espn_v2_url + f'/{team_id}/schedule?season=2026')
            data = response.json()
            games = data["events"]
            game_dates = {week: [] for week in range(1, 26)}
            for game in games:
                game_date_str = game["date"]
                week_number = self.get_week_from_date(game_date_str)
                game_dates[week_number].append(game['shortName'])

            self.teams.append({
                "id": team["team"]["id"],
                "name": team["team"]["displayName"],
                "abbreviation": team["team"]["abbreviation"],
                "game_dates": game_dates
            })

        with open(f"{self.folder_path}/nba_game.json", "w", encoding="utf-8") as f:
            json.dump(self.teams, f, ensure_ascii=False, indent=4)

    def search_player(self, name):
        for i, player in enumerate(self.players):
            if player["name"] == name:
                return i
            
    def calc_weekly_point(self, weeks_stats):
        ''' ["Minutes","Field Goals Made-Attempted","Field Goal Percentage","3-Point Field Goals Made-Attempted",
            "3-Point Field Goal Percentage","Free Throws Made-Attempted","Free Throw Percentage","Rebounds","Assists",
            "Blocks","Steals","Fouls","Turnovers","Points"
        '''
        total_points = 0
        total_rebounds = 0
        total_assists = 0
        total_steals = 0
        total_blocks = 0
        for stat in weeks_stats:
            total_points += int(stat[13])
            total_rebounds += int(stat[7])
            total_assists += int(stat[8])
            total_steals += int(stat[10])
            total_blocks += int(stat[9])

        fantasy_points = (total_points + total_rebounds + (total_assists*2) + (total_steals*3) + (total_blocks*3))
        return fantasy_points
            
    def make_player_stats(self, data):
        if not data.get("seasonTypes"):
            return {}
        events_list = data["events"]
        event_dict = {}
        game_stats_per_week = {
            week: {
                "total_point": 0,
                "per_game": []
            }
            for week in range(1, 26)
        }

        for event_id, event in events_list.items():
            game_date = event.get("gameDate")
            event_dict[event_id] = game_date

        stats = data["seasonTypes"][0]["categories"]
        for month in stats:
            try:
                if month.get("events"):
                    for events in month["events"]:
                        event_id = events["eventId"]
                        week_number = self.get_week_from_date(event_dict[event_id])
                        game_stats_per_week[week_number]["per_game"].append(events["stats"])
            except Exception as e:
                print(f"Error processing month data: {e}")
                print(data)
                continue

        for week in game_stats_per_week:
            total_fantasy_points = self.calc_weekly_point(game_stats_per_week[week]["per_game"])
            game_stats_per_week[week]["total_point"] = total_fantasy_points

        return game_stats_per_week

    def get_player_stats(self):
        player_not_found = []
        if self.teams and self.players:
            for team in self.teams:
                print(f"Fetching roster for team: {team['name']}")
                roster_request = f"{self.espn_v2_url}/{team['id']}/roster"
                response = requests.get(roster_request)
                data = response.json()
                for player in data["athletes"]:
                    player_index = self.search_player(player["displayName"])
                    if player_index is None:
                        messed_up_name = self.messed_up_names.get(player["displayName"])
                        if messed_up_name:
                            player_index = self.search_player(messed_up_name)
                        else:
                            player_not_found.append(player["displayName"])
                            continue

                    self.players[player_index]["id"] = player["id"]
                    self.players[player_index]["position"] = player["position"]["abbreviation"]
                    stats_request = f"{self.espn_v3_url}{player["id"]}/gamelog?season=2026"
                    stats_response = requests.get(stats_request)
                    stats_data = stats_response.json()
                    game_stats_per_week = self.make_player_stats(stats_data)
                    self.players[player_index]["weekly_stats"] = game_stats_per_week

            with open(f"{self.folder_path}/nba_players.json", "w", encoding="utf-8") as f:
                json.dump(self.players, f, ensure_ascii=False, indent=4)

            print("Players not found in initial data:")
            for name in player_not_found:
                print(name)
