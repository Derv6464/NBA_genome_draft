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
        self.players = []
        self.teams = []

    def run(self):
        self.get_player_data()
        self.get_game_data()
        # self.testing_api()

    def ensure_data_folder(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

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
                    "team": team,
                    "salary": salary,
                    "selected": selected,
                    "form": form,
                    "total_points": total_points
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
        #week 1 starts on wednesday, so messes with result
        week2_start = datetime.fromisoformat("2025-10-20").replace(tzinfo=timezone.utc)
        game_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        delta_days = (game_dt - week2_start).days
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

    def testing_api():
        roster = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/1/roster"

        player_id = "3948153"
        url = f"https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{player_id}/gamelog"

        response = requests.get(url)
        data = response.json()
        with open("data/nba_game.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


gen = DataGenerator(folder_path="data")
gen.get_game_data()