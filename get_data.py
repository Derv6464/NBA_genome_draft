from bs4 import BeautifulSoup
import requests

url = 'https://nbafantasy.nba.com/statistics'

r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')
table = soup.find_all("td")

print(table)