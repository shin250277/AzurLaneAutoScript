# KR compatibility regression ledger

Audit base: `619b6ecdc` (11/20 recorded baseline: 854 checks).
Scope: authored KR image/currency fixes; account configuration and untracked user
probes/deployment files are excluded. Commands run from the repository root with
`toolkit/python.exe -B` (Python 3.7), no device input or network.
Windows OCR needs the host OCR runtime; sandbox socket initialization failures
are NOT test passes. Full discovery is approximately six minutes.

## Recipe-name assets → recipe identity → island production

- Downstream: `module/island_handler/recipe.py`, production/season consumers.
- Dependency evidence: `rg -n "KoreanIslandNameOcr|IslandRecipe|IslandProduction" module/island module/island_handler`.
- Acceptance: `toolkit/python.exe -B -m unittest dev_tools.test_kr_final_replay_titles dev_tools.test_kr_season_update dev_tools.test_kr_season_claim`.
- Observed-frame reconciliation: `toolkit/python.exe -B -m dev_tools.replay_kr_recipe_audits` (local log frames required; missing evidence is not a pass).
- Propagation: any identity/mapping change runs full `test_*.py` discovery, including reservation, recipe selection, production, and season consumers.

## Event currency / item OCR → clerk → event shop

- Downstream: `module/shop_event/item.py`, `clerk.py`, `shop_event.py`.
- Dependency evidence: `rg -n "KoreanEventCurrency|validated_point_items|EventShopItemGrid|EventShopClerk" module/shop_event`.
- Acceptance: `toolkit/python.exe -B -m unittest dev_tools.test_kr_event_currency dev_tools.test_kr_shop_counter_retry dev_tools.test_kr_event_shop_safety dev_tools.test_kr_shop_ship_amount dev_tools.test_event_shop_october dev_tools.test_kr_event_shop_frame`.
- Propagation: currency, quantity, stock or reference changes require all listed consumers and full discovery. No exemption for a template-only change that changes a purchasing decision.
- Defect evidence: actual saved top/middle/bottom/shifted frames, diamonds/blank negatives, fresh-scan currency/amount changes, invalid `100/00` counter, preservation of valid zero stock.
- First full run: 864 tests, two fixture-initialization errors; corrected both explicit test fixtures rather than suppressing production errors. Subsequent full run: 873 tests, exit0,343.167s. One additional winter contract check passed separately; final discovery recorded in the dated report.

## OpSi repeating tasks → campaign scheduler wrappers

- Dependency evidence: `rg -n "os_meowfficer_farming|os_hazard1_leveling" module/campaign/os_run.py module/os/tasks`.
- Acceptance: `toolkit/python.exe -B -m unittest dev_tools.test_os_task_stop_boundaries`.
- Propagation: stop/AP exception behavior changes require wrapper and task checks; no gameplay run implied by these mocks.

## Whole changed tree gate

Sold-out scan dependency: `scan_all` → `kr_sold_out_page` → read-only tool and
purchase inventory. Acceptance: `dev_tools.test_kr_shop_sold_out` and
`dev_tools.test_event_shop_scan_rows`: white/black/available/one-missing-badge
negatives, partial final row, foreign-server rejection. Full discovery required.
Actual read-only GUI run reached bottom and Finish at16:46:53; no purchase.

`toolkit/python.exe -B -m unittest discover -s dev_tools -p "test_*.py"`

Also run `toolkit/python.exe -B -m dev_tools.kr_asset_inventory`,
`toolkit/python.exe -B -m dev_tools.kr_compatibility_audit`, and `git diff --check`.
All green is regression evidence for this change, not proof of all live game
conditions. Feature evidence and limitations are in `doc/KR_FEATURE_MATRIX.md`
and `doc/KR_COMPATIBILITY_2026-11-20.md`.

Closeout:879 checks passed in394.844s. The last overlapping full run had one
failure from temporary plate-name candidates read before their removal; those
nine candidate files were not committed. Post-removal31 checks (including the
exact failed test) and9 currency/plate checks passed. Do not label the last full
invocation itself green; see the dated report for timings and live evidence.
