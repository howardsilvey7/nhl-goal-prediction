# Research edition 0.1.0

This prerelease contains a formal 2026 thesis revision with the completed first
empirical experiment, a source-verified archival audit, and a frozen research
protocol, each in PDF and editable DOCX. PDF is the primary sharing format.

The experiment compares nine variants on 10,969 games. The final holdout has
1,312 games. The frozen count model improves joint NLL modestly over the league
baseline (3.85526 vs 3.87545); MAE changes very little (1.38806 vs 1.39229).
The bivariate shared component is zero, so there is no demonstrated dependence
gain. All models and negative results are reported.

The original 2020 PDF is unchanged. Its headline results were visually checked,
not reproduced by executing original code. Original data/code recovery remains
open. The date-based feature design does not establish exact publication-time
availability. Independent academic review and broader extensions remain pending.

Verification includes synthetic invariant tests, 54 official score checks,
frozen Python replay and base-R Poisson parity. Raw and row-level source data
are excluded; MoneyPuck.com is credited and data-use terms remain separate.

Do not describe this release as completion of every research-baseline gate,
a stable 1.0.0 thesis, or a new Carleton submission.
