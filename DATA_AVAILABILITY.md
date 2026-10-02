# Data availability

MoneyPuck.com supplies the modern input through its publicly listed
[all-team game download](https://moneypuck.com/data.htm). Its page permits
non-commercial use with attribution. This study uses that listed download;
it does not scrape unlisted pages or claim a blanket open-data license.

The repository contains source URL, completion timestamp, SHA256, schema,
aggregate research outputs, exclusions and validation-case identifiers.
Raw files, canonical game rows, feature rows and row-level predictions remain
local and git-ignored. No code license supersedes the source's terms.

The initial snapshot is 126,526,698 bytes (verify the exact size against
`reports/source-manifest.json`; the manifest is authoritative).
Its SHA256 is `27a6d0dcb1659eeb6780b955f058f2af5b33b5eba266bf120cdb23fb7f8477bf`.
The current download may differ. Frozen empirical replay requires this exact
snapshot; source updates must be separately versioned and reviewed.

Official NHL period-scoring responses support 54 deterministic score checks.
Only case IDs, endpoint references and pass/fail results are published, without
logos, player photographs, response dumps or redistributed event feeds.

Original 2020 input data and executable NHL R code have not been recovered in
the targeted local search. Exact reproduction is unresolved. The publicly hosted
author's original PDF is preserved unchanged and cited separately.

Synthetic fixtures in the tests are generated for software checks and are not
evidence about NHL model performance. The 2025-26 season is excluded from all
outcome analyses in this release and reserved for a future study.
