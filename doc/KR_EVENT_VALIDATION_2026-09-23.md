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

At the initial inspection, battle completion and fleet availability remained
unverified. The approved retry results below supersede that initial status.

Offline safety tests are separate from live battle validation.

## Approved live retry

The user approved a temporary oil floor of 1,000 for at most one completed run
per non-EX difficulty. Tickets, premium currency and automatic retirement remain
excluded. The trial's source-level floor will be restored after this session.

- 21:39: hard fleet now contains six ships (plus three submarines). Preparation
  stopped after 30 seconds because RAID_FLEET_PREPARATION still used JP text.
- Reproduced a failed template match on log/kr_raid_preparation_timeout.png.
  Extracted only the Korean shortcut button into assets/kr/raid and changed the
  KR asset mapping. The same frame then matched; blank-frame rejection passed.
- 21:41–21:42: Alas.exe retry recognized the shortcut, handled the automation
  notice, entered auto combat, detected BATTLE_STATUS_S, processed EXP_INFO,
  logged RAID END and exited normally after exactly one hard battle.
- 21:43: normal completed one S-rank battle and result handling, logged RAID END
  at 21:43:53 and exited normally. No further fix was needed.
- 21:45: easy completed one S-rank battle and result handling, logged RAID END
  at 21:45:46 and exited normally.
- Final game screen: each difficulty 14/15, PT 10,153 (increase 220), special
  tickets still 5. No premium purchase or retirement was executed.
- Restored the trial code's oil floor to 20,000. All 368 offline tests passed.

The above run verified non-EX entry, combat, result handling and return.

## EX, cumulative rewards and shop follow-up

- 21:49: EventShopScan reached the supply shop and returned "There is no event
  shop currently". The live screenshot also showed no event exchange tab.
  This is an absent-shop branch verification, not a purchase test. Gems: 6,206.
- 21:51: personal reward dialog opened. Phase 13 (7,000 PT) through phase 16
  (10,000 PT) were available at 10,153 PT.
- 21:52–21:54: claimed four stages through ALAS: T3 skill books (support 1,
  defense 2), SSR cat box 1, destroyer retrofit blueprint 1, and the displayed
  rainbow "상급 지향형" item 1. Each acquisition frame was saved locally.
- Claim button became gray and the next displayed unearned tier was phase 17,
  14,000 PT. The bounded claim handler requires KR + this event + reward header
  and an active color/template match. No purchase calls are present.
- Added a separate RaidRewardClaim GUI tool. It requires the personal reward
  dialog to already be open; it does not navigate or initiate battle.
- 21:55–21:57: EX entrance matched, ticket OCR read 5, six ships were present.
  Opened the explicit practice route and verified ticket use 0/5 and oil cost 0
  on preparation before starting one practice battle.
- Practice reached "전투완료", damage 461,503, merit 0. ALAS failed to recognize
  two Korean result screens (battle result and experience confirmation).
- Added KR-only result/confirmation templates. At 22:01 and 22:03, resumed
  only result handling through Alas.exe; the fixed handlers advanced both
  screens and returned to page_raid. No second battle or retry was started.
- Final frame: tickets 5, PT 10,153, easy/normal/hard 14/15 unchanged.
  Evidence: log/kr_bigshot_ex_practice_result.png and daily ALAS log.
- Temporary diagnostic changes to RaidInspect were removed; it remains
  navigation-only. EX was practice, not a ticket-consuming ranked run. Approval
  for one real EX ticket was requested but had not been received in this turn.

The EX fixes were revalidated from the blocked result screens, not by repeating
an entire battle after the patch. No premium currency was used.
