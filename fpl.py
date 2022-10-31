from operator import ge
from re import T
import requests
import json

url = "https://fantasy.premierleague.com/api/"

def get_live_gameweeks():
    gameweeks = []
    ext = "bootstrap-static/"
    response = requests.get(url+ext)
    if response.status_code != 200:
        raise Exception("Reponse code was "+str(response.status_code))
    data = json.loads(response.text)

    for i in data.keys():
        if i == "events":
            for gameweek in data[i]:
                if gameweek.get("finished"):
                    gameweeks.append(gameweek.get("name").strip("Gameweek ").encode("utf-8") )
    return gameweeks

def get_league():
    ext = "leagues-classic/152825/standings/"

    response = requests.get(url+ext)
    if response.status_code != 200:
        raise Exception("Reponse code was "+str(response.status_code))
    data = json.loads(response.text)
    return data

def get_teams(league_data):
    teams = []
    for i in league_data.keys():
        if i == "standings":
            for j in league_data[i].keys():
                if j == "results":
                    for team in league_data[i][j]:
                        teams.append(team)
    return teams

def get_entry_id(team):
    for k in team.keys():
        if k == "entry":
            return team[k]

def get_team_name(team):
     for k in team.keys():
        if k == "entry_name":
            return team[k].encode("utf-8") 

def get_picks(entry_id, gameweek):
    ext = "entry/{}/event/{}/picks/".format(entry_id, gameweek)
    response = requests.get(url+ext)
    if response.status_code != 200:
        raise Exception("Reponse code was "+str(response.status_code))
    data = json.loads(response.text)
    all_picks = []
    for i in data.keys():
        if i == "picks":
            for j in data[i]:
                all_picks.append(j)
    return all_picks

def get_playing_picks(all_picks):
    picks = []
    for i in all_picks:
        for j in i:
            if j == "multiplier" and i[j] > 0:
                picks.append(i)
    return picks

def get_player_ids(picks):
    player_ids = []
    for i in picks:
        for j in i.keys():
            if j == "element":
                player_ids.append(i[j])
    return player_ids

def get_player_gameweek_stats(player_id, gameweek):
    ext = "element-summary/{}/".format(player_id)
    response = requests.get(url+ext)
    if response.status_code != 200:
        raise Exception("Reponse code was "+str(response.status_code))
    data = json.loads(response.text)
    for i in data.keys():
        if i == "history":
            for fixture in data[i]:
                for k in fixture.keys():
                    if k == "round" and fixture[k] == int(gameweek):
                        if type(fixture) == type(None):
                            return None
                        return fixture

def calculate_penalties(fixture):
    yellow_cards = 0
    red_cards = 0
    own_goals = 0
    for i in fixture:
        if i == "yellow_cards":
            yellow_cards += fixture[i]
        if i == "red_cards":
            red_cards += fixture[i]
        if i == "own_goals":
            own_goals += fixture[i]
    penalty = yellow_cards + (red_cards*3) + (own_goals*2)
    return penalty

def main():
    overall_scores = {}
    gameweeks = get_live_gameweeks()
    league_data = get_league()
    teams = get_teams(league_data)
    for gameweek in gameweeks:
        gameweek_scores = {}
        print("Gameweek {}".format(gameweek))
        for team in teams:
            team_name = get_team_name(team)
            entry_id = get_entry_id(team)
            all_picks = get_picks(entry_id, gameweek)
            picks = get_playing_picks(all_picks)
            player_ids = get_player_ids(picks)
            penalty = 0
            for player in player_ids:
                fixture = get_player_gameweek_stats(player, gameweek)
                if fixture == None:
                    continue
                penalty += calculate_penalties(fixture)
            if team_name not in gameweek_scores.keys():
                gameweek_scores[team_name] = penalty
            else:
                gameweek_scores[team_name] += penalty
            
            if team_name not in overall_scores.keys():
                overall_scores[team_name] = penalty
            else:
                overall_scores[team_name] += penalty
        for i in sorted(gameweek_scores, key=gameweek_scores.get, reverse=True):
            print(str(i)+": "+str(gameweek_scores[i]))
        print("\n")

    print("Overall Scores")
    for i in sorted(overall_scores, key=overall_scores.get, reverse=True):
            print(str(i)+": "+str(overall_scores[i]))

main()
