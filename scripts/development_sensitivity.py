"""Exploratory follow-up: development-only window and feature sensitivity.

Specified after the initial holdout evaluation. Never accesses the holdout
outcomes, never changes the frozen family and never writes final test results.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import json
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import PoissonRegressor
from threadpoolctl import threadpool_limits
from nhl_forecast.data import canonical_games,build_features,stack_sides
from nhl_forecast.models import NUMERIC
from nhl_forecast.evaluation import evaluate

def fit_predict(train,test,columns,alpha):
    model=Pipeline([('prep',ColumnTransformer([('numeric',StandardScaler(),columns)])),
                    ('model',PoissonRegressor(alpha=alpha,max_iter=1000,tol=1e-8))])
    model.fit(stack_sides(train),stack_sides(train).target)
    means=np.maximum(model.predict(stack_sides(test)),.05)
    return means[:len(test)],means[len(test):]

def main():
    games,_=canonical_games(ROOT/'data/raw/all_teams.csv',end=2023)
    variants=[('window_5_full',5,NUMERIC),('window_10_full',10,NUMERIC),
              ('window_40_full',40,NUMERIC),
              ('window_20_no_shots_attempts',20,[c for c in NUMERIC if c not in
               ['team_sf','team_sa','opp_sf','opp_sa','team_cf','opp_ca']])]
    rows=[]
    for name,window,columns in variants:
        features=build_features(games,window=window)
        for season in range(2019,2024):
            train=features[features.season<season];test=features[features.season==season]
            valyear=int(train.season.max())
            inner=train[train.season<valyear];val=train[train.season==valyear]
            scores=[]
            for alpha in [.01,.1,1.]:
                mh,ma=fit_predict(inner,val,columns,alpha)
                metric,_,_=evaluate(val,mh,ma,outcomes=False)
                scores.append((metric['joint_nll'],alpha))
            alpha=min(scores)[1]
            mh,ma=fit_predict(train,test,columns,alpha)
            metric,_,_=evaluate(test,mh,ma,outcomes=False)
            metric.update(variant=name,season=season,penalty=alpha,window=window,
                          analysis_status='exploratory_development_only')
            rows.append(metric)
            print(name,season,f'{metric["joint_nll"]:.5f}',flush=True)
    pd.DataFrame(rows).to_csv(ROOT/'reports/development-sensitivity.csv',index=False)
    metadata={'status':'Exploratory follow-up specified after initial holdout evaluation',
              'accessed_season_start_years':[2016,2023],'holdout_outcomes_accessed':False,
              'primary_changed':False,'priors_changed':False,'variants':[v[0] for v in variants]}
    (ROOT/'reports/sensitivity-metadata.json').write_text(json.dumps(metadata,indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=4):main()
