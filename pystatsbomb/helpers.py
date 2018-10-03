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
        'shot.end_location.z': shot_end_location.map(lambda l: l[2] if len(l) == 3 else np.NaN, na_action='ignore'),
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
    df = df.assign(**{
        'location.x': np.where((df['location.x'] == 120) & (df['location.y'] == 40), 119.66666, df['location.x']),
        'location.x.GK': np.where((df['location.x.GK'] == 120) & (df['location.y.GK'] == 40), 119.88888, df['location.x.GK']),
    })
    df = df.assign(**{
        'DistToGoal': np.sqrt((df['location.x'] - 120) ** 2 + (df['location.y'] - 40) ** 2),
        'DistToKeeper': np.sqrt((df['location.x.GK'] - 120) ** 2 + (df['location.y.GK'] - 40) ** 2),
    })
    df = df.assign(**{
        'AngleToGoal': np.where(df['location.y'] <= 40, np.arcsin((120 - df['location.x']) / df.DistToGoal), (np.pi / 2) + np.arccos((120 - df['location.x']) / df.DistToGoal)),
        'AngleToKeeper': np.where(df['location.y.GK'] <= 40, np.arcsin((120 - df['location.x.GK']) / df.DistToKeeper), (np.pi / 2) + np.arccos((120 - df['location.x.GK']) / df.DistToKeeper)),
    })
    df = df.assign(**{
        'AngleToGoal': df.AngleToGoal * 180 / np.pi,
        'AngleToKeeper': df.AngleToKeeper * 180 / np.pi,
    })
    df = df.assign(**{
        'AngleDeviation': abs(df.AngleToGoal - df.AngleToKeeper),
        'avevelocity': np.sqrt((df['shot.end_location.x'] - df['location.x']) ** 2 + (df['shot.end_location.y'] - df['location.y']) ** 2) / df.duration,
        'DistSGK': np.sqrt((df['location.x'] - df['location.x.GK']) ** 2 + (df['location.y'] - df['location.y.GK']) ** 2),
    })
    return df


def freeze_frame_info(df):
    raise NotImplementedError


def format_elapsed_time(df):
    raise NotImplementedError


def possession_info(df):
    raise NotImplementedError
