# KR ALAS 전체 기능 확인표

기준: 2026-10-22. `menu.json`과 `task.yaml`의 합집합 **75개** 메뉴 항목을 `alas.py` 실행 진입점과 대조한다. 설정 화면과 진단 도구도 빠뜨리지 않되 게임 실기 통과 수에 섞지 않는다. 개별 테스트 514개 통과는 이 표의 실기 완료율이 아니다.

현재 전수 **목록화**만 완료했으며 전수 **실기 검증**은 미완료다. ‘실기’도 기재된 해역·옵션·날짜 범위만 뜻한다. 공통 실행 엔진을 쓰는 복제 슬롯이나 이벤트 미개방은 통과로 자동 승격하지 않는다.

근거: [11/9 수정·실기 기록](KR_VALIDATION_2026-11-09.md), [11/8 재개 기록](KR_VALIDATION_2026-11-08.md), [11/6 재개 기록](KR_VALIDATION_2026-11-06.md), [10/21 기록](KR_VALIDATION_2026-10-21.md), [10/22 기록](KR_VALIDATION_2026-10-22.md), [10/2 기록](KR_VALIDATION_2026-10-02.md). 과거 문서의 범위를 현재 완료로 확대하지 않는다. 원시 계정 로그·설정·화면은 첨부하지 않는다.

## 전체 메뉴와 세부 설정 그룹

### 한국 신규 섬 시즌 일정 — 2026-11-09 갱신

사용자 확인 일정은 **2026-11-19 점검 후**다. 해외11/5 개방을 KR에 적용하지 않는다. 신규 시즌 실기는 개방 조건 대기이며 현재 일반 생산의 구현/검증 미완료와 구분한다. 날짜 도달만으로 신규 시즌을 자동 활성화하지 않는다. 기존 데이터의11/19 12:00은 점검 종료 확인값이 아니므로 신규 시작 시각으로 재사용하지 않는다. 개방 후 실제 시즌/품목/과제 및 보호 재고를 확인해야 자동 연계를 검증할 수 있다.

