"""Canonical pairing, conservative calendar-day features and source integrity."""
from collections import defaultdict, deque
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

SOURCE_URL = 'https://moneypuck.com/moneypuck/playerData/careers/gameByGame/all_teams.csv'
SOURCE_COLUMNS = ['team', 'opposingTeam', 'season', 'gameId', 'home_or_away',
                  'gameDate', 'situation', 'goalsFor', 'goalsAgainst', 'iceTime',
                  'shotsOnGoalFor', 'shotsOnGoalAgainst', 'shotAttemptsFor',
                  'shotAttemptsAgainst', 'playoffGame']

def checksum(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def regulation_scores(home, away, seconds):
    """MoneyPuck counts actual goals, not the shootout scoreboard marker."""
    if seconds < 3600 or seconds > 3900:
        raise ValueError('Nonstandard or incomplete regular-season duration')
    if int(home) != home or int(away) != away or min(home, away) < 0:
        raise ValueError('Goals must be nonnegative integers')
    home, away = int(home), int(away)
    if seconds > 3600:
        if abs(home - away) > 1:
            raise ValueError('Invalid overtime score')
        if home > away:
            home -= 1
        elif away > home:
            away -= 1
    elif home == away:
        raise ValueError('Regulation-completed game cannot end in a tie')
    return home, away

def canonical_games(raw_path, start=2016, end=2024):
    raw = pd.read_csv(raw_path, usecols=SOURCE_COLUMNS)
    # Do not compute descriptive outcomes for the reserved 2025 season.
    raw = raw[raw.season.between(start, end) & (raw.situation == 'all') & (raw.playoffGame == 0)].copy()
    if raw.duplicated(['gameId', 'home_or_away']).any():
        raise ValueError('Duplicate team-game role')
    counts = raw.groupby('gameId').size()
    if (counts != 2).any():
        raise ValueError('Each game must have exactly two team records')
    h = raw[raw.home_or_away == 'HOME'].set_index('gameId')
    a = raw[raw.home_or_away == 'AWAY'].set_index('gameId')
    if set(h.index) != set(a.index):
        raise ValueError('Home/away pairing incomplete')
    a = a.loc[h.index]
    for hc, ac in [('goalsFor', 'goalsAgainst'), ('goalsAgainst', 'goalsFor'),
                   ('iceTime', 'iceTime'), ('gameDate', 'gameDate'), ('season', 'season'),
                   ('team', 'opposingTeam'), ('opposingTeam', 'team')]:
        if not (h[hc].to_numpy() == a[ac].to_numpy()).all():
            raise ValueError(f'Paired records disagree: {hc}/{ac}')
    records, excluded = [], []
    for gid, row in h.iterrows():
        opp = a.loc[gid]
        try:
            yh, ya = regulation_scores(row.goalsFor, opp.goalsFor, row.iceTime)
        except ValueError as exc:
            excluded.append({'game_id': int(gid), 'season': int(row.season), 'reason': str(exc)})
            continue
        records.append(dict(game_id=int(gid), season=int(row.season),
            date=pd.to_datetime(str(int(row.gameDate)), format='%Y%m%d'),
            home_team=row.team, away_team=opp.team,
            home_goals=yh, away_goals=ya,
            home_played_goals=int(row.goalsFor), away_played_goals=int(opp.goalsFor),
            duration=int(row.iceTime), went_to_overtime=bool(row.iceTime > 3600),
            went_to_shootout=bool(row.iceTime > 3600 and row.goalsFor == opp.goalsFor),
            home_shots=float(row.shotsOnGoalFor), away_shots=float(opp.shotsOnGoalFor),
            home_attempts=float(row.shotAttemptsFor), away_attempts=float(opp.shotAttemptsFor)))
    result = pd.DataFrame(records).sort_values(['date', 'game_id']).reset_index(drop=True)
    if result.game_id.duplicated().any():
        raise ValueError('Duplicate canonical game')
    return result, excluded

def build_features(games, window=20, prior_games=10):
    """Emit before update; all games on a source calendar date form one batch.

    Use a fixed, explicitly chosen cold-start prior. Retain at most 20 prior
    games across seasons. Source calendar dates are not claimed as UTC times.
    """
    history = defaultdict(lambda: deque(maxlen=window))
    last_date = {}
    league_h, league_a, league_n = 2.8 * 100, 2.6 * 100, 100
    rows = []
    for date, batch in games.groupby('date', sort=True):
        for row in batch.itertuples(index=False):
            values = row._asdict()
            values.update(league_home=league_h / league_n, league_away=league_a / league_n)
            for side, team in [('home', row.home_team), ('away', row.away_team)]:
                hist = list(history[team])
                # Same-date data cannot enter this feature snapshot.
                if team in last_date and not last_date[team] < date:
                    raise ValueError('Feature history crosses prediction date')
                n = len(hist)
                priors = [2.7, 2.7, 30., 30., 55., 55.]
                for j, name in enumerate(['gf', 'ga', 'sf', 'sa', 'cf', 'ca']):
                    values[f'{side}_{name}'] = (sum(v[j] for v in hist) + prior_games * priors[j]) / (n + prior_games)
                values[f'{side}_history_n'] = n
                values[f'{side}_rest'] = min((date-last_date[team]).days, 7) if team in last_date else 7
                values[f'{side}_back_to_back'] = int(values[f'{side}_rest'] == 1)
                values[f'{side}_history_date'] = last_date.get(team, pd.NaT)
            values['elo_difference'] = 0.  # Elo reserved for a later outcome-only track.
            rows.append(values)
        for row in batch.itertuples(index=False):
            history[row.home_team].append((row.home_goals, row.away_goals, row.home_shots, row.away_shots, row.home_attempts, row.away_attempts))
            history[row.away_team].append((row.away_goals, row.home_goals, row.away_shots, row.home_shots, row.away_attempts, row.home_attempts))
            last_date[row.home_team] = last_date[row.away_team] = date
            league_h += row.home_goals
            league_a += row.away_goals
            league_n += 1
    return pd.DataFrame(rows)

def stack_sides(features):
    blocks = []
    for side, other in [('home', 'away'), ('away', 'home')]:
        block = pd.DataFrame({
            'game_id': features.game_id, 'season': features.season,
            'date': features.date, 'is_home': int(side == 'home'),
            'team': features[f'{side}_team'], 'opponent': features[f'{other}_team'],
            'target': features[f'{side}_goals'],
            'team_gf': features[f'{side}_gf'], 'team_ga': features[f'{side}_ga'],
            'opp_gf': features[f'{other}_gf'], 'opp_ga': features[f'{other}_ga'],
            'team_sf': features[f'{side}_sf'], 'team_sa': features[f'{side}_sa'],
            'opp_sf': features[f'{other}_sf'], 'opp_sa': features[f'{other}_sa'],
            'team_cf': features[f'{side}_cf'], 'opp_ca': features[f'{other}_ca'],
            'rest': features[f'{side}_rest'], 'opp_rest': features[f'{other}_rest'],
            'history_n': features[f'{side}_history_n'],
            'league_rate': features[f'league_{side}']})
        blocks.append(block)
    return pd.concat(blocks, ignore_index=True)
