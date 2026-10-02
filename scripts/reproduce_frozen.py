"""Replay existing configurations without search or changing the release results."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import json
import pandas as pd
from threadpoolctl import threadpool_limits
from nhl_forecast.data import canonical_games, build_features, checksum
from nhl_forecast.evaluation import evaluate
from run_study import fit_predict, baseline

def main():
    frozen=json.loads((ROOT/'reports/frozen-models.json').read_text())
    source=ROOT/'data/raw/all_teams.csv'
    if checksum(source)!=frozen['source_sha256']:
        raise SystemExit('Source snapshot differs from release. Obtain original checksum or run a new separately versioned study.')
    if checksum(ROOT/'docs/PROTOCOL.md')!=frozen['protocol_sha256']:
        raise SystemExit('Protocol differs from frozen release.')
    games,_=canonical_games(source)
    features=build_features(games)
    (ROOT/'data/processed').mkdir(exist_ok=True)
    features.to_csv(ROOT/'data/processed/features.csv',index=False)
    train=features[features.season<2024]
    test=features[features.season==2024]
    expected=pd.read_csv(ROOT/'reports/holdout-metrics.csv').set_index('model')
    discrepancies=[]
    for name in ['league_poisson','rolling_poisson']+list(frozen['configs']):
        if name in frozen['configs']:
            mh,ma,alpha,rho=fit_predict(name,train,test,frozen['configs'][name])
        else:
            mh,ma=baseline(name,test)
            alpha=rho=0.
        actual,_,_=evaluate(test,mh,ma,alpha,rho)
        for metric in ['joint_nll','combined_mae','combined_rmse','outcome_brier','outcome_logloss']:
            difference=abs(actual[metric]-expected.loc[name,metric])
            discrepancies.append({'model':name,'metric':metric,'absolute_difference':difference})
            if difference>1e-7:raise ValueError(f'Replay mismatch: {name} {metric} {difference}')
        print(f'{name}: frozen metrics reproduced',flush=True)
    (ROOT/'reports/replay-verification.json').write_text(json.dumps({
        'status':'passed','tolerance':1e-7,'comparisons':discrepancies},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=4):main()
