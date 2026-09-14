# 한국 서버 섬 생산물 인식

현재 지원 범위는 관찰한 농지 생산물 이름/보유량 및 읽기 전용 진단입니다.
신규 생산과 재료 구매를 활성화한 완성 기능이 아닙니다. 주문/시즌 임무에도
이 인식기를 연결한 것으로 간주하지 마십시오.

## 인식 방식

- `assets/kr/island_item_name/<item_id>[_variant].png`는 실제 한국어 이름 영역입니다.
- 스크롤에 따라 달라지는 반투명 배경을 제외하고 글자 주변만 비교합니다.
- 서로 다른 품목의 점수가 비슷하면 템플릿 결과를 채택하지 않습니다.
- 템플릿에 없는 글자는 로컬 Windows 한국어 OCR로 시도합니다. 빈 문자열이나
  모호한 결과를 임의의 최근접 품목으로 바꾸지 않고 신규 생산 전에 중단합니다.
- 한 글자 이름은 Windows OCR만으로 불안정할 수 있습니다. 실제 스크롤 위치별
  화면을 회귀 검사에 추가하여 검증해야 합니다.

## 선택적 의존성

이 저장소의 Windows Python 3.7 런타임에서:

```powershell
.\toolkit\python.exe -m pip install -r requirements-kr-windows.txt
```

Windows에 한국어 OCR 언어 모델이 설치되어 있어야 합니다. 실행 정책이나 보안
설정을 바꿀 필요가 없습니다. 다른 Python 버전/Linux 지원을 검증한 것은 아닙니다.
모델을 사용할 수 없으면 설치 문제를 해결하기 전 이 기능을 활성화하지 마십시오.

OCR에는 ALAS가 이미 확보한 게임 프레임의 잘린 영역만 전달합니다. 별도 화면
캡처나 외부 OCR 서버 전송은 없습니다. 임시 PNG는 OCR 호출 후 정리합니다.

## 회귀 검사

```powershell
.\toolkit\python.exe -m unittest dev_tools.test_kr_island_recipe_ocr dev_tools.test_kr_windows_ocr dev_tools.test_kr_island_production_names
```

회귀 검사에는 저장된 게임 화면과 모의 객체만 사용하며 장치 연결·게임 입력을
실행하지 않습니다. 실제 `Alas.exe` 검증 결과는 날짜별 검증 기록을 참조하십시오.
