import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from shapely.geometry import Point, Polygon


def all_clean(df):
    return df\
        .pipe(clean_locations)\
        .pipe(goalkeeper_info)\
        .pipe(shot_info)\
        .pipe(freeze_frame_info)\
        .pipe(format_elapsed_time)\
        .pipe(possession_info)


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
    }).sort_index()


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
    shots = df[df['type.name'] == 'Shot'][
        ['id', 'shot.freeze_frame', 'location.x', 'location.y', 'location.x.GK', 'location.y.GK', 'DistToGoal', 'AngleToGoal']
    ]
    shots = shots.assign(**{
        'Angle.New': shots.AngleToGoal.where(shots.AngleToGoal <= 90, 180 - shots.AngleToGoal),
    })
    shots = shots.assign(**{
        'Angle.Rad': shots['Angle.New'] * np.pi / 180,
    })
    shots = shots.assign(**{
        'Dist.x': 120 - shots['location.x'],
        'Dist.y': (40 - shots['location.y']).abs(),
        'new.Dx': np.sin(shots['Angle.Rad']) * (shots.DistToGoal + 1),
        'new.Dy': np.cos(shots['Angle.Rad']) * (shots.DistToGoal + 1),
    })
    shots = shots.assign(**{
        'new.x': 120 - shots['new.Dx'],
        'new.y': np.where(shots['location.y'] < 40, 40 - shots['new.Dy'], shots['new.Dy'] + 40),
    })

    ff = pd.concat(
        [json_normalize(shot['shot.freeze_frame']).assign(df_id=idx)
         for idx, shot in shots[shots['shot.freeze_frame'].notna()].iterrows()]
    ).join(shots, on='df_id').rename(columns={'location.x': 'x', 'location.y': 'y'})
    ff = ff.assign(**{
        'location.x': ff.location.map(lambda l: l[0], na_action='ignore'),
        'location.y': ff.location.map(lambda l: l[1], na_action='ignore'),
    })
    ff = ff.assign(**{
        'distance': np.sqrt((ff.x - ff['location.x'])**2 + (ff.y - ff['location.y'])**2)
    })
    ff.distance = ff.distance.where(ff.distance != 0, 1/3)

    ff = ff.assign(**{
        'cone': ff.apply(lambda row: Polygon([(120, 35), (120, 45), (row['new.x'], row['new.y'])]), axis=1),
        'cone_gk': ff.apply(lambda row: Polygon([
                (row['location.x.GK'], row['location.y.GK']-1), (row['location.x.GK'], row['location.y.GK']+1),
                (row.x, row.y+1), (row.x, row.y-1)
            ]) if not np.isnan(row['location.x.GK']) else Polygon(), axis=1),
    })
    ff = ff.assign(**{
        'InCone': ff.apply(lambda row: Point(row.location).within(row.cone), axis=1),
        'InCone.GK': ff.apply(lambda row: Point(row.location).within(row.cone_gk), axis=1),
    })

    def defender_area(group):
        return (group['location.x'].max() - group['location.x'].min()) * (group['location.y'].max() - group['location.y'].min())
    defenders = ff[(ff['location.x'] >= ff.x) & ~ff.teammate & (ff['position.name'] != 'Goalkeeper')]
    metrics = pd.DataFrame({
        'density': defenders.groupby('df_id').apply(lambda g: np.sum(np.reciprocal(g.distance))),
        'density.incone': defenders[defenders.InCone].groupby('df_id').apply(lambda g: np.sum(np.reciprocal(g.distance))),
        'DefendersInCone': defenders[defenders.InCone].groupby('df_id').df_id.count(),
        'distance.ToD1': defenders.groupby('df_id').distance.min(),
        'distance.ToD2': defenders.sort_values('distance').groupby('df_id').distance.nth(1),
        'InCone.GK': ff[(ff['location.x'] >= ff.x) & ff['InCone.GK']].groupby('df_id').df_id.count(),
        'AttackersBehindBall': ff[(ff['location.x'] >= ff.x) & ff.teammate].groupby('df_id').df_id.count(),
        'DefendersBehindBall': defenders.groupby('df_id').df_id.count(),
        'DefArea': ff[~ff.teammate & ff['position.id'].between(2, 8)].groupby('df_id').apply(defender_area),
    }).fillna({
        'density': 0,
        'density.incone': 0,
        'AttackersBehindBall': 0,
        'DefendersBehindBall': 0,
        'DefendersInCone': 0,
        'InCone.GK': 0,
        'DefArea': 1000,
    })
    distances_behind = ff[(ff['location.x'] < ff.x) & ~ff.teammate].sort_values('distance').groupby('df_id').distance
    metrics = metrics.fillna({
        'distance.ToD1': -distances_behind.nth(0),
        'distance.ToD2': -distances_behind.nth(1),
    }).fillna({
        'distance.ToD1': 30,
        'distance.ToD2': 30,
    })

    return df.join(metrics)


def format_elapsed_time(df):
    df = df.assign(milliseconds=pd.to_datetime(df.timestamp).dt.microsecond // 1000)
    df = df.assign(ElapsedTime=df.minute*60*1000 + df.second*1000 + df.milliseconds)

    periods = df.groupby(['match_id', 'period']).ElapsedTime.max().reset_index().rename(columns={'ElapsedTime': 'endhalf'})
    periods.period += 1
    firsthalf = pd.DataFrame({'match_id': periods.match_id.unique(), 'period': 1, 'endhalf': 0})
    periods = pd.concat([firsthalf, periods])
    df = df.merge(periods, how='left', on=['match_id', 'period'], copy=False)

    df.ElapsedTime[df.period == 2] += df.endhalf - (45 * 60 * 1000)
    df.ElapsedTime[df.period == 3] += df.endhalf - (90 * 60 * 1000)
    df.ElapsedTime[df.period == 4] += df.endhalf - (105 * 60 * 1000)
    df.ElapsedTime[df.period == 5] += df.endhalf - (120 * 60 * 1000)
    df.ElapsedTime /= 1000

    return df.drop('endhalf', axis=1)


def possession_info(df):
    possession = df.groupby(['match_id', 'possession'])
    df = df.assign(StartOfPossession=possession.ElapsedTime.transform('min'))
    df = df.assign(
        TimeInPoss=df.ElapsedTime - df.StartOfPossession,
        TimeToPossEnd=possession.ElapsedTime.transform('max') - df.ElapsedTime,
    )
    return df


def get_opposing_team(df):
    team1 = df.groupby('match_id')['team.name'].min()
    team2 = df.groupby('match_id')['team.name'].max()
    team1 = team1[df.match_id].reset_index().set_index(df.index)
    team2 = team2[df.match_id].reset_index().set_index(df.index)
    return df.assign(OpposingTeam=np.where(df['team.name'] == team1['team.name'], team2['team.name'], team1['team.name']))
