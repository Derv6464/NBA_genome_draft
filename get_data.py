from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

def run():
    options = Options()

    driver = webdriver.Chrome(options=options)
    driver.get("https://nbafantasy.nba.com/statistics")

    wait = WebDriverWait(driver, 10)

    try:
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
        )
        cookie_button.click()
        time.sleep(0.5)
    except:
        pass

    players = []

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

            players.append({
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

    with open("nba_players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(players)} players to nba_players.json")


    print(f"Scraped {len(players)} players")