| ID | 분류 | 설정 그룹(별도 확인 범위) | 판정 | 확인한 범위 / 다음 확인 |
|---|---|---|---|---|
| `Alas` | Alas | Emulator, EmulatorInfo, Error, Optimization, DropRecord | 부분 실기 | 로그인·예약·오류 중단 확인. 통신/최적화/알림/통계 옵션 전 조합은 미확인 |
| `General` | Alas | Retirement, OneClickRetire, Enhance, OldRetire | 부분 실기 | 기존 기준 일괄퇴역 10/21 통과. 강화·돌파 보존·각 희귀도 경계 별도 확인 필요 |
| `Restart` | Alas | Scheduler | 실기 | 11/6 점검 후 로그인/08:39 정상 종료 재확인. 장애별 복구는 별도 분기 |
| `Main` | Farm | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 실기 | 10/21 12-4 1회 보스/보상/종료. 모든 해역 통과 의미 아님 |
| `Main2` | Farm | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 오프라인·공통경로 | 10/22 합성 설정으로 Main/Main2/Main3 해역·횟수·스케줄러 바인딩 및 쓰기 경로 격리 통과. 별도 슬롯 실기 완료는 아님 |
| `Main3` | Farm | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 오프라인·공통경로 | 10/22 합성 설정으로 Main/Main2/Main3 해역·횟수·스케줄러 바인딩 및 쓰기 경로 격리 통과. 별도 슬롯 실기 완료는 아님 |
| `GemsFarming` | Farm | Scheduler, GemsFarming, EquipmentCode, Campaign, StopCondition, Fleet, Submarine, Emotion | 미확인·범위제한 | 함선 확보/퇴역 반복과 별도 육성 동작. 현재 비활성 유지; 일반 일괄퇴역 승인으로 확대하지 않음 |
| `EventGeneral` | Event | EventGeneral, TaskBalancer | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `Event` | Event | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 실기 | 11/9 템페스타와 안개회랑 T1~T6 개방 및 T6 연속2회/횟수0 자동 종료/메인 복귀. 긴급 의뢰 팝업 보완의 동일 화면 실기는 별도 |
| `Event2` | Event | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `Raid` | Event | Scheduler, Raid, Campaign, StopCondition, Emotion | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `Hospital` | Event | Scheduler, Hospital, StopCondition, Emotion | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `Coalition` | Event | Scheduler, Campaign, Coalition, StopCondition, Emotion | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `EventShop` | Event | Scheduler, EventShop | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `WarArchives` | Event | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 실기 | 10/21 T1 1회 보스/보상/자동 비활성 |
| `EventA` | EventDaily | Scheduler, EventDaily, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `EventB` | EventDaily | Scheduler, EventDaily, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `EventC` | EventDaily | Scheduler, EventDaily, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `EventD` | EventDaily | Scheduler, EventDaily, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `EventSp` | EventDaily | Scheduler, Campaign, StopCondition, Fleet, Submarine, Emotion, HpControl, EnemyPriority | 실기 | 11/9 사용자 편성 후17:15:41 보스S/17:15:53 종료 및 다음날 예약. 임시false 복원, 정기의뢰 후17:17:04 메인 복귀 |
| `RaidDaily` | EventDaily | Scheduler, RaidDaily, Campaign, StopCondition, Emotion | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `CoalitionSp` | EventDaily | Scheduler, Campaign, Coalition, StopCondition, Emotion | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `Commission` | Reward | Scheduler, Commission | 실기 | 11/6 08:40 수령·재출항/4칸/정상 종료 재확인. 신규 의뢰 이름/기름 의뢰 보호는 별도 분기 |
| `Tactical` | Reward | Scheduler, Tactical, ControlExpOverflow, AddNewStudent | 부분 실기 | 10/21 16:44 기존 필터 교재 사용/2칸 재시작. 새 학생/경험치 경계는 미확인 |
| `Research` | Reward | Scheduler, Research | 실기 | 10/21~22 수령·대기열 보충. 연구 종류별 지출 경계 별도 |
| `Dorm` | Reward | Scheduler, Dorm, BuyFurniture | 부분 실기 | 11/8 보유음식 보급/빠른 수집/21:58 정상 종료 재확인, 11/6 수집 시간초과 경고 미재발. 가구 구매 미확인 |
| `Meowfficer` | Reward | Scheduler, Meowfficer, MeowfficerTrain | 부분 실기·육성 대상 필요 | 11/6 기존 구매계획 1회 처리/bought=1/15/추가계획0/작업 종료. 훈련 비활성 유지; 훈련·강화 대상 미확정 |
| `Guild` | Reward | Scheduler, GuildLogistics, GuildOperation | 부분 실기·승인필요 | 로비/임무 보상 통과. 기부0; 공유 작전·새 임무 선택 별도 승인 유지 |
| `Reward` | Reward | Scheduler, Reward | 실기 | 10/22 자원·임무 수령/메인 복귀. 일시적 시간초과 이력 별도 |
| `Awaken` | Reward | Scheduler, Awaken | 조건부족 | 11/6 대상 없음/필터 복원/정상 종료 재확인. 실제 재료 사용 각성 미검증 |
| `Daily` | DailyMission | Scheduler, Daily | 부분 실기 | 11/8 잘린 KR 버튼의 이중 크롭/목록 오탐 수정 후 빠른 완료·보상·23:42 정상 종료. 미해금 유형 및 수동전투 미검증 |
| `Hard` | DailyMission | Scheduler, Hard | 실기 | 11/8 11-4 3회 잔여0/23:48 정상종료 재확인 |
| `Exercise` | DailyMission | Scheduler, Exercise | 실기 | 10/21 10회 전투/보상/잔여 처리 |
| `ShopFrequent` | DailyMission | Scheduler, GeneralShop | 부분 실기 | 기존 비유료 필터 실행. 미구매 품목/보호 재고 경계 확인 필요 |
| `ShopOnce` | DailyMission | Scheduler, GuildShop, MedalShop2, MeritShop, CoreShop | 부분 실기 | 11/6 길드·훈장 거래 및 정상 종료. 공훈/코어 필터 순회는 실제 구매 통과와 구분 |
| `Shipyard` | DailyMission | Scheduler, ShipyardDr, Shipyard | 조건·승인필요 | 신규 개발 대상 선택 금지 유지. 기존 대상 무료/할인 강화 분기 증거 대조 필요 |
| `Gacha` | DailyMission | Scheduler, Gacha | 실기 | 10/21 소형1회 제출/함선수령,10/22 0회 수령전용 통과. 유료 쾌속 금지 |
| `Freebies` | DailyMission | Scheduler, BattlePass, DataKey, Mail, SupplyPack | 부분 실기 | 정상 종료. 패스/키/우편/무료패키지별 신규 수령 증거 구분 필요 |
| `Minigame` | DailyMission | Scheduler | 실기 | 11/6 무료 코인10회/보상/정상 종료 재확인. 모든 게임 유형은 아님 |
| `PrivateQuarters` | DailyMission | Scheduler, PrivateQuarters | 부분 실기 | 11/6 기존 금화 선물 및 잔여3/3에서 상호작용3회/정상종료. 다른 대상·유료 선물은 미검증 |
| `OpsiGeneral` | Opsi | OpsiGeneral | 공통설정 | 기존 비유료 자원 상한/함대/잠수함/체력 보호 유지. 옵션별 증거 대조 필요 |
| `OpsiAshBeacon` | Opsi | Scheduler, OpsiAshBeacon | 부분 실기 | 10/21 본인META 1회 공격/피해/종료. 격파 보상 미확인 |
| `OpsiAshAssist` | Opsi | Scheduler, OpsiAshAssist | 부분 실기·수정 재검증 | 11/8 지원3회/보상/잔여0,23:53:15 정상종료·메인 복귀. 11/9 지원3회 후 별도 누적 보상의 META 결정 획득 카드에서00:31:34 중단 발견. 전용 문구+카드 두 앵커 보완 및 실패 화면 양성/빈 화면·한 앵커 음성 재생 통과. 동일 보상 재출현 실기는 아직 미확인 |
| `OpsiExplore` | Opsi | Scheduler, OpsiExplore, OpsiFleet | 부분 실기 | 10/2 다수 해역 개척 통과. 전체 개척 완료 아님 |
| `OpsiShop` | Opsi | Scheduler, OpsiShop | 실기 | 10/21 기존 비유료 물품15종 구매/정상종료 |
| `OpsiVoucher` | Opsi | Scheduler, OpsiVoucher | 부분 실기 | 11/6 교환권 상점 순회/보유 기록 사용/정상 종료/다음 월 예약. 빈 품목 시간초과 경고가 있어 품목별 구매 통과로 확대하지 않음 |
| `OpsiDaily` | Opsi | Scheduler, OpsiDaily, OpsiFleet | 실기 | 10/21 16:37 남은임무 없음/정상종료. 과거 카리브 좌표순환 재현은 별도 |
| `OpsiObscure` | Opsi | Scheduler, OpsiObscure, OpsiFleet | 조건부족 | 10/21 좌표없음 종료. 현재 좌표 전투 미검증; 일괄좌표사용 연계 범위 확인 |
| `OpsiAbyssal` | Opsi | Scheduler, OpsiAbyssal, OpsiFleetFilter | 조건부족 | 현재 대상/전투력 확인 필요. 기존 함대·체력 보호 유지 |
| `OpsiArchive` | Opsi | Scheduler, OpsiFleet | 실기 | 10/21 장치7회 구매→연속임무→보상→구매재고없음→정상종료 |
| `OpsiStronghold` | Opsi | Scheduler, OpsiStronghold, OpsiFleetFilter | 조건부족 | 기존 전투력 부족 실패. 같은 조건 무리 재시도 금지 |
| `OpsiMonthBoss` | Opsi | Scheduler, OpsiMonthBoss, OpsiFleetFilter | 조건부족 | 적응도 보호 유지. 강제 실행 금지; 현재 수치 읽기 확인 가능 |
| `OpsiMeowfficerFarming` | Opsi | Scheduler, OpsiMeowfficerFarming, OpsiFleet | 미확인 | 현재 AP/좌표/연료 상한과 종료 조건 확인 후 제한된 실기 필요 |
| `OpsiHazard1Leveling` | Opsi | Scheduler, OpsiHazard1Leveling, OpsiFleet | 미확인 | 현재 함대/체력/종료 조건 확인 후 제한된 실기 필요 |
| `OpsiCrossMonth` | Opsi | Scheduler | 발생조건 | 월말 전환 전용. 날짜변조/보호우회 없이 오프라인 경계 검사 |
| `IslandProduction` | Island | Scheduler, IslandProduction | 부분 실기·修正 재검증 | 11/9 농장·목장·양식장·광산·벌목·과수원·원예·전자공방·식당601 감사/관리 복귀 확인(모든 렌더링 변형 통과 아님). 달걀/목장/샐러드/필터 실제 수령 및19:16 즉시 시각 삭제 저장 통과.19:29 카페12배치/필터1배치 신규 시작 즉시 저장·정상 종료,19:50 양모 시작 저장 통과. 다음 카페21:29/필터23:29/양모11/10 00:50 수령은 시간 대기.19:51 카페 이름 실패 후9변형 보완/전체718개 통과,20:01 GUI 재검증 중/반복 활성false. 보호 재고·식당 예약분 유지, 구매 없음 |
| `IslandOrder` | Island | Scheduler, IslandOrder | 일반 주문 실기 통과·나머지 미검증 | 10/22 일반 주문 14건 제출/보상/횟수 감소, 재고 부족 1건 보호 건너뛰기, 정상 종료/메인 복귀/임시 활성 해제. 긴급·시즌·포기는 실행하지 않음 |
| `IslandFreebie` | Island | Scheduler, IslandFreebie | 실기 | 11/9 19:31:45 지급 연출 종료→19:31:47 수령→19:31:53 Received freebie/정상 종료. 공유false 유지, 임시 활성false 복원 |
| `IslandCollect` | Island | Scheduler | 실기 | 11/9 19:32:17 Collect successfully/작업 정상 종료,19:32:22 메인 복귀. 임시false 복원. 일부 캐릭터 OCR None 경고는 전체 성공과 별도 기록 |
| `IslandSeasonTask` | Island | Scheduler, IslandSeasonTask | 현재 시즌 목표 연계 실기 | 11/9 08:14 전체 목록 두 스캔의 미완료11과제/8품목 일치→TaskTarget 반영→정상 종료/메인 복귀 통과, 임시false 복원. 이름 누락·행 건너뛰기·스크롤 횟수 오판정 수정. 보호 재고·식당 export/구매/교환 없음. 보상수령 및11/19 점검 후 신규 시즌은 별도 미검증 |
| `IslandBusiness` | Island | Scheduler, IslandRestaurant | 실기 | 10/21 기존 메뉴/등급/보유음식으로 5곳 운영. 10/2 정산/휴가/메인복귀 |
| `Daemon` | Tool | Daemon | 미확인 | 사용자 수동 플레이 보조. 전투/보상 핸들러 단위 검증과 별도 |
| `OpsiDaemon` | Tool | OpsiDaemon | 미확인 | 대형작전 수동 플레이 보조. 일반 자동 작업과 별도 |
| `EventStory` | Tool | EventStory | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `IslandProductionPlanner` | Tool | IslandProductionPlanner | 읽기 전용 계산 통과 | 11/9 19:24 계산 성공(생산64/구매24/교환1 제안). 실제 export/구매/교환 없음. 모의 export 필드 범위·직렬화 실패·식당 메뉴 누락 시 무변경 통과. 실제 설정 적용은 별도 승인/검증 |
| `IslandProductionTrial` | Tool | 독립 도구 | 한정도구 | 과거 감자1회 전용 영수증 보호. 재승인 없이 영수증 초기화/반복 금지 |
| `EventShopScan` | Tool | 독립 도구 | 스캔 종료 실기·일부 미인식 | 11/9 19:53~54 8페이지/31품목/바닥 도달·정상 종료. 신규3품목/PlateUnknown은 미인식, 구매 없음. 전체 상품 판독/구매 통과와 구분 |
| `IslandInspect` | Tool | 독립 도구 | 읽기 진단·복귀 실기 | 11/9 19:54~55 주문 요구/현재 시즌 끝까지 고유29과제 읽기·메인 복귀 통과. 일부 수령 완료 제목 미인식은 남음. 주문 제출/보상 수령/목표 변경 없음 |
| `IslandOrderTrial` | Tool | 독립 도구 | 한정도구 | 철광석1회 전용. 일반주문 대체 아님; 원본task.yaml 누락 수정 |
| `RaidInspect` | Tool | 독립 도구 | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `RaidRewardClaim` | Tool | 독립 도구 | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `RaidTrial` | Tool | 독립 도구 | 발생조건·미확인 | 이벤트/특수 도구. 현재 개방·보상·종료 조건을 먼저 확인; 과거 이벤트 통과를 현재 통과로 대체하지 않음 |
| `Benchmark` | Tool | Benchmark | 진단도구 | 장치 성능 검사. 게임 기능 완료로 집계하지 않음 |
| `AzurLaneUncensored` | Tool | AzurLaneUncensored | 범위제한 | 게임 파일/표현 변경 도구. 기능검증 명목으로 실행하지 않음 |
| `GameManager` | Tool | GameManager | 진단도구 | 앱/에뮬레이터 관리. 일상게임 기능과 별도; 프로세스 종료 부작용 검토 |

