import pandas as pd
import requests
from pandas.io.json import json_normalize

COMPETITIONS_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json"
MATCHES_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{}.json"
LINEUPS_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/lineups/{}.json"
EVENTS_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{}.json"

print(
    "Whilst we are keen to share data and facilitate research, we also urge you to be responsible with the data. "
    "Please register your details on https://www.statsbomb.com/resource-centre and read our User Agreement carefully."
)


def get_competitions():
    return pd.read_json(COMPETITIONS_URL)


def get_matches(competition_ids):
    matches = pd.DataFrame()
    for competition_id in competition_ids:
        response = requests.get(MATCHES_URL.format(competition_id))
        matches = matches.append(json_normalize(response.json()), ignore_index=True)
    return matches


def get_match_lineups(match):
    response = requests.get(LINEUPS_URL.format(match.match_id))
    lineups = json_normalize(response.json())
    return lineups.assign(
        match_id=match['match_id'],
        competition_id=match['competition.competition_id'],
        season_id=match['season.season_id']
    )


def get_lineups(matches=None):
    if matches is None:
        competitions = get_competitions()
        matches = get_matches(competitions.competition_id.unique())

    lineups = pd.DataFrame()
    for _, match in matches.iterrows():
        match_lineups = get_match_lineups(match)
        lineups = lineups.append(match_lineups, ignore_index=True)
    return lineups


def get_match_events(match):
    response = requests.get(EVENTS_URL.format(match.match_id))
    events = json_normalize(response.json())
    return events.assign(
        match_id=match['match_id'],
        competition_id=match['competition.competition_id'],
        season_id=match['season.season_id']
    )


def get_events(matches=None):
    if matches is None:
        competitions = get_competitions()
        matches = get_matches(competitions.competition_id.unique())

    events = pd.DataFrame()
    for _, match in matches.iterrows():
        match_events = get_match_events(match)
        events = events.append(match_events, ignore_index=True)
    return events
