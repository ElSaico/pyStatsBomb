import numpy as np
from pandas.io.json import json_normalize


def all_clean(df):
    df = clean_locations(df)
    df = goalkeeper_info(df)
    df = shot_info(df)
    df = freeze_frame_info(df)
    df = format_elapsed_time(df)
    df = possession_info(df)
    return df


def clean_locations(df):
    pass_end_location = df['pass.end_location']
    shot_end_location = df['shot.end_location']
    return df.sort_values(by=['match_id']).assign(**{
        'location.x': df.location.map(lambda l: l[0], na_action='ignore'),
        'location.y': df.location.map(lambda l: l[1], na_action='ignore'),
        'pass.end_location.x': pass_end_location.map(lambda l: l[0], na_action='ignore'),
        'pass.end_location.y': pass_end_location.map(lambda l: l[1], na_action='ignore'),
        'shot.end_location.x': shot_end_location.map(lambda l: l[0], na_action='ignore'),
        'shot.end_location.y': shot_end_location.map(lambda l: l[1], na_action='ignore'),
        'shot.end_location.z': shot_end_location.map(lambda l: l[2] if len(l) < 3 else np.NaN, na_action='ignore'),
    })


def goalkeeper_info(df):
    def get_goalkeeper(ff):
        dff = json_normalize(ff)
        filtered = dff[~dff.teammate & (dff['position.name'] == 'Goalkeeper')]
        if filtered.empty:
            filtered = filtered.append({}, ignore_index=True)
        return filtered.iloc[0]

    goalkeepers = df['shot.freeze_frame'].dropna().apply(get_goalkeeper)
    return df.assign(**{
        'player.id.GK': goalkeepers['player.id'],
        'player.name.GK': goalkeepers['player.name'],
        'location.x.GK': goalkeepers.location.map(lambda gk: gk[0], na_action='ignore'),
        'location.y.GK': goalkeepers.location.map(lambda gk: gk[1], na_action='ignore'),
    })


def shot_info(df):
    raise NotImplementedError


def freeze_frame_info(df):
    raise NotImplementedError


def format_elapsed_time(df):
    raise NotImplementedError


def possession_info(df):
    raise NotImplementedError
