# National Hockey League Goal Prediction

## Audit of the 2020 Honours Project and 2026 Research Baseline

**Author:** Howard R. Silvey  
**Original supervisor:** Dr. Jason Nielsen  
**Original submission:** April 7, 2020  
**Initial audit date:** September 5, 2026  
**Expanded baseline date:** September 27, 2026  
**Document version:** 2.0 - Codex transfer baseline  
**2026 working title:** *National Hockey League Goal Prediction: Modern Statistical and Machine Learning Approaches*  
**Subtitle:** *A Revision and Extension of the 2020 Undergraduate Honours Project*

**Source audited:** [National Hockey League Data: Analysis and Prediction (2020)](https://carleton.ca/math/wp-content/uploads/Howard-Silvey-Honours-Project-2.pdf)

## 0. Document purpose, authority, and use

This document is the governing audit and research baseline for the NHL honours-project revision. It is intended to survive transfers between ChatGPT conversations, Codex workspaces, local development environments, and eventual repository documentation. It consolidates the decisions, interpretations, cautions, and planned work established through September 27, 2026.

It has four functions:

1. preserve an accurate account of what the 2020 honours project did;
2. distinguish historical results from later corrections and extensions;
3. lock the scientific principles that govern the 2026 research edition;
4. provide an implementation map detailed enough for another capable agent or developer to continue without silently changing the research question.

When this document conflicts with a casual earlier suggestion, this document governs unless Howard R. Silvey explicitly changes a decision. New decisions should be added to a dated decision log rather than silently substituted. A correction made during a numbered workflow automatically propagates into all later steps, and work continues through the remaining steps unless Howard explicitly requests a pause.

### Current project status at transfer

- The 2020 PDF has been read and methodologically audited.
- The revised title, subtitle, authorship, archival policy, core research question, principal response structure, validation philosophy, and R/Python division have been established.
- No original source-code or data inventory has yet been completed in this workspace.
- No modern NHL dataset has yet been selected, ingested, or modeled for the revision.
- No 2026 model results have been produced or frozen.
- The next gate is recovery and inventory of the original project materials.
- No hardware switch is currently required.

## 1. Executive conclusion

The original project contains a worthwhile research foundation and a notably good diagnosis of its own central limitation: a model intended for individual-game prediction was trained on team-season aggregates. The project also anticipated the most important conceptual extension—predicting home and away goals jointly as a vector-valued response—and correctly identified regularization, game-level data, player-level information, simulation, and richer tracking data as future work.

The revision should not merely refit the original regression. It should reconstruct it as an archival benchmark, document what can and cannot be reproduced, and then replace the research design with a leakage-controlled, game-level, time-aware forecasting study. The revised primary estimands should be the conditional distributions of home and away goals given only information available before puck drop.

The original low out-of-sample performance does not invalidate the research question. It mainly demonstrates that season-level aggregation, contemporaneous predictors, stepwise selection, and ordinary least squares were poorly matched to per-game NHL goal forecasting.

## 2. What the original project actually studied

### 2.1 Stated objective

The thesis states an objective of predicting the number of goals scored by a home team in a future game. It proposes extending this to the visiting team and potentially estimating a vector-valued response \((Y_1,Y_2)\).

### 2.2 Effective statistical unit

The effective unit was not a game. It was a **team-season**:

- 2016-17: 30 teams;
- 2017-18 through 2019-20: 31 teams per season;
- total: 123 team-season rows;
- approximately 40 candidate columns.

The paper describes `40 x 123 = 4,920` as data observations. More precisely, this is approximately 4,920 table cells; the regression sample size is 123 rows.

### 2.3 Effective response

Although the prose calls the response home-team goals, the construction is season-level team goals-for. A predicted season total was divided by 82 to produce a per-game average. This yields an estimate of average team scoring, not a matchup-specific forecast for a particular home game.

### 2.4 Candidate feature families

The project considered shooting/possession, expected and adjusted goals, scoring chances, high-danger chances, special teams, goaltending, schedule, and basic standings variables. Examples include shots, Corsi, Fenwick, expected goals, scoring chances, power-play percentage, save percentage, PDO, strength of schedule, wins, losses, points, and average age.

### 2.5 Models and validation

- Ordinary multiple linear regression;
- backward elimination;
- forward selection;
- residual plots and normal Q-Q plots;
- seven displayed predictions from each of three samples;
- leave-one-out cross-validation using `caret`.

The reported backward-elimination model retained Corsi For, Corsi Against, Corsi For Percentage, Power-Play Percentage, and Losses. Its reported in-sample \(R^2\) was 0.1161. The forward model's reported \(R^2\) was 0.06451. The reported LOOCV results were RMSE 46.20022, \(R^2\) 0.03927991, and MAE 37.91543 on the season-total response scale.

## 3. Strengths worth preserving

1. **An independently chosen, concrete research problem.** The project connects hockey domain knowledge to a formal predictive question.
2. **Original data assembly.** Constructing a multi-season team dataset and defining roughly 40 candidate measures was substantial undergraduate work.
3. **Transparent scope limitations.** The thesis repeatedly states what time and resource constraints prevented.
4. **An explicit out-of-sample instinct.** The work did not stop at in-sample fit and correctly recognized deterioration beyond the estimation sample.
5. **Recognition of overfitting.** The discussion identifies overfitting as a likely reason for weakened performance.
6. **Useful future-work foresight.** Game-level modeling, player information, Ridge regression, match simulation, richer tracking data, and joint home/away responses all point toward the right research direction.
7. **Reproducibility intent.** The software and key functions are identified, and the analysis was conducted in R.
8. **An honest negative result.** Reporting that the chosen linear model performed poorly is scientifically preferable to overstating it.

## 4. Methodological audit

### 4.1 Critical: mismatch between objective and unit of analysis

Dividing a predicted team-season goal total by 82 produces a nearly constant team average. It cannot represent a particular opponent, starting goaltender, lineup, venue, rest schedule, or current team state. This explains the clustered forecasts noted in the thesis itself.

**2026 resolution:** one row per game, with a prediction timestamp and paired home/away responses.

### 4.2 Critical: feature leakage and simultaneity

Several candidate predictors are calculated from the same season being predicted or contain components of goals and game outcomes:

- shooting percentage uses goals divided by shots;
- adjusted goals-for is constructed from goals-for;
- actual-minus-expected goals directly uses goals;
- high-danger goals-for contains a subset of goals;
- power-play percentage uses power-play goals;
- wins, losses, and points are realized game outcomes;
- save percentage and PDO are also contemporaneous season outcomes.

This does not mean these statistics can never be predictors. They must be **lagged or computed strictly from games completed before the forecasted game**. A same-period feature cannot be used to forecast its own period's target.

**2026 resolution:** maintain a feature-availability ledger and test every derived feature against the forecast timestamp.

### 4.3 Critical: validation did not match future deployment

Random sampling and LOOCV across pooled team-seasons allow later seasons to help predict earlier seasons and ignore dependence among repeated observations for the same teams. LOOCV estimates interpolation performance under an exchangeability assumption; it does not emulate forecasting the next NHL season or next game.

**2026 resolution:** expanding-window or rolling-origin validation, with seasons and dates strictly ordered. Hyperparameter selection must be nested inside each training window.

### 4.4 High: linear-Gaussian model was mismatched to a count outcome

Goals are nonnegative integer counts with low means and potentially unequal conditional variance. Ordinary least squares can produce impossible negative predictions and does not directly provide a calibrated probability distribution for scorelines.

**2026 resolution:** retain OLS only as an historical benchmark. Establish Poisson and negative-binomial baselines; model the two scores with independent and correlated count approaches; evaluate distributional calibration.

### 4.5 High: the home-team outcome was not operationally defined

The response is described both as home goals in a game and as each team's season goals. Those are different targets. It is also unclear how home status enters the season-level design.

**2026 resolution:** define \(Y_{g,H}\) and \(Y_{g,A}\) for game \(g\), with the home/away roles explicit in every row and feature.

### 4.6 High: stepwise significance testing is not a reliable forecasting strategy

Forward and backward selection are unstable with correlated predictors; repeated p-value testing understates selection uncertainty; and statistical significance is not equivalent to out-of-sample predictive value. Comparing in-sample \(R^2\) after selection compounds optimism.

**2026 resolution:** pre-specified baselines, penalized regression, model pipelines, nested tuning, and held-out temporal evaluation. Interpretability analysis occurs after honest model comparison.

### 4.7 High: multicollinearity was structural

CF, CA, and CF% are mathematically related; similar dependencies occur across Fenwick, scoring-chance, percentage, goal, standings, and PDO variables. NA coefficients for FA and OL likely indicate exact or near-exact linear dependence or data-construction problems, not innocuous missing output.

**2026 resolution:** encode feature families deliberately; never include raw totals and deterministic ratios without justification; audit rank, correlations, variance inflation, and transformation provenance.

### 4.8 High: sample and uncertainty reporting were insufficient

Only seven example games per display set were shown, and “two of seven rounded correctly” is not a stable accuracy measure. Confidence/prediction intervals were omitted. An RMSE threshold of 0.5 is not universal; its interpretation depends on the response scale and baseline performance.

**2026 resolution:** report every held-out game, uncertainty intervals, bootstrap or fold-level uncertainty around metrics, and comparison against naive baselines.

### 4.9 Medium: model assumptions were sometimes justified incorrectly

The Central Limit Theorem does not make OLS errors independent, homoscedastic, or normal, does not make the error distribution irrelevant, and does not guarantee that OLS always achieves minimum variance. The Gauss-Markov result requires specific assumptions; normality is additionally relevant for exact small-sample inference. A Q-Q plot addresses marginal residual normality, not independence.

**2026 resolution:** restate OLS assumptions precisely and separate estimation, inference, and prediction requirements.

### 4.10 Medium: panel dependence was ignored

Each franchise appears across multiple seasons, neighboring seasons are temporally related, and teams share league-level scoring environments. Rows are not plausibly independent and identically distributed.

**2026 resolution:** model team attack/defence effects, season effects, and temporal evolution explicitly or use grouped/time-aware evaluation that respects this structure.

### 4.11 Medium: incomplete-season and schedule assumptions

The 2019-20 season was incomplete at the paper's cutoff, and not every NHL season or team context is equivalent to an 82-game schedule. A fixed division by 82 can be wrong or distort rates.

**2026 resolution:** use game-level rows and exposure-aware rates where aggregation is needed.

### 4.12 Medium: reproducibility package was incomplete

The appendix lists R functions but not executable scripts, package versions, random seeds, source files, exact preprocessing, or a data dictionary sufficient to reproduce the outputs.

**2026 resolution:** repository-level environment locks, data provenance, scripts, tests, deterministic seeds, generated tables/figures, and a one-command build.

## 5. Data dictionary audit

The original glossary is valuable but needs correction and provenance fields. Examples requiring attention:

- `FA` is labeled “Fenwick For” in one definition but appears intended to mean Fenwick Against.
- The high-danger percentage formula is labeled with `SCF%` and reuses the scoring-chance formula, apparently a typographical/formula error.
- `SV% = S/SA` is ambiguous because `S` was earlier defined as team shots, not goaltender saves.
- PDO is described as save percentage alone in its name, whereas standard PDO combines on-ice shooting and save percentages (scale conventions differ).
- PK% uses `PP` where an opponent power-play-goals-against term appears intended.
- “home goals” and overall team goals-for are conflated.
- Totals, rates, percentages, adjusted measures, and derived identities are not tagged separately.

The 2026 data dictionary should contain: canonical name, mathematical definition, unit, level (game/team/player), side (home/away/for/against), source, source version, time window, lag, missing-value policy, leakage status, and transformation lineage.

## 6. Reproducibility verdict

**Current status: partially reproducible in principle, not yet reproducible in execution.**

The PDF contains enough information to identify the broad dataset dimensions, feature families, chosen models, and reported results. It does not contain the underlying CSV files, executable analysis source, exact row construction, exact randomization, final formulas/coefficient tables, or software environment. Exact reproduction therefore requires locating the original project files or reconstructing the source data and making explicit decisions where the record is ambiguous.

The archival reproduction must distinguish:

- **reproduced:** obtained by running preserved original code on preserved original data;
- **reconstructed:** recreated from documented methods and newly acquired equivalent data;
- **verified:** a reported number independently confirmed;
- **unverified:** reported in the PDF but not yet independently confirmed;
- **corrected:** an error fixed for the revision while retaining the archival result.

## 7. Locked 2026 research question

> Using only information available before an NHL game begins, which statistical or machine-learning framework most accurately and reliably estimates the joint predictive distribution of home-team and away-team goals on future games and seasons?

Supporting questions:

1. How much improvement is obtained by moving from team-season aggregates to game-level, lagged features?
2. Do correlated-score models improve probability and scoreline calibration over separate count models?
3. How do classical count, hierarchical, rating, tree-ensemble, and selected neural models compare under identical temporal folds?
4. Which features contribute stable predictive value across seasons rather than only within one scoring environment?
5. How well do forecasts support downstream quantities such as win/draw-after-regulation/loss probabilities, total goals, and scoreline intervals?

## 8. Response and prediction design

For each game \(g\):

\[
\mathbf{Y}_g = (Y_{g,H},Y_{g,A}),
\]

where \(Y_{g,H}\) and \(Y_{g,A}\) are home and away goals under a clearly locked scoring convention. The revision must decide whether the primary target uses regulation-only goals or final official goals including overtime/shootout effects. Recommended primary design: model regulation-time team goals and treat overtime/shootout outcome separately, because shootout goals are not ordinary scoring events. A final-games-goals sensitivity analysis can be included for comparability and product use.

Every record must include `prediction_timestamp` and every feature must be computable as of that time.

## 9. Minimum honest baselines

1. League-average goals, updated only from past games;
2. home/away league-average goals;
3. rolling team goals-for/goals-against averages;
4. Elo-style win model for derived outcome comparison;
5. original-style OLS benchmark, clearly labeled;
6. independent Poisson home/away regression;
7. negative-binomial alternative where dispersion warrants it.

Advanced models earn inclusion only by answering a distinct research question or beating these baselines under the locked validation design.

## 10. Candidate model ladder

### Tier A: archival and simple baselines

- original OLS reconstruction;
- regularized linear regression;
- rolling averages;
- Elo-derived outcome baseline.

### Tier B: classical count models

- separate Poisson regressions;
- negative-binomial regressions;
- bivariate Poisson;
- Dixon-Coles-style low-score correction, adapted and justified for hockey rather than assumed transferable from soccer;
- generalized Poisson or other dispersion-aware variants only if diagnostics warrant them.

### Tier C: structured/hierarchical models

- team attack and defence effects;
- home-ice effect;
- season/scoring-environment effects;
- dynamic team strengths or state-space models;
- Bayesian hierarchical count models with partial pooling.

### Tier D: machine learning

- regularized generalized linear models;
- gradient-boosted trees (one carefully selected implementation first);
- random forest as a benchmark;
- distributional boosting or count-objective models if well supported;
- neural networks only after tabular baselines, and only with enough data and a clear temporal or distributional purpose.

This ladder avoids treating a long algorithm list as scientific depth. Each family must have a hypothesis, controlled inputs, honest tuning, and comparable outputs.

## 11. Evaluation framework

### Primary predictive metrics

- mean absolute error for home and away goals;
- root mean squared error for home and away goals;
- Poisson deviance or appropriate count deviance;
- negative log-likelihood/log score for the joint or marginal predictive distribution;
- ranked probability score or Brier score for derived game outcomes;
- interval coverage and interval width;
- calibration of goal and outcome probabilities.

### Secondary metrics

- exact scoreline accuracy, reported cautiously;
- within-one-goal accuracy;
- total-goals MAE and distributional calibration;
- win/draw-after-regulation/loss accuracy and log loss;
- \(R^2\) only as a secondary descriptive measure where meaningful.

### Temporal protocol

- train on earlier games/seasons;
- tune using only later portions within the training era;
- test on the next untouched interval;
- roll or expand forward;
- aggregate fold results and report variability;
- never use future standings, end-of-season summaries, or future feature normalization.

## 12. Claims the revision must avoid

- A predetermined target such as \(R^2 > 0.65\) or 0.70;
- “prediction accuracy” defined by rounding a handful of point estimates;
- claiming causal effects from predictive associations;
- claiming that normal-looking residuals establish independence;
- assuming more predictors or more complex models imply better forecasts;
- implying access to proprietary NHL tracking data unless it is actually licensed and used;
- rewriting the 2020 thesis as though its corrected methodology was what originally occurred.

## 13. Archival integrity and authorship

Keep the Carleton-hosted 2020 PDF unchanged as the historical submission. Publish the 2026 work as a separate revision and extension. Within the revised work:

- normal authorship: **Howard R. Silvey**;
- bibliographic order: **Silvey, Howard R.**;
- refer to the original as the 2020 undergraduate honours project;
- distinguish archival results from reproduced, reconstructed, and newly estimated results.

The accidental `-2` in the hosted filename is a hosting/file-management issue, not part of the scholarly title. It can be addressed separately with Carleton after the revision is complete.

## 14. Draft 2026 author's preface

The original version of this honours project was completed during the final semester of my undergraduate studies at Carleton University while I was carrying an overloaded course schedule to satisfy graduation requirements. The project's scope was therefore constrained to producing a complete statistical analysis within the available academic timeframe. Several approaches identified during the original research—including penalized regression, expanded validation, game-level modeling, and a paired home-and-away response—were documented but not implemented before submission.

This revised edition returns to those questions with additional statistical, computational, and software-engineering experience. Its purpose is not to rewrite the historical record or replace the original submission. It reproduces and audits the original analysis where the surviving materials permit, corrects methodological limitations transparently, and extends the research using game-level data, time-aware evaluation, count models, hierarchical methods, and machine-learning benchmarks.

## 15. Initial phased research plan

### Phase 0 - Governance and preservation

- Preserve the 2020 PDF unchanged.
- Establish naming, authorship, citation, and versioning rules.
- Create an assumptions/decisions log and correction-continuation rule.

### Phase 1 - Source recovery

- Locate original R scripts, CSV files, Word document, charts, notes, and package information.
- Record checksums and provenance.
- Classify each item as original, reconstructed, or new.

### Phase 2 - Archival reproduction

- Rebuild the 123-row data table.
- Re-run OLS, forward selection, backward elimination, residual diagnostics, predictions, and LOOCV.
- Reconcile every reported model, coefficient, metric, and plot.

### Phase 3 - Literature and data-source review

- Conduct an updated, source-controlled review of NHL goal models, correlated counts, dynamic team strengths, calibration, and hockey data sources.
- Confirm legal, licensing, citation, and redistribution constraints before ingestion.

### Phase 4 - Game-level data contract

- Lock seasons, scoring rules, identifiers, time zones, postponements, neutral sites, overtime/shootouts, expansion/relocation, and missing-data policies.
- Build raw, interim, processed, and feature datasets.

### Phase 5 - Leakage-safe feature engineering

- Generate lagged team form, attack/defence, shot-quality, special-teams, rest/travel, roster/goaltender, and opponent-strength features where available.
- Enforce prediction-time availability programmatically.

### Phase 6 - Baselines and count models

- Fit naive, OLS, Poisson, negative-binomial, and paired-score baselines.
- Diagnose dispersion, dependence, zero frequency, calibration, and residual structure.

### Phase 7 - Hierarchical and dynamic models

- Fit partial-pooling attack/defence and time-evolving strength models.
- Quantify uncertainty and season-to-season stability.

### Phase 8 - Machine-learning benchmarks

- Fit a controlled subset of penalized and tree-based models.
- Add neural models only if sample size and research value justify them.

### Phase 9 - Locked model comparison

- Run identical rolling-origin folds.
- Compare accuracy, probability quality, calibration, uncertainty, stability, runtime, and interpretability.
- Freeze the selected primary and secondary models before final narrative drafting.

### Phase 10 - Research manuscript

- Write methods from the locked protocol.
- Generate tables and figures directly from the pipeline.
- Separate archival findings, reproduction findings, new findings, limitations, and future work.

### Phase 11 - Repository and quality assurance

- Provide R and Python environments, tests, linting, deterministic builds, documentation, data cards, model cards, and citation metadata.
- Verify the project from a clean environment.

### Phase 12 - Portfolio release

- Publish the report, repository, concise project page, selected bibliography, and demonstration video.
- Preserve the full scientific caveats in every shorter portfolio summary.

## 16. Current decisions and open decisions

### Locked

- The original 2020 PDF remains archival and unchanged.
- The 2026 work is a separate revision and extension.
- The research objective is comparative, not “make linear regression work.”
- Home and away goals are related count responses.
- Evaluation is time-aware and out-of-sample.
- There is no predetermined \(R^2\) target.
- R provides continuity; Python supports broader engineering and benchmarking.
- The private circumstances surrounding 2020 are not included; the overloaded academic schedule may be acknowledged professionally.
- Chromebook work continues until an explicit hardware-switch notice.
- A correction to any numbered step automatically propagates through and continues the remaining sequence unless Howard explicitly pauses it.

### Open

- Whether original source code/data survive and can be recovered;
- exact historical data extraction dates and transformations;
- primary goal convention (recommended: regulation goals);
- historical start season and test-era end date;
- final public data source and redistribution permissions;
- whether player, lineup, goaltender, travel, betting-market, or tracking features are feasible and ethical for the primary study;
- exact manuscript format and eventual Carleton re-hosting request.

## 17. Immediate gate

Before modern data collection or model fitting, recover and inventory the original artifacts. If they no longer exist, formally declare the archival analysis “reconstructed rather than reproduced” and build the closest defensible historical dataset without pretending it is identical.

No hardware switch is recommended for this gate. Source inventory, audit reconciliation, research design, and initial data-source evaluation can be completed from the current Chromebook workflow.

## 18. Scientific framing for the 2026 research edition

### 18.1 Research type

The revised work is a **comparative predictive-modeling study with an archival reproduction component**. It is not a causal study and should not make causal claims about how a statistic changes scoring. Its primary task is to estimate future goal distributions honestly from pregame information and compare model families under a common temporal protocol.

### 18.2 Population and unit of analysis

The intended population is NHL regular-season games within the seasons ultimately included by the data contract. The canonical row is one scheduled game. Each row must identify the home team, away team, scheduled start, actual start where known, season, game type, venue context, and the forecast cutoff.

Playoff games may later form a separate external-validity or transfer experiment. They should not be casually pooled with regular-season games because pace, strategy, roster use, overtime format, and selection into the playoffs differ.

### 18.3 Prediction moment

The primary forecast should represent a realistic **pregame prediction**. The exact cutoff remains to be locked, but the preferred default is immediately before the game using only information that would have been available by a documented cutoff such as the scheduled game day or a fixed number of hours before puck drop.

If confirmed starting-goaltender or lineup information is used, the project must either:

- define a later forecast cutoff at which that information is normally available; or
- maintain two model tracks: an early forecast without confirmed lineups and a late forecast with them.

The same target may not be predicted with different information availability across observations unless the distinction is explicitly modeled and reported.

### 18.4 Primary statistical object

The ideal output is not merely two rounded point predictions. It is a joint predictive distribution:

\[
p(Y_{g,H}=h, Y_{g,A}=a \mid \mathcal{I}_{g,t}),
\]

where \(\mathcal{I}_{g,t}\) is the information genuinely available for game \(g\) at forecast time \(t\). From this distribution the project can derive:

- expected home and away goals;
- marginal goal-count probabilities;
- exact-score probabilities;
- total-goals distribution;
- goal-differential distribution;
- regulation win/draw/loss probabilities;
- overtime-eligibility probability;
- prediction intervals or credible intervals.

This preserves the user's original two-response intuition while making it statistically operational.

### 18.5 Primary and secondary targets

The recommended target hierarchy is:

1. **Primary:** regulation-time home and away goals, because shootout goals are not ordinary scoring events and overtime conditions differ from regulation.
2. **Secondary sensitivity analysis:** official final home and away goals under a precisely documented NHL scoring convention.
3. **Derived:** regulation outcome, final outcome, goal differential, and total goals.

The project must inspect available source fields before locking this hierarchy. If reliable regulation-only goals cannot be reconstructed across the full study period, final goals may become the primary target, with the limitation stated explicitly.

## 19. Pre-specified research hypotheses and questions

The hypotheses below should be treated as testable expectations, not promised outcomes.

### H1 - Unit-of-analysis improvement

A leakage-safe game-level model will materially outperform the reconstructed team-season OLS approach on future games because it preserves opponent, venue, time, and recent-state information.

### H2 - Count-distribution advantage

Poisson or dispersion-aware count models will produce more coherent probabilistic forecasts than OLS, even when point-error differences are modest, because their support and likelihood match goal counts more closely.

### H3 - Correlated-score advantage

A joint or correlated home/away count model may improve joint log score, exact-score calibration, totals, or regulation-outcome probabilities over two conditionally independent score models. This is not guaranteed; empirical residual dependence must justify the added structure.

### H4 - Partial-pooling advantage

Hierarchical attack and defence effects should improve estimates for teams with limited recent data and reduce unstable season-to-season estimates through partial pooling.

### H5 - Dynamic-strength advantage

Time-varying team-strength estimates may outperform static season effects during coaching changes, injuries, trades, roster turnover, and changing league scoring environments.

### H6 - Shot-quality information

Lagged expected-goals and shot-quality features may improve forecasts beyond goals and shot totals, but only if their source definitions remain sufficiently consistent across seasons.

### H7 - Lineup/goaltender incremental value

Confirmed or probabilistic starting-goaltender and lineup features may improve late pregame forecasts. The gain should be measured separately from the base model because the information may not be available at an earlier operational forecast time.

### H8 - Complexity restraint

Tree ensembles or neural models may not outperform well-specified hierarchical count models after temporal validation, calibration, and data-volume constraints are considered. Complexity itself is not evidence of advancement.

### H9 - Stability across eras

Feature importance and model performance may change across league scoring environments. A robust model should retain useful calibration after season effects or dynamic baselines account for those shifts.

### H10 - Original insight reassessment

Corsi-family predictors may remain useful, but their apparent importance in the 2020 stepwise model may not survive leakage-safe, time-aware comparison against expected goals, recent form, opponent strength, and hierarchical team effects.

## 20. Data-source and provenance policy

### 20.1 Source-selection order

Data sources must be assessed in this order:

1. official NHL or other authoritative first-party sources where technically and legally practical;
2. stable public research datasets with explicit provenance and reproducible snapshots;
3. reputable third-party hockey-statistics sources with documented definitions;
4. community APIs or scraped sources only when terms, reliability, and reproducibility are acceptable.

No source should be selected solely because it is easy to scrape. Selection must consider historical depth, field stability, identifier quality, missingness, revision behavior, access limits, terms of use, attribution, and redistribution rights.

### 20.2 Required provenance record

Every raw input should record:

- source organization and URL or endpoint;
- retrieval date and time;
- query parameters or requested seasons;
- source schema/version when available;
- HTTP or package version details where relevant;
- original filename and checksum;
- licence/terms notes;
- known corrections or revision behavior;
- whether repository redistribution is allowed;
- transformation script that first consumes it.

### 20.3 Immutable raw layer

Raw downloads should be treated as immutable. Corrections belong in scripted transformations, never manual edits to source files. If a source republishes corrected data, retain a new version or checksum and document the change.

### 20.4 Original 2020 source caution

The thesis states that data were extracted from Hockey-Reference and discusses Sportradar as the provider. The precise chain of ownership, distribution, and allowable reuse must be verified rather than repeated as an unexamined licensing claim. The revision should distinguish data provenance from legal ownership and avoid calling a public table “proprietary NHL data” unless that characterization is supported.

### 20.5 Public-repository strategy

If redistribution is restricted, the repository should include:

- acquisition instructions or scripts where permitted;
- a schema-only or synthetic fixture for tests;
- checksums and expected row counts;
- derived aggregate outputs only where permitted;
- a clear `DATA_AVAILABILITY.md` statement.

The scientific report must remain reproducible without illegally republishing restricted raw data.

## 21. Canonical game-level data contract

The final column list will depend on source availability, but the following minimum contract should guide acquisition.

### 21.1 Identity and scheduling fields

| Field | Purpose |
| --- | --- |
| `game_id` | Stable canonical game identifier |
| `season_id` | NHL season convention, explicitly defined |
| `game_type` | Preseason, regular season, playoff, or other |
| `scheduled_start_utc` | Temporal ordering and forecast cutoff |
| `actual_start_utc` | Delay/postponement audit where available |
| `prediction_timestamp_utc` | Exact information boundary for the forecast |
| `home_team_id` | Stable franchise/team-season identifier |
| `away_team_id` | Stable franchise/team-season identifier |
| `venue_id` | Venue/neutral-site context where available |
| `neutral_site` | Explicit neutral-site indicator |
| `status` | Final, postponed, cancelled, suspended, etc. |

### 21.2 Target fields

| Field | Purpose |
| --- | --- |
| `home_goals_regulation` | Recommended primary home response |
| `away_goals_regulation` | Recommended primary away response |
| `home_goals_final` | Official final home score under locked convention |
| `away_goals_final` | Official final away score under locked convention |
| `went_to_overtime` | Separates regulation and post-regulation process |
| `went_to_shootout` | Prevents treating shootout markers as ordinary goals |
| `final_outcome` | Derived only after score conventions are locked |

### 21.3 Feature families

Features should be computed separately for home and away teams and, where useful, as differences or interactions:

- lagged goals for and against;
- shots, shot attempts, Fenwick, Corsi, scoring chances, high-danger chances;
- expected goals and expected goals against;
- shooting and save measures, with shrinkage for small samples;
- power-play and penalty-kill measures;
- team attack and defence ratings;
- Elo or other opponent-adjusted strength;
- recent rolling and exponentially weighted form;
- season-to-date and multi-season priors;
- days of rest, back-to-back status, travel, time-zone change, and schedule density;
- roster continuity, injuries, scratches, trades, and projected/confirmed lineup if reliable;
- starting-goaltender identity, rest, and lagged performance if reliable;
- home-ice, venue, altitude, neutral-site, and era effects where justified.

### 21.4 Feature-registry fields

Every modeled feature should have an accompanying registry entry containing:

| Registry field | Meaning |
| --- | --- |
| `feature_name` | Canonical machine-readable name |
| `plain_language_name` | Human-readable description |
| `formula` | Exact transformation |
| `source_columns` | Inputs and upstream tables |
| `level` | Game, team-game, player-game, season, venue, etc. |
| `lookback_window` | Expanding, 3/5/10 games, days, season-to-date, etc. |
| `lag_rule` | How current-game information is excluded |
| `available_at` | Earliest valid operational timestamp |
| `missing_policy` | Imputation, indicator, exclusion, or prior |
| `leakage_class` | Safe, unsafe, or conditionally safe |
| `expected_direction` | Optional pre-model expectation |
| `included_models` | Pipelines permitted to use it |

## 22. Leakage-control specification

Leakage prevention is a first-class research requirement, not a final diagnostic.

### 22.1 Core invariant

For a game beginning at time \(t_g\), every feature must be a function only of data timestamped strictly before its permitted cutoff. The target game and all later games must be excluded from rolling calculations, normalization, imputation, feature selection, and model tuning.

### 22.2 Common failure modes to test

- full-season statistics attached to games within that same season;
- rolling windows that accidentally include the current game;
- standings or team records downloaded after the predicted date;
- final injury/lineup information used in an early-forecast model;
- preprocessing fitted once on the complete dataset;
- imputation values learned from validation/test seasons;
- Elo ratings updated with the result before storing the pregame rating;
- opponent features joined from the wrong date;
- schedule-derived rest values calculated incorrectly around postponements;
- target-derived percentages treated as contemporaneously known;
- hyperparameters selected after inspecting the locked test period.

### 22.3 Automated leakage tests

The pipeline should fail if:

- any source event timestamp exceeds the row's prediction timestamp;
- any rolling group includes its current target row;
- train/validation/test game IDs overlap;
- a scaler or encoder is fitted outside its training fold;
- expected row counts change unexpectedly after a one-to-one join;
- future-season labels appear in training artifacts;
- feature snapshots cannot be regenerated from an as-of date.

## 23. Preprocessing and data-quality rules

### 23.1 Team and franchise identity

Team identifiers should remain stable despite naming, abbreviation, arena, or relocation changes. Franchise history and team-season identity may both be needed. Expansion teams require explicit cold-start priors rather than accidental missing values.

### 23.2 Game status and unusual events

Postponed, cancelled, suspended, forfeited, neutral-site, outdoor, and internationally played games should be tagged. Exclusions must be defined before outcome inspection wherever possible.

### 23.3 Missingness

Missingness should be classified as:

- structurally unavailable;
- not yet available at forecast time;
- source failure;
- legitimately undefined;
- data error.

Missing values should not be replaced by zero unless zero is substantively correct. Model-specific imputation must occur within temporal training folds.

### 23.4 Early-season history

For teams with few current-season games, use pre-specified multi-season priors, hierarchical shrinkage, or limited-history indicators. Do not silently drop early-season games, because that would change the deployment population.

### 23.5 Source-definition drift

Advanced-stat definitions may change over time or differ across providers. Each candidate feature needs a comparability audit. Where harmonization is unreliable, restrict the feature to a compatible period, use source/era indicators, or exclude it from the primary study.

## 24. Temporal validation and research firewall

### 24.1 Outer evaluation

The principal comparison should use expanding-window or rolling-origin folds. A generic expanding design is:

1. train on an initial block of complete seasons;
2. validate/tune on the next chronological block;
3. evaluate on the following untouched block;
4. expand the training window and repeat;
5. reserve a final season or period as the principal locked test set.

Exact seasons must be selected only after data availability and quality are known. The protocol should be written and versioned before final model comparison.

### 24.2 Inner tuning

Hyperparameters, early stopping, feature selection, transformations, calibration methods, and threshold choices must be learned exclusively within the training portion of each outer fold. If compute limits prevent fully nested tuning, use a fixed development-era configuration and report that compromise.

### 24.3 Final holdout

The final test period is a research firewall. It must not be used to choose features, hyperparameters, model families, seeds, stopping points, or narrative emphasis. If a serious implementation bug invalidates the holdout, record the incident and version a replacement protocol rather than quietly rerunning until results improve.

### 24.4 Comparison fairness

Models should be compared on identical eligible games, target definitions, feature-availability cutoffs, and folds. A late-lineup model may be compared with an early model only as a separate information-set experiment.

### 24.5 Season and subgroup reporting

Report overall and fold/season results, plus planned subgroups such as:

- early versus late season;
- expansion/cold-start teams;
- back-to-back versus rested games;
- overtime versus regulation-only games where relevant;
- high- and low-scoring eras;
- games with and without confirmed-goaltender information.

Subgroups are diagnostic unless pre-specified and adequately powered.

## 25. Model-family specifications

### 25.1 Naive reference models

At minimum include league mean, home/away mean, team rolling mean, and recent goals-for/goals-against baselines. A sophisticated model that cannot improve materially on these baselines has limited practical value.

### 25.2 Archival OLS benchmark

Reconstruct the 2020 design as faithfully as surviving materials permit. Also create a corrected game-level OLS or regularized linear benchmark so that failure of the historical design is not confused with failure of all linear predictors.

### 25.3 Separate Poisson models

Estimate home and away conditional means with log links. Check calibration, mean-variance relationships, tail behavior, zero frequency, and residual dependence. Do not assume equidispersion merely because Poisson is the starting model.

### 25.4 Negative-binomial and dispersion-aware models

Use only if diagnostics indicate meaningful overdispersion or unobserved heterogeneity. Estimate and report the dispersion parameter using the chosen parameterization; do not confuse it with regularization strength.

### 25.5 Bivariate Poisson or other joint-count models

Model shared game-level scoring components or dependence explicitly. Evaluate whether the dependence parameter is stable and whether added complexity improves joint distribution metrics, not just marginal MAE.

### 25.6 Dixon-Coles-style adjustment

Treat this as an adaptation experiment, not an automatic sports-analytics standard. Hockey's scoring frequency and mechanisms differ from soccer. Include only if empirical low-score residual patterns and literature support the correction.

### 25.7 Hierarchical Bayesian model

Candidate structure:

- team attack effects;
- team defence effects;
- home-ice effect;
- season or scoring-environment effect;
- partial pooling across teams/seasons;
- optional dynamic evolution;
- posterior predictive score distributions.

Assess convergence, effective sample size, divergent transitions where relevant, prior predictive behavior, posterior predictive checks, calibration, and computational cost.

### 25.8 Dynamic/state-space models

Allow team strengths to evolve over time. Compare update speed, stability, and forecast gains with simpler rolling/Elo features. Prevent the model from reacting to the target game before its forecast is recorded.

### 25.9 Tree ensembles

Use one or a small number of defensible implementations, likely gradient boosting plus a random-forest benchmark. Count-aware objectives or distributional outputs are preferable where supported. Calibrate derived probabilities using training-era data only.

### 25.10 Neural models

Neural networks are optional. They require a pre-stated rationale such as sequence representation, nonlinear interaction learning, or joint distribution estimation. They should not be included merely to make the project appear modern. If they are not competitive, the negative result remains useful.

### 25.11 Ensembles

An ensemble should be considered only after individual models are frozen and their errors shown to be complementary. Blend weights must be selected within development data, never the final holdout.

## 26. Metrics and statistical comparison

### 26.1 Point forecasts

- MAE by home, away, combined, goal differential, and total goals;
- RMSE on the same views;
- mean error/bias;
- optional secondary \(R^2\), with its limitations stated.

### 26.2 Distribution forecasts

- marginal and joint negative log-likelihood/log score;
- Poisson or model-appropriate deviance;
- ranked probability score for ordered outcomes where appropriate;
- Brier score and log loss for regulation outcome or final outcome;
- calibration curves and reliability summaries;
- prediction-interval coverage and sharpness;
- probability integral transform or randomized quantile residual diagnostics where appropriate.

### 26.3 Practical score summaries

- exact score accuracy;
- within-one-goal accuracy;
- probability assigned to the observed score;
- top-k scoreline coverage;
- total-goals distribution performance;
- regulation win/draw/loss performance.

These should remain secondary to proper scoring rules because exact score accuracy is sparse and can reward poorly calibrated point concentration.

### 26.4 Uncertainty in model comparisons

Report fold/season variation and paired differences on the same games. Candidate tools include block bootstrap, season-level bootstrap, or paired fold summaries that respect temporal/team dependence. Avoid presenting tiny metric differences as meaningful without uncertainty and practical-effect discussion.

### 26.5 Model-selection principle

The primary model should balance:

- out-of-sample predictive quality;
- probability calibration;
- stability across folds/seasons;
- interpretability appropriate to a research thesis;
- reproducibility and runtime;
- ability to generate the required paired-score outputs.

The numerically best single metric need not be the final primary model if the difference is trivial and another model is materially more stable, transparent, or reproducible. Any such choice must be documented before final narrative emphasis.

## 27. Calibration, simulation, and uncertainty

### 27.1 Calibration

Calibration should be examined for marginal goals, totals, regulation outcomes, and relevant score bins. Calibration methods, if used, must be fit within development folds. The uncalibrated and calibrated versions should both be reported.

### 27.2 Predictive intervals

Intervals should come from each model's predictive distribution or a defensible residual/bootstrap method. Report nominal versus observed coverage and average width. Narrow intervals are not better if they under-cover.

### 27.3 Game simulation

Simulation is a downstream use of the fitted joint distribution, not a substitute for missing observations. Simulated games can estimate outcome, total, and scoreline probabilities. The report must distinguish model-based simulated draws from real data.

### 27.4 Bayesian uncertainty

If Bayesian models are included, separate posterior parameter uncertainty from posterior predictive uncertainty. Priors and prior predictive checks should be documented in plain language and code.

## 28. Interpretability and scientific reporting

Interpretation should focus on stable predictive relationships and model behavior rather than causal narratives.

Recommended outputs include:

- attack/defence effect estimates with uncertainty;
- home-ice and season-environment effects;
- permutation importance or SHAP-like summaries for tree models, computed on held-out eras where feasible;
- partial-dependence or accumulated-local-effect plots for a limited number of important continuous features;
- feature stability across temporal folds;
- calibration and error examples, including model failures;
- comparison of the original selected Corsi variables with modern feature families.

Avoid overinterpreting one model's coefficient when predictors are correlated or transformed. Distinguish predictive value, statistical association, and domain interpretation.

## 29. Archival reproduction protocol

### 29.1 Artifact search list

Search likely local, cloud, email, and backup locations for:

- original `.R`, `.Rmd`, `.RData`, `.Rhistory`, `.csv`, `.xlsx`, `.docx`, and PDF files;
- downloaded Hockey-Reference tables;
- charts exported from R;
- assignment/project folders and compressed archives;
- email attachments exchanged with the supervisor;
- notes describing manual cleaning or random sampling;
- package/library lists and old computer backups.

Do not modify discovered originals. Copy them into a read-only archival area and calculate checksums.

### 29.2 Inventory fields

For every recovered item record:

- original path/name;
- file type and size;
- created/modified timestamps, treated cautiously;
- checksum;
- apparent role;
- relation to a thesis table/figure/result;
- whether it opens successfully;
- whether it contains sensitive or restricted data;
- archival, reproducible, or uncertain status.

### 29.3 Reproduction sequence

1. establish an environment capable of running the original code without altering it;
2. identify all external paths and dependencies;
3. run data assembly where possible;
4. confirm the 123 rows and candidate columns;
5. verify response construction and sampling/reordering;
6. reproduce the full OLS model and NA coefficients;
7. reproduce backward and forward procedures;
8. recover exact final formulas and coefficient estimates;
9. regenerate residual plots;
10. reproduce the displayed game predictions;
11. reproduce LOOCV settings and output;
12. reconcile every number against the PDF;
13. document discrepancies without rewriting the historical record.

### 29.4 Reconstruction fallback

If original inputs are unavailable, construct the closest defensible historical dataset from archived public sources. Label every inference and discrepancy. The goal is to understand and benchmark the historical workflow, not manufacture an exact match that the evidence cannot support.

## 30. Technology and repository architecture

### 30.1 Tool roles

- **R:** archival reproduction, continuity with the 2020 work, classical statistical/count models, and any methods best supported in R.
- **Python:** data engineering, machine-learning pipelines, selected probabilistic/Bayesian models, tests, and broader benchmarking.
- **Quarto:** preferred reproducible manuscript/report system, capable of integrating R, Python, citations, equations, tables, and figures.
- **VS Code:** recommended primary IDE when local development begins.
- **RStudio:** optional companion for inspecting and running R-specific notebooks or scripts.
- **Git/GitHub:** version control, issues, releases, and CI.
- **Docker:** later reproducibility/deployment layer if justified, not an immediate requirement.

### 30.2 Proposed repository layout

```text
nhl-goal-prediction/
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
├── DATA_AVAILABILITY.md
├── REPRODUCIBILITY.md
├── DECISIONS.md
├── pyproject.toml
├── renv.lock
├── _quarto.yml
├── config/
├── data/
│   ├── README.md
│   ├── raw/              # ignored or restricted where required
│   ├── interim/
│   ├── processed/
│   └── fixtures/
├── src/
│   ├── r/
│   └── python/
├── scripts/
│   ├── acquire/
│   ├── build/
│   ├── model/
│   └── report/
├── notebooks/           # exploratory only; production logic moves to src
├── models/              # metadata or permitted small artifacts
├── reports/
│   ├── manuscript/
│   ├── figures/
│   └── tables/
├── tests/
│   ├── data/
│   ├── features/
│   ├── leakage/
│   ├── models/
│   └── integration/
├── archive/
│   └── 2020-original/
└── .github/workflows/
```

The exact layout may evolve, but raw data, reusable source code, exploratory notebooks, generated outputs, tests, and the 2020 archive must remain clearly separated.

### 30.3 Environment locking

Use explicit Python dependency locking and `renv` for R. Record interpreter versions, platform information, random seeds, external system dependencies, and commands for rebuilding data, models, figures, and the manuscript.

### 30.4 Workflow orchestration

Start with transparent scripts and a documented command sequence. Add a workflow system such as `targets`, `make`, or another orchestrator only when it reduces genuine dependency-management risk. The finished project should expose one high-level verification command even if the full model suite has optional long-running stages.

## 31. Testing and quality gates

### Gate A - Archival integrity

- original PDF preserved byte-for-byte;
- recovered originals checksummed and unedited;
- archival versus reconstructed results labeled.

### Gate B - Data integrity

- primary keys unique;
- team/game identifiers valid;
- score totals and overtime/shootout flags internally consistent;
- row counts reconciled by season;
- no impossible negative counts or dates;
- joins audited for duplication and loss.

### Gate C - Leakage safety

- as-of timestamps validated;
- lag tests pass;
- preprocessing fit within folds;
- split overlap is zero;
- research-firewall period untouched.

### Gate D - Model validity

- naive baselines executed;
- convergence/optimization checked;
- count diagnostics completed;
- calibration assessed;
- predictions constrained to valid support or clearly interpreted.

### Gate E - Reproducibility

- clean-environment run succeeds;
- fixed seeds and deterministic settings documented;
- generated results match committed tables within tolerance;
- environment locks are complete;
- CI runs fast tests on supported versions.

### Gate F - Manuscript consistency

- every reported result traces to a generated artifact;
- table and figure numbers match references;
- formulas, terminology, and score conventions are consistent;
- citations resolve;
- abstract and conclusion do not overstate findings.

### Gate G - Release readiness

- repository documentation complete;
- licence and data availability correct;
- no secrets, private paths, restricted raw files, or personal data committed;
- tagged release built from a clean commit;
- thesis PDF and portfolio summaries match the frozen results.

## 32. Proposed revised-manuscript architecture

1. **Front matter**
   - title page;
   - author's preface (2026);
   - abstract;
   - acknowledgements if desired;
   - contents, tables, and figures.
2. **Introduction**
   - forecasting problem;
   - historical origin of the project;
   - revised research question and contributions.
3. **The 2020 honours project**
   - original objective, data, methods, results, and limitations;
   - archival reproduction/reconstruction outcome;
   - what the original work correctly anticipated.
4. **Related research and NHL analytics context**
   - count models;
   - correlated scores;
   - hierarchical/dynamic strength;
   - ratings and machine learning;
   - probabilistic validation and calibration;
   - modern hockey data.
5. **Data and prediction contract**
   - sources, rights, seasons, game definition, targets, exclusions;
   - prediction timestamp and feature availability;
   - descriptive analysis and data quality.
6. **Methods**
   - baselines;
   - count models;
   - hierarchical/dynamic models;
   - ML models;
   - tuning, calibration, and temporal validation.
7. **Results**
   - archival benchmark;
   - development/fold performance;
   - locked holdout;
   - calibration, uncertainty, stability, and computation;
   - ablations and sensitivity analyses.
8. **Discussion**
   - answer to the research question;
   - relation to the 2020 conclusions;
   - practical meaning;
   - limitations and non-causal interpretation.
9. **Conclusion and future work**
10. **Reproducibility and data-availability statement**
11. **References**
12. **Appendices**
   - definitions;
   - detailed folds and metrics;
   - priors/diagnostics;
   - supplementary results;
   - repository/build instructions.

## 33. Planned tables and figures

Candidate publication outputs include:

- timeline from the 2020 project to the 2026 extension;
- 2020 method-versus-2026 correction table;
- source and feature-availability table;
- study-period/game-count flow diagram;
- league scoring trends by season;
- home and away goal distributions and dependence;
- temporal validation diagram;
- model-family comparison table;
- MAE/RMSE by fold and season;
- probabilistic-score comparison;
- marginal and outcome calibration plots;
- prediction-interval coverage plot;
- attack/defence effects with uncertainty;
- feature stability/importance across folds;
- representative predictive score distributions;
- archival reproduction discrepancy table;
- ablation and sensitivity-analysis summary;
- runtime and model-complexity comparison.

Only figures that answer a research or diagnostic question should survive into the final manuscript.

## 34. Deliverables

### 34.1 Scientific deliverables

- preserved 2020 archival PDF;
- archival reproduction/reconstruction report;
- updated literature review and bibliography;
- canonical game-level analytical dataset specification;
- model-comparison results;
- complete revised thesis PDF;
- appendices and reproducibility statement.

### 34.2 Technical deliverables

- public or appropriately restricted GitHub repository;
- acquisition and data-build scripts;
- R and Python model implementations;
- leakage and data-quality tests;
- environment locks;
- CI workflow;
- generated figures/tables;
- model/data cards;
- tagged stable release, expected to be `v1.0.0` when truly complete.

### 34.3 Portfolio deliverables

- HowardSilvey.com project page;
- concise executive/project summary;
- selected bibliography or citation page;
- architecture/research visual;
- OBS-recorded technical demonstration;
- private “Business Solutions Portfolio” video publication unless Howard later changes the channel plan.

### 34.4 Institutional follow-up

After the revision is final, decide whether to contact Carleton's School of Mathematics and Statistics. The recommended request would be to retain the 2020 thesis as the historical submission and separately link or host the clearly labeled 2026 revision/extension. Do not retroactively date the new work as a revised 2020 submission. Any request to clean the accidental `-2` filename should be administrative and separate from authorship/version claims.

## 35. Portfolio and communication narrative

The strongest accurate narrative is:

> An undergraduate project identified a difficult forecasting problem and documented several unrealized extensions. In 2026, Howard R. Silvey preserved the original work, audited its limitations, reconstructed it where possible, rebuilt the study at the game level with leakage-safe temporal validation, and compared classical statistics, probabilistic count models, hierarchical methods, and machine learning in a reproducible research repository.

This demonstrates statistical judgment, humility about historical limitations, data engineering, predictive modeling, software quality, research communication, and the ability to modernize earlier work. The portfolio should never imply that the 2020 work used methods introduced only in 2026.

## 36. Hardware and local-development policy

### 36.1 Current status

Continue from the Chromebook. Audit writing, source inventory planning, literature review, data-source assessment, schema design, and much of the remote analysis do not require a hardware change.

### 36.2 Notice format

When a switch is genuinely useful, provide the explicit notice:

> **Hardware switch recommended:** This phase involves sustained local model training, environment setup, Docker, or application testing. Move to a higher-processing computer before beginning.

### 36.3 Likely switch triggers

- running the full repository locally in VS Code/RStudio;
- independently reproducing the environment;
- installing and maintaining both R and Python dependencies;
- executing large rolling hyperparameter searches;
- running Bayesian sampling or neural models for long periods;
- using Docker;
- building an interactive application;
- testing the entire pipeline end to end;
- recording the OBS demonstration;
- handling datasets too large or restricted for convenient browser transfer;
- debugging machine-specific deployment issues.

The preferred local setup is VS Code with Python, R, Jupyter, Quarto, GitHub, and later Docker extensions. RStudio may remain installed for focused R work.

## 37. Detailed execution programme

The 13 phases in Section 15 are the macro roadmap. The following granular programme controls execution. Steps may be split further, but should not be silently skipped.

### Programme A - Governance and archival recovery

1. Preserve the original Carleton PDF and record its checksum and public URL.
2. Create `DECISIONS.md`, `CHANGELOG.md`, and a project status ledger.
3. Lock naming, authorship, citation-order, and version labels.
4. Search all known devices, drives, email, and archives for original artifacts.
5. Inventory recovered files without modifying originals.
6. Classify each artifact as original, derivative, reconstructed, new, restricted, or unknown.
7. Decide whether exact reproduction is possible.
8. Create the archival reproduction issue list and discrepancy ledger.

### Programme B - Original-project reproduction

9. Restore or emulate the original R environment.
10. Reconstruct original source paths and data imports.
11. Verify the 123 team-season rows and approximately 40 variables.
12. Audit every original variable definition and transformation.
13. Reproduce the full OLS output and diagnose NA coefficients.
14. Reproduce backward elimination.
15. Reproduce forward selection.
16. Recover the exact two selected formulas and coefficients.
17. Regenerate all residual/normality plots.
18. Reproduce the three displayed prediction sets.
19. Reproduce LOOCV and confirm scale, RMSE, MAE, and \(R^2\).
20. Write the archival reproduction/reconstruction report.

### Programme C - Modern evidence and data design

21. Conduct the updated literature review using authoritative/primary sources where possible.
22. Create a literature matrix linking each model family to assumptions, output, strengths, and NHL relevance.
23. Audit candidate data sources, terms, schemas, and historical coverage.
24. Select primary and fallback data sources.
25. Lock included seasons and regular-season/playoff scope.
26. Lock goal conventions and overtime/shootout treatment.
27. Lock prediction timestamps and early/late forecast tracks.
28. Finalize canonical identifiers and game-level schema.
29. Finalize the feature registry and leakage classifications.
30. Pre-register the temporal folds, final holdout, metrics, and model-selection rule in the repository.

### Programme D - Data pipeline

31. Build raw-data acquisition with provenance and checksums.
32. Build canonical game/team/player identifier tables.
33. Build game and score tables with validation tests.
34. Build event/advanced-stat tables where permitted.
35. Build roster, injury, and goaltender inputs if reliable enough.
36. Implement lagged season-to-date and rolling features.
37. Implement opponent-adjusted/Elo features.
38. Implement schedule, rest, travel, and venue features.
39. Generate the feature-availability ledger automatically.
40. Execute leakage, join, missingness, and row-count tests.
41. Freeze the first canonical analytical dataset and data dictionary.

### Programme E - Modeling and validation

42. Run naive league/home-away/team-form baselines.
43. Run archival and corrected OLS/regularized baselines.
44. Fit independent Poisson models.
45. Diagnose dispersion and fit negative-binomial alternatives where warranted.
46. Fit and evaluate a joint/bivariate count model.
47. Evaluate a Dixon-Coles-style correction only if justified.
48. Fit hierarchical attack/defence models.
49. Fit dynamic team-strength/state-space models if feasible.
50. Fit controlled gradient-boosting and random-forest benchmarks.
51. Decide, from data volume and incremental research value, whether neural models proceed.
52. Calibrate candidate probabilistic outputs within development folds.
53. Perform feature-family ablations and forecast-time information ablations.
54. Check seeds, windows, fold boundaries, priors, and reasonable hyperparameter sensitivity.
55. Freeze primary, secondary, and baseline model configurations.
56. Run the untouched final holdout once under the locked protocol.
57. Generate the complete model-comparison and uncertainty package.

### Programme F - Manuscript, repository, and release

58. Draft methods directly from the pre-registered protocol.
59. Generate all result tables and figures from code.
60. Draft results without selecting only favorable metrics.
61. Draft discussion, limitations, and comparison with 2020.
62. Finalize the author's preface and abstract after results are frozen.
63. Complete citations, appendices, data availability, model cards, and reproduction notes.
64. Add unit, integration, leakage, and smoke tests to CI.
65. Verify the project from a clean environment.
66. Render and visually inspect the final thesis PDF.
67. Conduct a numerical, editorial, and claims audit.
68. Complete README, citation metadata, licence, changelog, and release notes.
69. Tag the stable repository release.
70. Build the HowardSilvey.com project presentation and selected bibliography.
71. Write and record the OBS demonstration from the frozen release.
72. Decide on the Carleton institutional follow-up and archival-link request.

## 38. Decision log seed

| Date | Decision | Status |
| --- | --- | --- |
| 2026-09-05 | Preserve the 2020 thesis as a separate archival work | Locked |
| 2026-09-05 | Use the revised title and subtitle shown in this document | Locked working identity |
| 2026-09-05 | Acknowledge the overloaded final-semester schedule professionally; omit private relationship/family details | Locked |
| 2026-09-05 | Reproduce/audit the original analysis before extending it | Locked |
| 2026-09-05 | Treat home and away goals as related count responses | Locked |
| 2026-09-05 | Use time-aware out-of-sample validation and probabilistic evaluation | Locked |
| 2026-09-05 | Do not target a predetermined \(R^2\) | Locked |
| 2026-09-05 | Use R for continuity and Python for engineering/benchmark breadth | Locked |
| 2026-09-05 | Continue from Chromebook until an explicit hardware-switch notice | Locked operating policy |
| 2026-09-05 | Propagate mid-sequence corrections through all remaining steps and continue unless paused | Locked operating policy |
| 2026-09-27 | Use this expanded audit as the Codex transfer baseline | Locked for handover |

Future decisions should add rows with dates, reasons, alternatives considered, and downstream consequences where useful.

## 39. Risk register

| Risk | Consequence | Mitigation |
| --- | --- | --- |
| Original files cannot be found | Exact reproduction impossible | Label reconstruction honestly; retain discrepancy ledger |
| Historical public tables changed or disappeared | Original values cannot be recovered | Use web archives, checksums, multiple sources, and explicit uncertainty |
| Data licensing restricts publication | Public repo cannot contain raw data | Acquisition scripts, fixtures, schemas, and data-availability statement |
| Advanced-stat definitions drift | False across-season comparability | Definition audit, compatible-period restriction, source/era indicators |
| Pregame availability is unclear | Leakage and unrealistic performance | Prediction timestamp, feature registry, source-time audit |
| Too many models dilute the thesis | Shallow comparisons and compute waste | Model ladder, inclusion hypotheses, stopping criteria |
| Hyperparameter search uses final holdout | Optimistic performance | Research firewall and nested/development-only tuning |
| Joint models are hard to implement or unstable | Schedule and reproducibility risk | Independent count baseline first; advance only after diagnostics |
| Player/injury data are incomplete | Missingness and bias | Separate optional feature track; base model remains team/game-level |
| Bayesian/neural compute becomes excessive | Hardware/time bottleneck | Early smoke tests, compute budgets, simplified models, explicit switch notice |
| Metrics disagree | Ambiguous winner | Pre-specified primary metrics and model-selection rule |
| Report overstates portfolio claims | Scientific/reputational risk | Claims audit and exact archival/new-result separation |
| NHL rules/teams change across eras | Distribution shift | Season effects, rule-era notes, temporal evaluation |

## 40. Definition of done

The project is complete only when all of the following are true:

- the 2020 work is preserved and accurately characterized;
- reproduction status is explicitly resolved;
- the game-level dataset and feature availability are documented;
- automated leakage tests pass;
- temporal validation and the final holdout follow the locked protocol;
- honest baselines and justified advanced models are compared;
- probability calibration and uncertainty are evaluated;
- the primary and secondary models are frozen and reproducible;
- every manuscript number is generated from versioned code/data;
- R and Python environments are locked;
- CI and a clean-environment verification succeed;
- the final report receives visual and numerical QA;
- data rights and repository contents are appropriate;
- the stable release, portfolio page, and demonstration all describe the same frozen findings;
- limitations and negative results remain visible rather than edited away.

## 41. Next required user input and immediate next action

The next action is not model fitting. Howard should provide any surviving original project materials, preferably together in one ZIP without renaming or editing the internal files. Particularly valuable items are R scripts/history, CSV or Excel data, the original Word document, exported figures, notes, and email attachments.

Once received, the work sequence is:

1. inventory files and calculate checksums;
2. identify sensitive/restricted materials;
3. map artifacts to thesis sections, tables, figures, and results;
4. determine whether the 2020 analysis can be reproduced or only reconstructed;
5. produce the archival reproduction plan and first executable environment specification.

If no original files survive, state that explicitly. The project will then proceed under the reconstruction fallback without treating the absence as a project failure.

**Hardware status:** No switch recommended at this checkpoint.