## 메뉴 외 실행 진입점

11/9 소스 대조 결과를 아래처럼 구분한다. 메뉴에 없다는 이유로 누락하지 않되 폐지된 기능을 현재 미완료 기능으로 세지 않는다. `start`, `goto_main`, `wait_until`, `loop`, `run`, 오류 로그 저장은 공통 운용 경로다.

| 실행 진입점 | 현재 코드 범위 | 판정 |
|---|---|---|
| `sos` | `CampaignSos.run`은 KR/CN/EN/JP에서 화면 진입 전에 스케줄러 비활성화·task_stop | KR 폐지 기능. 현재 실기 대상 아님 |
| `maritime_escort` | 이벤트 기간 검사 후 진입·철수 보상, 잔여 없으면 다음 갱신 예약 | 이벤트 발생조건. 상시 비이벤트 미완료로 세지 않음 |
| `c72_mystery_farming` | 설정의 해역/폴더/모드를 같은 `CampaignRun.run`에 전달 | 공통 엔진 진입점 확인. 해당 특수 해역 실기와 별개 |
| `c122_medium_leveling` | 동일 `CampaignRun.run` 경로 | 공통 엔진 진입점 확인. 별도 레벨링 실기 통과 아님 |
| `c124_large_leveling` | 동일 `CampaignRun.run` 경로 | 공통 엔진 진입점 확인. 별도 레벨링 실기 통과 아님 |

