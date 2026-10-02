"""Check deterministic stratified score reconstruction against official scoring."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import json
import subprocess
import time
import pandas as pd
from nhl_forecast.data import canonical_games

games,_=canonical_games(ROOT/'data/raw/all_teams.csv')
results=[]
cache=ROOT/'data/raw/official-validation'
cache.mkdir(exist_ok=True)
# Two examples per finish type and season; sampling locked by game ID.
for season in range(2016,2025):
    for finish in ['REG','OT','SO']:
        subset=games[(games.season==season)]
        subset=subset[(~subset.went_to_overtime) if finish=='REG' else
                      (subset.went_to_shootout if finish=='SO' else (subset.went_to_overtime & ~subset.went_to_shootout))]
        for row in subset.sort_values('game_id').head(2).itertuples():
            path=cache/f'{row.game_id}.json'
            url=f'https://api-web.nhle.com/v1/gamecenter/{row.game_id}/landing'
            if not path.exists():
                subprocess.run(['curl','--silent','--fail','--retry','2','--output',str(path),url],check=True)
                time.sleep(.2)
            d=json.loads(path.read_text(encoding='utf-8'))
            home=away=0
            periods=d.get('summary',{}).get('scoring',[])
            if not periods:
                raise ValueError(f'Missing official scoring for {row.game_id}')
            for p in periods:
                if p['periodDescriptor']['periodType']=='REG':
                    for goal in p.get('goals',[]):
                        if goal.get('isHome') is True: home+=1
                        elif goal.get('isHome') is False: away+=1
                        else:
                            abbrev=goal['teamAbbrev']['default']
                            if abbrev==d['homeTeam']['abbrev']:home+=1
                            elif abbrev==d['awayTeam']['abbrev']:away+=1
                            else:raise ValueError('Unknown scoring team')
            passed=(home,away)==(row.home_goals,row.away_goals)
            results.append(dict(game_id=row.game_id,season=season,finish=finish,passed=passed,
                                source_url=url))
            print(f'{row.game_id} {finish} {"PASS" if passed else "FAIL"}',flush=True)
            if not passed:raise ValueError(f'Regulation reconstruction mismatch for {row.game_id}')
pd.DataFrame(results).to_csv(ROOT/'reports/score-validation.csv',index=False)
print(f'Validated {len(results)} official comparisons',flush=True)
