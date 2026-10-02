"""Run development, freeze configurations, then score the final holdout once."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import argparse
import json
import time
import platform
import importlib.metadata
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from threadpoolctl import threadpool_limits
from nhl_forecast.data import canonical_games, build_features, stack_sides, checksum
from nhl_forecast.models import fit_model, predict_model, bivariate_logpmf
from nhl_forecast.evaluation import evaluate, paired_bootstrap

CONFIGS = {
 'ridge_poisson_proxy': [{'alpha':a} for a in [1.,10.,100.]],
 'poisson': [{'alpha':a} for a in [.01,.1,1.]],
 'negative_binomial': [{'alpha':a} for a in [.01,.1]],
 'attack_defence_poisson': [{'alpha':a} for a in [.01,.1,1.]],
 'bivariate_poisson': [{'alpha':a} for a in [.01,.1,1.]],
 'boosted_poisson': [{'leaves':l,'iterations':i} for l in [7,15] for i in [100,200]],
 'random_forest_poisson_proxy': [{'leaf':v} for v in [20,50]]}

def estimate_rho(fitted, train):
    mu = predict_model('bivariate_poisson', fitted, stack_sides(train))
    mh, ma = mu[:len(train)], mu[len(train):]
    h, a = train.home_goals.to_numpy(), train.away_goals.to_numpy()
    def loss(rho):
        return -bivariate_logpmf(h,a,mh,ma,rho).mean()
    fit = minimize_scalar(loss, bounds=(0.,.8), method='bounded', options={'xatol':1e-5})
    if not fit.success:
        raise RuntimeError('Shared-count optimizer failed')
    return float(fit.x) if fit.fun < loss(0.) else 0.

def fit_predict(name, training, testing, config):
    stacked = stack_sides(training)
    fitted = fit_model(name,stacked,config)
    mu = predict_model(name,fitted,stack_sides(testing))
    alpha = fitted.alpha if name=='negative_binomial' else 0.
    rho = estimate_rho(fitted,training) if name=='bivariate_poisson' else 0.
    return mu[:len(testing)], mu[len(testing):], alpha, rho

def select_config(name, training):
    val_season = int(training.season.max())
    inner = training[training.season < val_season]
    validation = training[training.season == val_season]
    results = []
    for config in CONFIGS[name]:
        mh,ma,alpha,rho = fit_predict(name,inner,validation,config)
        score,_,_ = evaluate(validation,mh,ma,alpha,rho,outcomes=False)
        results.append({'config':config, 'inner_nll':score['joint_nll'], 'validation_season':val_season})
    best = min(results,key=lambda r:r['inner_nll'])
    return best['config'], results

def baseline(name, testing):
    if name=='league_poisson':
        return testing.league_home.to_numpy(), testing.league_away.to_numpy()
    return ((testing.home_gf.to_numpy()+testing.away_ga.to_numpy())/2,
            (testing.away_gf.to_numpy()+testing.home_ga.to_numpy())/2)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--holdout',action='store_true')
    args = parser.parse_args()
    reports = ROOT/'reports'
    predictions = reports/'predictions'
    predictions.mkdir(parents=True,exist_ok=True)
    frozen_path = reports/'frozen-models.json'
    holdout_path = reports/'holdout-metrics.csv'
    if frozen_path.exists() or holdout_path.exists():
        raise SystemExit('Study is frozen. Use scripts/reproduce_frozen.py; do not select models again.')
    source = ROOT/'data/raw/all_teams.csv'
    games, excluded = canonical_games(source)
    features = build_features(games)
    (ROOT/'data/processed').mkdir(exist_ok=True)
    features.to_csv(ROOT/'data/processed/features.csv',index=False)
    pd.DataFrame(excluded).to_csv(reports/'exclusions.csv',index=False)
    summary = games.groupby('season').agg(n_games=('game_id','size'),
        home_mean=('home_goals','mean'),away_mean=('away_goals','mean'),
        home_variance=('home_goals','var'),away_variance=('away_goals','var'),
        overtime_fraction=('went_to_overtime','mean'),shootout_fraction=('went_to_shootout','mean'))
    # Holdout outcome summaries written only after all configurations are frozen.
    summary[summary.index<2024].to_csv(reports/'development-data-summary.csv')
    names = ['league_poisson','rolling_poisson']+list(CONFIGS)
    metric_rows, tuning, prediction_rows = [], [], []
    start = time.perf_counter()
    for season in range(2019,2024):
        train = features[features.season<season]
        test = features[features.season==season]
        for name in names:
            tick = time.perf_counter()
            if name in CONFIGS:
                config, search = select_config(name,train)
                tuning.append({'outer_season':season,'model':name,'search':search,'selected':config})
                mh,ma,alpha,rho = fit_predict(name,train,test,config)
            else:
                config={}
                mh,ma = baseline(name,test)
                alpha=rho=0.
            scores,nll,prob = evaluate(test,mh,ma,alpha,rho)
            scores.update(season=season,model=name,runtime_seconds=time.perf_counter()-tick,
                          config=json.dumps(config,sort_keys=True))
            metric_rows.append(scores)
            pred = pd.DataFrame({'game_id':test.game_id,'date':test.date,'season':season,
                'model':name,'home_mean':mh,'away_mean':ma,'joint_nll':nll,
                'home_actual':test.home_goals,'away_actual':test.away_goals,
                'p_home':prob[:,0],'p_draw':prob[:,1],'p_away':prob[:,2]})
            prediction_rows.append(pred)
            print(f'{season} {name}: joint NLL={scores["joint_nll"]:.5f}',flush=True)
    metrics=pd.DataFrame(metric_rows)
    metrics.to_csv(reports/'development-metrics.csv',index=False)
    devpred=pd.concat(prediction_rows,ignore_index=True)
    devpred.to_csv(predictions/'development.csv',index=False)
    primary=devpred.groupby('model').joint_nll.mean().idxmin()
    # Model choice and all final configurations precede holdout evaluation.
    train=features[features.season<2024]
    frozen={'protocol_sha256':checksum(ROOT/'docs/PROTOCOL.md'),
            'source_sha256':checksum(source),'selected_primary':primary,
            'holdout_season':2024,'configs':{},'development_seconds':time.perf_counter()-start,
            'seed':20261002,'python':platform.python_version(),
            'packages':{n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','scikit-learn','matplotlib']}}
    for name in CONFIGS:
        config,search=select_config(name,train)
        frozen['configs'][name]=config
        tuning.append({'outer_season':2024,'model':name,'search':search,'selected':config})
    frozen_path.write_text(json.dumps(frozen,indent=2),encoding='utf-8')
    (reports/'tuning-ledger.json').write_text(json.dumps(tuning,indent=2),encoding='utf-8')
    print(f'Frozen primary: {primary}; holdout not yet scored',flush=True)
    if not args.holdout:
        return
    test=features[features.season==2024]
    out, preds=[],[]
    for name in names:
        tick=time.perf_counter()
        if name in CONFIGS:
            mh,ma,alpha,rho=fit_predict(name,train,test,frozen['configs'][name])
        else:
            mh,ma=baseline(name,test)
            alpha=rho=0.
        scores,nll,prob=evaluate(test,mh,ma,alpha,rho)
        scores.update(model=name,season=2024,runtime_seconds=time.perf_counter()-tick)
        out.append(scores)
        preds.append(pd.DataFrame({'game_id':test.game_id,'date':test.date,'model':name,
            'home_mean':mh,'away_mean':ma,'joint_nll':nll,'home_actual':test.home_goals,
            'away_actual':test.away_goals,'p_home':prob[:,0],'p_draw':prob[:,1],'p_away':prob[:,2]}))
        print(f'HOLDOUT {name}: joint NLL={scores["joint_nll"]:.5f}',flush=True)
    pd.DataFrame(out).to_csv(holdout_path,index=False)
    holdpred=pd.concat(preds,ignore_index=True)
    holdpred.to_csv(predictions/'holdout.csv',index=False)
    base=holdpred[holdpred.model=='league_poisson'].set_index('game_id')
    comparisons=[]
    for name in names:
        frame=holdpred[holdpred.model==name].set_index('game_id').loc[base.index]
        diff=frame.joint_nll.to_numpy()-base.joint_nll.to_numpy()
        comparisons.append(dict(model=name,**paired_bootstrap(frame.date.reset_index(drop=True),diff)))
    pd.DataFrame(comparisons).to_csv(reports/'holdout-paired-comparisons.csv',index=False)
    summary.to_csv(reports/'data-summary.csv')
    print('Study complete; all outputs saved',flush=True)

if __name__=='__main__':
    with threadpool_limits(limits=4):
        run()