## 공통 분기 — 별도 완료 판정 필요

### 이미지 등록 정적 감사 (10/22)

`module/**/assets.py`의 Button/Template 선언 1,797개를 AST로 읽어 KR 파일 참조를 확인했다. 1,797개 모두 KR 키가 있고 참조 파일 누락은 0개다. 하지만 KR 경로는 264개이고 1,533개는 외국 서버/공통 경로를 사용한다. KR 경로 중 2개는 외국 서버 파일과 바이트가 같다. 따라서 ‘한국 서버 실측 이미지를 전부 갖췄다’는 판정은 할 수 없다. 공통 아이콘 재사용 자체는 오류가 아니며 실제 화면 일치 검사가 필요하다. 이 수치는 생성 assets.py 선언 범위이며 인라인 버튼/OCR/동적 경로 전체 개수는 아니다.

### 이번 코드 대조

- 후속 [이미지 호환 보고서](KR_IMAGE_COMPATIBILITY.md): 1,797개 디코딩/좌표 검사와 EMP·S승리 관찰 화면 재생을 분리해 기록. 빈 화면 템플릿 오인식 수정, 월말 날짜 보호 오프라인 검사 추가. 월말 실기 완료는 아님.
- 생산 계획 최적화 실패 시 기존 설정을 빈 결과로 덮어쓰지 않도록 export 전에 중단. 읽기 전용 실패 분석은 유지한다.

