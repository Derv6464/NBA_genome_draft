import json 
class Schedule:
    def __init__(self, schedule_data):
        self.espn_to_nba  = self.read_messed_up_names()
        self.schedule_data = self.make_schedule(schedule_data)

    def read_messed_up_names(self):
        with open(f"data/messed_up_name.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["teams"]

    def make_schedule(self, schedule_data):
        schedule = [[[] for _ in range(7)] for _ in range(26)] 
        for week, week_data in schedule_data.items():
            for day, games in week_data.items():
                teams_playing = []
                for game in games:
                    if len(game.split(" @ ")) < 2:
                        home, away = game.split(' VS ')
                    else: 
                        home, away = game.split(' @ ')
                    teams_playing.append(self.espn_to_nba[home])
                    teams_playing.append(self.espn_to_nba[away])
                schedule[int(week)-1][int(day)-1] = teams_playing

        return schedule


    def get_team_days(self, team, week):
        days_playing = []

        for i, day in enumerate(self.schedule_data[week-1]):
            for teams_playing in day:
                if team in teams_playing:
                    days_playing.append(i+1)
                    break
        return days_playing
