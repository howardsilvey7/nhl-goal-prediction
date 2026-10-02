# Model card

**Task:** paired NHL regulation-goal probability forecasting from earlier-date
team histories. **Research version:** 0.1.0. **Primary metric:** joint NLL.

**Frozen label:** bivariate_poisson, exactly tied with independent Poisson in
development. Estimated shared dependence rho is zero, so the prediction
distribution is the independent-Poisson model. Do not claim a dependence advantage.

## Performance on the frozen final season

1,312 games, 2024-25. Joint NLL 3.85526; combined MAE 1.38806; combined RMSE
1.72034; regulation-outcome Brier 0.62735. League baseline NLL 3.87545.
Paired week-bootstrap NLL difference -0.02019, 95% interval [-0.03101, -0.00774].
Marginal central-90% coverage: home 94.82%, away 95.73%; mean width 5.596 goals.
Discrete endpoints and broad intervals limit interpretations of coverage.

## Appropriate interpretation

Modest probability-quality improvement; very small MAE improvement. Ridge with
Poisson margins has slightly lower numerical holdout NLL but was not substituted
after observing test performance. Tree-model intervals versus baseline cross zero.

## Limits

Retrospective revised snapshots; calendar-day boundary; no exact historical
publication times, rosters or goalies; positive-only dependence; one final season;
28 bootstrap week blocks and remaining cross-week team dependence. The model
is not a causal tool, profitable betting claim or final-winner forecast.

Bayesian posterior inference, latent dynamics, xG and neural models are not
implemented. The attack/defence variant is frequentist penalized regression.
