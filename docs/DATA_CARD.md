# Data card

**Source:** MoneyPuck.com explicitly listed all-team game-by-game download.
**Scope:** 2016-17 through 2024-25 NHL regular seasons, situation all.
**Unit:** one ordered home/away paired game, derived from mirrored team rows.
**Included:** 10,969 games. **Excluded:** one incomplete duration record, 2019020876.
**Primary response:** reconstructed regulation home and away goals.

## Checks

Require one HOME and one AWAY record, unique game ID, opponent symmetry,
mirrored goals, matching dates/seasons/duration, nonnegative integer scores,
valid regular-season duration and valid post-regulation scores. Fifty-four
deterministic stratified reconstructions agree with official scoring.

## Information and limitations

The modern snapshot can include historical corrections. Calendar-date batching
is verified, but publication-time availability is not. Rest uses source dates;
neutral sites and exact venue schedules are not modeled. Historical shots and
attempts may include overtime while goals use regulation only. Renamed/new
team labels use pooled cold starts rather than undocumented franchise merging.

## Access

Raw and row-level outputs stay local. The exact source hash is recorded in
`reports/source-manifest.json`. Current downloads may differ. MoneyPuck must be
credited in every empirical display and its non-commercial terms respected.
