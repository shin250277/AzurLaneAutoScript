# KR live event check — 2026-09-23

Executed through the running Alas.exe GUI, not a headless device script.

## Observed

- 21:26 KST: RaidInspect navigated to page_raid and finished normally.
- Live event: 「“거물”의 예고장」, raid_20260827 (BIGSHOT).
- Displayed period: 9.10–9.24 maintenance.
- Hard / normal / easy remaining: 15/15 each; special tickets: 5; PT: 9,933.
- Local evidence: log/kr_raid_inspect.png and log/2026-09-23_alas.txt.
- 21:30 KST: RaidTrial started hard mode, read oil 14,800, and stopped
  before entering battle because the trial oil floor is 20,000.
- The oil guard rescheduled Raid.NextRun to 2026-09-24 00:47:19.
  No battle, ticket use, purchase, or retirement was performed by this trial.

## Scope and pending validation

RaidInspect only navigates and saves a frame. RaidTrial uses the configured
KR non-EX difficulty with a one-run limit, ticket use disabled, old retirement
mode with every rarity disabled, and task balancing disabled.

Battle completion, reward handling, and difficulty-specific fleet availability
are **not verified** today. The previous empty hard fleet must not be assumed
fixed. User confirmation was requested before reducing the oil protection floor.

Offline safety tests are separate from live battle validation.
