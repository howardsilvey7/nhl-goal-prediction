# NHL paired goal forecasting protocol

Author: Howard R. Silvey. Frozen first empirical protocol: 2026-10-02.
Research release: 0.1.0. This is a dated retrospective protocol, not a claim of
external preregistration. Commit it before running development comparisons.

## Research question

Using historical information from earlier source calendar dates, which practical
statistical or machine-learning framework best predicts the paired regulation
goal counts on subsequent NHL regular-season games and seasons?

The full project retains the broader pregame joint-distribution question in the
transfer baseline. This initial experiment is a narrower, explicitly operational
implementation. Calendar-date separation is verified; exact publication-time
availability and archived historical source revisions are not verified.

## Archival track

Preserve the 2020 PDF without editing. Local recovery has found that PDF but no
original NHL R code or input table. Original numerical findings are source-verified
where readable and are not computationally reproduced. Do not present a modern
game-level ridge model as an exact reconstruction of the 2020 analysis. Archival
source recovery remains open without blocking this separately labeled experiment.

## Data and scoring

Use MoneyPuck's explicitly published all-team game download for non-commercial
research and credit MoneyPuck.com. Raw data and row-level derivatives are not
redistributed. Retain source URL, retrieval time and SHA256 locally and commit
the provenance manifest. Do not scrape unlisted MoneyPuck pages.

Select season-start years 2016 through 2024, regular-season records only, and
situation `all`. One canonical row per game joins exactly one HOME and one AWAY
team record. Require score, opponent, date, season and duration agreement across
the two records. Fail on duplicate roles or pairing inconsistencies.

Primary targets are regulation goals reconstructed from actual played goals and
elapsed seconds. At 3600 seconds, use the played goals directly. Above 3600,
subtract one actual overtime goal from the winning team; if played goals are
tied, the game went to a shootout and no shootout marker is counted. Require
duration between 3600 and 3900, and tied regulation scores after adjustment.
Exclude incomplete/nonstandard records and retain an exclusion ledger. Check a
stratified sample against official period-by-period scoring before modeling.
This reconstruction and its source limitations must be disclosed in the report.

## Information boundary

Forecast on the source game calendar day. All games with that date receive
features before any same-date game updates the history. Use only strictly earlier
dates. This is a conservative calendar-day design, not a fabricated UTC cutoff.
No contemporaneous statistics, final standings, lineups, odds or goaltender claims
are used. Goals, shots and attempts come from the preceding 20 included games,
with 10 fixed prior games at 2.7 goals, 30 shots and 55 attempts per side.
Historical league home/away rates start with 100 prior games at 2.8/2.6 goals.
These priors are engineering choices fixed before comparisons, not estimated
from holdout outcomes. Histories carry across seasons; rest is capped at 7 days.
An expansion/renamed team starts from the pooled prior. ARI and UTA are distinct
team identities in this first experiment, without an assumed franchise merge.
Missing predictors cause a failure rather than silent zero filling.

All features derive from included regular-season games only. Playoff form is
excluded. Shots/attempts describe prior completed games including their overtime,
while goals are regulation-only. These mixed-exposure predictors are documented
and may be refined in later versions. Historical source revisions are an inherent
limitation even when date leakage is prevented.

## Temporal validation

Foundation: 2016-17 through 2018-19. Outer development seasons: 2019-20, 2020-21,
2021-22, 2022-23 and 2023-24. For each outer season, use earlier seasons to fit;
choose hyperparameters on the most recent earlier season, with only its preceding
seasons used for the inner fit. Fit preprocessing separately in every inner and
outer training window. Refit the chosen configuration on the full outer training
window. Learned coefficients are fixed for the complete outer season, while
lagged history features can update from earlier dates within it.

Final holdout: 2024-25. After development results, freeze the winning model family
using game-weighted mean joint negative log likelihood over outer development
games. Choose its final hyperparameters using 2023-24 with training through
2022-23, then refit through 2023-24. Freeze all comparison-model configurations
the same way before one holdout evaluation. No holdout-dependent recalibration,
search, feature selection or narrative-driven reruns. 2025-26 is reserved for a
future external extension; no outcome analysis of that season in this release.

## Models and fixed search spaces

1. Expanding home/away league Poisson baseline, updated from strictly earlier dates.
2. Smoothed 20-game team-form Poisson baseline: average attack and opponent defence.
3. Ridge point prediction embedded in an independent Poisson distribution (a proxy,
   not a fitted count likelihood): penalties 1, 10 and 100.
4. Penalized independent Poisson log-link model: penalties 0.01, 0.1 and 1.
5. NB2 log-link model: penalties 0.01 and 0.1; training-estimated dispersion.
6. Penalized attack/defence Poisson: team and opponent indicators, shared home effect,
   league rate, penalties 0.01, 0.1 and 1; unseen teams receive zero categorical effect.
   This is a frequentist shrinkage model, not Bayesian posterior inference.
7. Plug-in bivariate Poisson: same marginal Poisson feature model and search;
   training-estimated shared component c=rho*min(mu_home,mu_away), 0<=rho<=0.8.
   This allows only positive conditional dependence. It is not jointly optimized
   bivariate regression and does not guarantee a gain.
8. Histogram gradient boosting with Poisson loss: 7/15 leaves crossed with
   100/200 iterations, learning rate 0.05, minimum leaf 50, L2 penalty 1,
   no random internal early-stopping split.
9. Random forest point means embedded in Poisson margins: minimum leaf 20/50,
   250 trees, max features 0.8; this distribution is also explicitly a proxy.

Neural networks, Bayesian sampling, roster/goaltender information, xG, dynamics,
Dixon-Coles correction and calibrated ensembles are outside this first experiment.
They remain future hypotheses. They are not implied by completed model names.

## Evaluation and selection

Primary: paired-score mean negative log likelihood, lower is better. Secondary:
side and combined MAE/RMSE, bias, totals and differential MAE, marginal central
90% interval coverage and width, regulation home/draw/away Brier and log loss.
For discrete counts, equal-tail 90% intervals can cover more than 90%.
Outcome probabilities use a 0..35 score grid; reject material truncated mass.
Joint log likelihood is evaluated on the untruncated distribution.

Compare all models on the same games. Use 2000 paired calendar-week bootstrap
replicates for NLL differences; acknowledge cross-week team dependence and the
limited single-holdout horizon. Report every model, fold and exclusion, including
negative results. Draw calibration uses fixed probability bins. Do not claim
causality, profit, institutional acceptance or that any hypothesis is proven.

## Completion and release

Version 0.1.0 can release the source-verified audit, this executable first
experiment, formal PDF/DOCX documents and reproducibility tooling. Version 1.0.0
requires archival status resolution, independent review, full sensitivity work,
source-time/score verification, R parity and clean-environment reproducibility.