- `IslandOrderTrial`의 메뉴/실행 함수는 있으나 원본 task.yaml 항목이 빠진 것을 수정했다. 75개 목록 일치·실행 함수 존재·문서 누락 방지 검사 통과.
- 섬 주문의 cooldown 목록을 순회 중 삭제하여 연속 두 번째 대기 주문이 남던 결함을 실패 테스트로 재현하고 필터 방식으로 수정했다. 실기 발동은 별도 확인한다.
- Main/Main2/Main3 합성 설정 바인딩/변경 경로 격리 검사 통과. 계정 설정·게임 장치는 사용하지 않았다.

- 전투: 해역 선택, 함대/잠수함, 매복/탄약/체력, 보스/패배/철수, 결과/경험치/함선획득, 재출격 및 횟수 종료.
- 도크: 기존 게임 일괄퇴역 설정만 사용. 보호·희귀도·잠금·돌파 기준 변경 및 유료 확장 금지.
- 자원: 연료·행동력·보호재고 하한/구매횟수 상한 유지. 금화 구매 가능과 보석 구매를 별도 판정.
- 대형작전: 지도 경계·좌표순환·EMP·결과 화면 경합·월말·복구. 정상 경로 통과가 모든 예외 통과는 아님.
- 섬: 이름/재료/OCR 검증, 기존 메뉴/보존수량, 구매·교환, 생산 시작/완료/수령, 시즌 목표 반영을 각각 판정.
- 운영: 로그인, 예약, 일시정지/재개, 설정 복원, 통신 끊김, 알 수 없는 화면 안전 중단.

## 실행 순서

1. 원본 작업 정의/GUI/실행 진입점 불일치와 목록 누락 회귀 검사.
2. 증거 없는 세부 옵션은 통과로 추정하지 않고 원시 로그를 로컬 대조.
3. 현 계정·기존 보호 범위에서 가능한 미검증 항목을 제한된 1회 실기로 확인.
4. 실패하면 반복 방치하지 않고 중지→원인 재현→수정→오프라인 회귀→같은 분기 실기.
5. 승인/기간/대상 조건이 없는 항목은 정확한 조건을 명시. 전체 완료로 표시하지 않음.
