import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
from scipy.stats import poisson
from nhl_forecast.data import regulation_scores, build_features, stack_sides
from nhl_forecast.models import bivariate_logpmf, outcome_probabilities, NBRegressor, NUMERIC
from nhl_forecast.evaluation import paired_bootstrap

def fixture():
    rows=[]
    for i,(date,h,a,yh,ya) in enumerate([
        ('2020-01-01','A','B',2,1),('2020-01-01','C','D',5,3),
        ('2020-01-02','A','C',4,2),('2020-01-03','D','B',0,1),
        ('2020-01-04','B','A',2,3)]):
        rows.append(dict(game_id=i,season=2019,date=pd.Timestamp(date),home_team=h,away_team=a,
            home_goals=yh,away_goals=ya,home_shots=30.,away_shots=28.,home_attempts=55.,away_attempts=50.))
    return pd.DataFrame(rows)

class IntegrityTests(unittest.TestCase):
    def test_regulation_and_postregulation(self):
        self.assertEqual(regulation_scores(4,2,3600),(4,2))
        self.assertEqual(regulation_scores(4,3,3695),(3,3))
        self.assertEqual(regulation_scores(2,2,3900),(2,2))
        self.assertEqual(regulation_scores(0,1,3655),(0,0))
        for values in [(1,1,1200),(1,1,3600),(5,2,3700),(-1,2,3600),(1.5,2,3600)]:
            with self.assertRaises(ValueError):regulation_scores(*values)

    def test_current_and_future_outcomes_cannot_change_past_features(self):
        games=fixture()
        first=build_features(games)
        changed=games.copy()
        changed.loc[changed.date>=pd.Timestamp('2020-01-02'),['home_goals','away_goals']]=99
        second=build_features(changed)
        columns=[c for c in first if c.endswith(('_gf','_ga','_sf','_sa','_cf','_ca','_rest','_history_n')) or c.startswith('league_')]
        pd.testing.assert_frame_equal(first.loc[:2,columns],second.loc[:2,columns])

    def test_same_day_league_features_are_identical(self):
        f=build_features(fixture())
        self.assertEqual(f.loc[0,'league_home'],f.loc[1,'league_home'])
        self.assertEqual(f.loc[2,'home_history_n'],1)
        self.assertLess(f.loc[2,'home_history_date'],f.loc[2,'date'])

    def test_side_stacking_order(self):
        f=build_features(fixture())
        s=stack_sides(f)
        self.assertEqual(s.target.tolist(),f.home_goals.tolist()+f.away_goals.tolist())
        self.assertEqual(s.is_home.tolist(),[1]*len(f)+[0]*len(f))

    def test_bivariate_distribution_normalization_and_moments(self):
        v=np.arange(40)
        j=np.exp(bivariate_logpmf(v[:,None],v[None,:],3.,2.5,.2))
        self.assertAlmostEqual(j.sum(),1.,places=10)
        self.assertAlmostEqual((j*v[:,None]).sum(),3.,places=10)
        self.assertAlmostEqual((j*v[None,:]).sum(),2.5,places=10)
        self.assertAlmostEqual((j*(v[:,None]-3)*(v[None,:]-2.5)).sum(),.5,places=8)
        np.testing.assert_allclose(bivariate_logpmf(v,v,3.,2.5,0.),poisson.logpmf(v,3.)+poisson.logpmf(v,2.5))

    def test_outcome_probabilities_and_symmetry(self):
        p=outcome_probabilities(np.array([3.]),np.array([3.]))[0]
        self.assertAlmostEqual(p.sum(),1.)
        self.assertAlmostEqual(p[0],p[2])
        self.assertGreater(p[1],0.)

    def test_bootstrap_keeps_pairing(self):
        dates=pd.Series(pd.date_range('2020-01-01',periods=40))
        result=paired_bootstrap(dates,np.ones(40)*-.1,repetitions=100)
        self.assertAlmostEqual(result['low95'],-.1)
        self.assertAlmostEqual(result['high95'],-.1)

if __name__=='__main__':unittest.main()
