"""Proper joint scores, outcome calibration and paired calendar-week bootstrap."""
import numpy as np
from scipy.stats import poisson, nbinom
from .models import nb_logpmf, bivariate_logpmf, marginal_quantiles, outcome_probabilities

def evaluate(games, mh, ma, alpha=0., rho=0., outcomes=True):
    yh, ya = games.home_goals.to_numpy(), games.away_goals.to_numpy()
    nll = -(bivariate_logpmf(yh,ya,mh,ma,rho) if rho > 0 else nb_logpmf(yh,mh,alpha)+nb_logpmf(ya,ma,alpha))
    eh, ea = yh-mh, ya-ma
    hlow, hhigh = marginal_quantiles(mh,alpha)
    alow, ahigh = marginal_quantiles(ma,alpha)
    result = dict(n=len(games), joint_nll=float(nll.mean()),
        home_mae=float(np.abs(eh).mean()), away_mae=float(np.abs(ea).mean()),
        combined_mae=float((np.abs(eh).mean()+np.abs(ea).mean())/2),
        combined_rmse=float(np.sqrt((np.mean(eh**2)+np.mean(ea**2))/2)),
        home_bias=float(-eh.mean()), away_bias=float(-ea.mean()),
        total_mae=float(np.abs(yh+ya-mh-ma).mean()),
        difference_mae=float(np.abs(yh-ya-mh+ma).mean()),
        home_coverage90=float(((yh>=hlow)&(yh<=hhigh)).mean()),
        away_coverage90=float(((ya>=alow)&(ya<=ahigh)).mean()),
        mean_interval_width=float(((hhigh-hlow)+(ahigh-alow)).mean()/2),
        rho=float(rho), nb_alpha=float(alpha))
    probabilities = None
    if outcomes:
        probabilities = outcome_probabilities(mh,ma,alpha,rho)
        target = np.where(yh>ya,0,np.where(yh==ya,1,2))
        actual = np.eye(3)[target]
        result['outcome_brier'] = float(np.mean(np.sum((probabilities-actual)**2,axis=1)))
        result['outcome_logloss'] = float(-np.log(np.maximum(probabilities[np.arange(len(target)),target],1e-15)).mean())
    return result, nll, probabilities

def paired_bootstrap(dates, differences, repetitions=2000, seed=20261002):
    """Resample ISO calendar weeks, preserving pairing within each block."""
    import pandas as pd
    labels = pd.to_datetime(dates).dt.to_period('W').astype(str).to_numpy()
    unique = np.unique(labels)
    sums = np.array([np.sum(differences[labels==label]) for label in unique])
    counts = np.array([np.sum(labels==label) for label in unique])
    rng = np.random.default_rng(seed)
    sampled = rng.integers(0,len(unique),size=(repetitions,len(unique)))
    means = sums[sampled].sum(axis=1)/counts[sampled].sum(axis=1)
    return {'mean_difference':float(np.mean(differences)),
            'low95':float(np.quantile(means,.025)), 'high95':float(np.quantile(means,.975)),
            'blocks':len(unique), 'repetitions':repetitions}
