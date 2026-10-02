from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'figure.dpi':160})
labels={'league_poisson':'League baseline','rolling_poisson':'Rolling form',
 'ridge_poisson_proxy':'Ridge with Poisson margins','poisson':'Independent Poisson',
 'negative_binomial':'Negative binomial','attack_defence_poisson':'Attack and defence',
 'bivariate_poisson':'Bivariate Poisson','boosted_poisson':'Poisson boosting',
 'random_forest_poisson_proxy':'Forest with Poisson margins'}
s=pd.read_csv(ROOT/'reports/data-summary.csv')
fig,ax=plt.subplots(figsize=(7.2,3.5))
ax.plot(s.season,s.home_mean,'o-',label='Home regulation goals',color='#234764')
ax.plot(s.season,s.away_mean,'o-',label='Away regulation goals',color='#977443')
ax.set(xlabel='Season starting year',ylabel='Mean goals per game',title='Regulation scoring varies across the study period')
ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/'scoring-by-season.png');plt.close(fig)
m=pd.read_csv(ROOT/'reports/holdout-paired-comparisons.csv').iloc[1:].sort_values('mean_difference')
fig,ax=plt.subplots(figsize=(7.2,4.2))
y=np.arange(len(m));ax.errorbar(m.mean_difference,y,
 xerr=np.vstack([m.mean_difference-m.low95,m.high95-m.mean_difference]),fmt='o',color='#234764',capsize=3)
ax.axvline(0,color='gray',linestyle='--');ax.set_yticks(y,[labels[n] for n in m.model])
ax.set(xlabel='Joint NLL difference from league baseline (lower is better)',title='Final holdout NLL differences and 95% bootstrap intervals')
fig.tight_layout();fig.savefig(OUT/'holdout-comparison.png');plt.close(fig)
d=pd.read_csv(ROOT/'reports/development-metrics.csv')
fig,ax=plt.subplots(figsize=(7.2,3.8))
for name in ['league_poisson','poisson','boosted_poisson','ridge_poisson_proxy']:
 frame=d[d.model==name];ax.plot(frame.season,frame.joint_nll,'o-',label=labels[name])
ax.set(xlabel='Outer validation season starting year',ylabel='Mean joint NLL',title='Temporal folds reveal changing forecast difficulty')
ax.set_xticks(range(2019,2024))
ax.legend(frameon=False,fontsize=8);fig.tight_layout();fig.savefig(OUT/'development-folds.png');plt.close(fig)
p=pd.read_csv(ROOT/'reports/predictions/holdout.csv')
frozen=json.loads((ROOT/'reports/frozen-models.json').read_text())
selected=p[p.model==frozen['selected_primary']].copy()
calibration=[]
fig,axes=plt.subplots(1,3,figsize=(7.2,3.0),sharex=True,sharey=True)
for ax,col,name in zip(axes,['p_home','p_draw','p_away'],['Home win','Regulation draw','Away win']):
 actual=(selected.home_actual>selected.away_actual) if col=='p_home' else ((selected.home_actual==selected.away_actual) if col=='p_draw' else (selected.home_actual<selected.away_actual))
 bins=np.linspace(0,1,11)
 ids=np.minimum(np.digitize(selected[col],bins)-1,9)
 for j in range(10):
  mask=ids==j
  if mask.sum():
   calibration.append(dict(outcome=name,bin=j,n=int(mask.sum()),predicted=float(selected.loc[mask,col].mean()),observed=float(actual[mask].mean())))
 c=pd.DataFrame([r for r in calibration if r['outcome']==name]);ax.plot(c.predicted,c.observed,'o-',color='#234764')
 ax.plot([0,1],[0,1],'--',color='gray');ax.set(title=name,xlabel='Mean probability',xlim=(0,1),ylim=(0,1))
axes[0].set_ylabel('Observed frequency')
fig.suptitle('Frozen model outcome calibration on the final holdout',fontsize=11)
fig.tight_layout();fig.savefig(OUT/'outcome-calibration.png');plt.close(fig)
pd.DataFrame(calibration).to_csv(ROOT/'reports/outcome-calibration.csv',index=False)
fig,ax=plt.subplots(figsize=(7.2,3.1))
for y,season in enumerate(range(2019,2025)):
 ax.broken_barh([(2016,season-2016)],(y-.3,.6),facecolors='#cbd8df')
 ax.broken_barh([(season,1)],(y-.3,.6),facecolors='#977443' if season==2024 else '#234764')
ax.set(xlim=(2016,2025),ylim=(-.6,5.6),xlabel='Season starting year',title='Expanding windows preserve the direction of time')
ax.set_yticks(range(6),['Validate 2019','Validate 2020','Validate 2021','Validate 2022','Validate 2023','Final holdout 2024'])
ax.set_xticks(range(2016,2026));fig.tight_layout();fig.savefig(OUT/'temporal-validation.png');plt.close(fig)
print('Built five research figures and outcome-calibration table')
