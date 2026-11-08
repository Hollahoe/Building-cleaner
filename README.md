# Building-cleaner

**소규모 건물주를 위한 공동구매형 건물관리. 1단계는 직접 뛰는 콘시어지형으로 운영합니다.**

소규모 건물주 혼자 계약하면 비싼 청소·승강기·소방·보험·세무를 여러 건물 묶음으로 협상하고,
운영자가 건물주의 "총무" 역할을 맡아 업체 관리와 서류를 대신 정리합니다.

> 이 레포에는 **앱도 플랫폼도 없습니다.** 카톡·엑셀·노션만으로 건물 3개를 직접 관리하는 데 필요한
> 문서, 템플릿, 계산기만 들어 있습니다. 직접 뛰면서 같은 일이 반복되는 게 확인되면, 그 업무만 2단계에서 자동화합니다.

---

## 바로 시작하기

1. [`docs/30-day-plan.md`](docs/30-day-plan.md): 오늘부터 할 일 체크리스트. 항목마다 쓸 템플릿이 연결돼 있습니다.
2. [`ops/kakao-templates.md`](ops/kakao-templates.md): 멘토님께 보낼 메시지와 인터뷰 섭외 문구.
3. [`interview/guide.md`](interview/guide.md): 건물주 인터뷰 질문 5개와 진행 방법.
4. [`docs/legal-checklist.md`](docs/legal-checklist.md): **돈 받기 전에 꼭 읽기.** 보험·세무·법률 알선 수수료는 법적으로 막혀 있을 수 있습니다.
5. [`docs/strategy.md`](docs/strategy.md)와 [`docs/investment.md`](docs/investment.md): 포지셔닝, 쐐기, 밀도 전략, 중단 기준, 그리고 VC 투자를 받을 수 있는지에 대한 판단.

## 레포 구조

| 폴더 | 내용 | 쓰는 시점 |
|---|---|---|
| `docs/` | [전략](docs/strategy.md), [투자 가능성·자금 조달](docs/investment.md), [30일 플랜](docs/30-day-plan.md), [법률 체크리스트](docs/legal-checklist.md) | 처음, 그리고 단계 바꿀 때 |
| `interview/` | [인터뷰 가이드](interview/guide.md), [기록지](interview/note-template.md), [고통 TOP 3 뽑는 법](interview/synthesis.md), [후보 리스트 CSV](interview/candidates.csv) | Week 1–2 |
| `service/` | [서비스 범위](service/scope.md), [가격 모델](service/pricing.md), [1장 계약서 초안](service/contract-draft.md) | Week 3–4 |
| `sourcing/` | [업체 견적 요청서](sourcing/rfq-template.md), [업체 DB CSV](sourcing/vendors.csv) | Week 3–4 |
| `pilot/` | [건물 건강진단 리포트](pilot/building-health-report-template.md), [케이스 스터디](pilot/case-study-template.md) | Month 2–3 |
| `ops/` | [건물 대장 CSV](ops/buildings.csv), [민원·이슈 로그 CSV](ops/issue-log.csv), [법정 점검 캘린더](ops/compliance-calendar.md), [카톡 문구](ops/kakao-templates.md), [월간 보고서](ops/monthly-report-template.md) | 파일럿부터 매일 |
| `tools/` | [`savings-calculator.xlsx`](tools/savings-calculator.xlsx): 고통 집계, 견적 비교, 절감액·수수료 계산, 24개월 사업계획과 VC 규모 역산 | Week 2부터 |

## 노션으로 옮기기

노션에서 **가져오기(Import) → Markdown & CSV**를 고르고 이 레포 파일을 올리면 됩니다.

- `.md` 파일은 페이지로 들어갑니다. 체크리스트(`- [ ]`)는 노션 할 일 블록이 됩니다.
- `.csv` 파일은 데이터베이스로 들어갑니다. 첫 줄의 `예시` 행은 형식을 보여주려고 넣은 가짜 데이터라서, 가져온 뒤 지우면 됩니다.
- CSV를 엑셀에서 바로 열면 한글이 깨질 수 있습니다. 엑셀에서는 **데이터 → 텍스트/CSV에서 가져오기 → UTF-8**로 여세요.

## 표기 규칙

- **`[가설]`**: 조언에서 나왔거나 예시로 넣은 숫자입니다. 아직 검증되지 않았습니다(예: "월 200만 원 → 130만 원", "고통 1위는 청소").
  인터뷰나 실제 견적으로 확인한 뒤 실제 값으로 바꾸세요.
- **`[확인 필요]`**: 법령이나 행정 기준처럼 관할 기관이나 전문가에게 최종 확인해야 하는 항목입니다.

## 청진기와의 분리 원칙

이 사업은 기존 청약 진단·안전마진 앱(청진기)과 **코드가 전혀 겹치지 않도록** 따로 운영합니다.

1. **실행 코드 없음.** 이 레포에는 문서, CSV, 엑셀만 있습니다. 청진기 코드를 복사하거나 import하거나 fork한 부분이 없습니다.
2. **공유하는 것 없음.** 라이브러리, DB, API 키, 배포 설정, 패키지 이름을 함께 쓰지 않습니다.
3. **안전마진 계산은 다시 만들지 않음.** 건물 건강진단 리포트에 안전마진이 필요하면 청진기에서 나온 **결과값만 사람이 옮겨 적는 칸**을 씁니다.
   이 레포는 그 값을 계산하지 않습니다.
4. **2단계에서 연결할 때도 데이터만 주고받음.** "청진기 출력(리포트·CSV) → 이 레포의 입력"처럼 한 방향 데이터 경계로만 연결하고,
   코드나 모듈은 함께 쓰지 않습니다.

## 고지

이 레포의 계약서·법률 메모는 법률 자문이 아닙니다. 돈을 받고 서비스를 시작하기 전에 변호사·세무사에게
계약서와 수익 구조(특히 수수료 구조)를 검토받으세요. 자세한 내용은 [`docs/legal-checklist.md`](docs/legal-checklist.md)에 있습니다.
