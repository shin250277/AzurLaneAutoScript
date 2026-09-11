# 한국 서버 유지보수 기준

## 2026-09-12 통합

- 원본: `LmeSzinc/AzurLaneAutoScript`, master `46fe341db463aa82a3ee4dbdd3899042561dd7ec` (2026-09-11).
- 통합 전 한국 서버: `2b73346f5`; 공통 조상: `81ccf63b4540f00241628c82a58c02c7a2bb11af`.
- 원본에만 있던 150개 커밋 통합. 한국 서버의 기존 262개 커밋은 삭제하거나 재작성하지 않음.
- 원본 변경에는 8월/9월 이벤트, 일반/하드 출격 화면 구분, 지도 스위치, S8 연구 데이터, 이벤트 상점 등이 포함됨.
- 충돌 13개 파일 해결. 생성 파일은 원본 도구로 재생성하고 수동 한국 서버 보정은 `dev_tools/kr_asset_overrides.json`으로 이관(158개 정의).
- 색상 판정 API 변경에 맞춰 한국 서버가 추가한 옛 유사도 임계값 25개를 `255 - old` 거리값으로 변환. 실제 픽셀 판정 동등성 회귀 검사 추가.
- 한국어 작전문서 제목은 설정 생성 원본에 반영하여 재생성 때 번역이 사라지지 않게 함.
- 원본의 일반 CV 보호 로직은 최신 Enhancement 구현을 사용하고 한국 서버 퇴역 확인/UR 보호는 유지.
- 기존 안전 검사에서 확인하는 창고 정리 버튼 위치, AP 사용 확인, 실패한 요새 작업 중단을 보존.

## 확인 결과와 한계

- `toolkit/python.exe -W ignore::DeprecationWarning -m unittest discover -s dev_tools -p test_*.py`: 251개 통과.
- 한국 서버 설정으로 `import alas` 성공. 장치 생성/게임 입력 없이 실행.
- 원본 이벤트 데이터 포함은 한국 서버의 해당 이벤트 개방 또는 실기 성공을 의미하지 않음. KR 일정은 실제 게임/공식 공지와 대조해야 함.
- 새 EventShop은 기본 Enable=false. 기존 실제 계정 설정과 재화 제한은 수정하지 않았음. config/template*.json은 기본 템플릿이며 실제 alas.json과 다름.
- 실기 검증을 재개하거나 자동화를 켜지 않았음. 기존 수정의 조건부 실기 확인 과제는 그대로 남음.

## 다음 업데이트 절차

1. 원본 master를 fetch하고 마지막 통합 커밋 이후만 비교한다. 전체 기능 목록 검증을 처음부터 반복하지 않는다.
2. 기존 한국 서버 코드가 있는 짧은 통합 브랜치에서 원본을 merge한다. 계정 설정, 로그, 스크린샷 전체를 커밋하지 않는다.
3. 공통 코드는 원본 구현을 우선 사용한다. KR 이미지/번역/패키지/실제 동작 차이만 별도로 유지한다.
4. 이미지 추가 후 `toolkit/python.exe -m dev_tools.button_extract`, 설정 원본 변경 후 `toolkit/python.exe -m module.config.config_updater`를 실행한다. 자동 생성된 assets.py를 직접 수정하지 않는다.
5. 저장 화면 인식 및 오프라인 회귀 검사를 먼저 실행한다. 실기는 변경된 경로와 구매/퇴역 등 위험 경계에 한정한다.
6. 개방/재화 조건 부족은 해당 기능의 제한으로 기록한다. 나머지 사용 가능한 기능의 완료 판정을 무기한 보류하지 않는다.

`migrate_kr_asset_overrides.py`, `migrate_kr_color_thresholds.py`, `resolve_kr_upstream_generated.py`는 이번 통합의 일회성 이관 도구다. 일반 업데이트마다 재실행하지 않는다.
