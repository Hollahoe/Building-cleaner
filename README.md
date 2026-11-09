# 빌딩모아관리 (Building-cleaner)

**소규모 건물주를 위한 공동구매형 건물관리. 1단계는 직접 뛰는 콘시어지형으로 운영합니다.**

소규모 건물주 혼자 계약하면 비싼 청소·승강기·소방·보험·세무를 여러 건물 묶음으로 협상하고,
운영자가 건물주의 "총무" 역할을 맡아 업체 관리와 서류를 대신 정리합니다.

> 이 레포에는 두 가지가 들어 있습니다.
> 1. **웹 창구(`app/`)**: 건물주가 우리 동네 공동구매를 신청하고(동네·항목별 수요 게시판), 무료 진단을 신청하고, 열린 공동구매에 참여하는 사이트. 업체는 협력 업체로 등록합니다. 운영자용 관리자 화면 포함. 결제·업체 입찰은 아직 없습니다([플랫폼 전략](docs/platform.md)).
> 2. **운영 키트**: 카톡·엑셀·노션으로 건물을 직접 관리할 때 쓰는 문서, 템플릿, 계산기.
>
> 직접 뛰면서 같은 일이 반복되는 게 확인되면, 그 업무만 다음 단계에서 자동화합니다.

---

## 바로 시작하기

1. [`docs/30-day-plan.md`](docs/30-day-plan.md): 오늘부터 할 일 체크리스트. 항목마다 쓸 템플릿이 연결돼 있습니다.
2. [`ops/kakao-templates.md`](ops/kakao-templates.md): 멘토님께 보낼 메시지와 인터뷰 섭외 문구.
3. [`interview/guide.md`](interview/guide.md): 건물주 인터뷰 질문 5개와 진행 방법.
4. [`docs/legal-checklist.md`](docs/legal-checklist.md): **돈 받기 전에 꼭 읽기.** 보험·세무·법률 알선 수수료는 법적으로 막혀 있을 수 있습니다.
5. [`docs/strategy.md`](docs/strategy.md)와 [`docs/investment.md`](docs/investment.md): 포지셔닝, 쐐기, 밀도 전략, 중단 기준, 그리고 VC 투자를 받을 수 있는지에 대한 판단.
6. [`docs/platform.md`](docs/platform.md): 웹 창구를 어디까지 만들었고 언제 무엇을 더 만들지, 출시 체크리스트.
7. [`docs/deploy-guide.md`](docs/deploy-guide.md): **도메인 · GitHub · Supabase · Vercel로 사이트를 공개하는 방법**(단계별).
8. [`docs/strategy-report.md`](docs/strategy-report.md): **전략 보고서 요약 v2**(원문 조사로 바뀐 결론, 권고 사업 모델, 60개월 재무와 300억 경로). 재무 모델 [`tools/financial-model-60m-v2.xlsx`](tools/financial-model-60m-v2.xlsx), 원자료 [`research/`](research/README.md).
9. [`docs/execution-plan.md`](docs/execution-plan.md): **36개월 실행계획 요약**(조사로 바뀐 결론, 재무 모델 결과, 게이트). 재무 모델은 [`tools/financial-model-36m.xlsx`](tools/financial-model-36m.xlsx).
10. [`docs/benchmark.md`](docs/benchmark.md): **경쟁사 17곳 벤치마킹, 차별화, 단계별 로드맵, 300억까지의 숫자**. 액션 아이템 200개는 [`ops/action-items.csv`](ops/action-items.csv).

## 웹 창구 실행하기

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
ADMIN_PASSWORD=원하는비밀번호 uvicorn app.asgi:app --reload --port 8000
```

- 브라우저에서 `http://localhost:8000` (건물주 화면), `http://localhost:8000/admin` (관리자, 아이디 `admin`)
- 화면 확인용 예시 공동구매 넣기: `python -m app.seed --demo` (제목에 [예시]가 붙고 금액은 가상입니다. 실제 운영 DB에는 쓰지 마세요)
- 테스트: `python -m pytest` (Postgres로도 돌리려면 `TEST_DATABASE_URL=postgresql://… python -m pytest`)
- 설정(브랜드 이름, 지역, 연락처, 카톡 링크, 비밀번호 등)은 환경 변수로 바꿉니다. 목록과 설명은 [`.env.example`](.env.example)에 있습니다.
- 저장소: `DATABASE_URL`(Supabase Postgres)이 있으면 Postgres, 없으면 SQLite 파일(`DATABASE_PATH`)을 씁니다. 표는 처음 켜질 때 자동으로 만들어집니다.
- 배포: [배포 가이드](docs/deploy-guide.md) (Vercel + Supabase). Docker + 디스크로도 올릴 수 있습니다(`Dockerfile`).

| 경로 | 화면 |
|---|---|
| `/` | 첫 화면: 소개, 모집 중인 공동구매, **모이고 있는 공동구매(동네·항목별 신청 수)**, 진행 방식, 비용, 하지 않는 일, 협력 업체 안내, 자주 묻는 질문 |
| `/demand` | 우리 동네 공동구매 신청 (같은 번호·같은 동네는 합쳐져 숫자가 부풀지 않음) |
| `/partners` | 협력 업체 등록 |
| `/diagnosis` | 무료 운영비 진단 신청 |
| `/rounds`, `/rounds/<주소>` | 공동구매 목록과 상세(모인 건물 수, 묶음 단가 구간, 참여 신청) |
| `/privacy`, `/terms` | 개인정보처리방침, 이용 안내 |
| `/admin` | 관리자: 수요 게시판(기준 도달 시 '이 수요로 공동구매 열기'), 공동구매 신청·협력 업체·진단 신청 관리, 공동구매 만들기·수정, 참여자 관리, CSV 내보내기 |

## 레포 구조

| 폴더 | 내용 | 쓰는 시점 |
|---|---|---|
| `app/`, `tests/` | 웹 창구(FastAPI + Supabase Postgres 또는 SQLite)와 테스트 | 지금부터 |
| `docs/` | [전략](docs/strategy.md), [플랫폼 전략](docs/platform.md), [배포 가이드](docs/deploy-guide.md), [투자 가능성·자금 조달](docs/investment.md), [벤치마킹과 청사진](docs/benchmark.md), [36개월 실행계획](docs/execution-plan.md), [30일 플랜](docs/30-day-plan.md), [법률 체크리스트](docs/legal-checklist.md) | 처음, 그리고 단계 바꿀 때 |
| `interview/` | [인터뷰 가이드](interview/guide.md), [기록지](interview/note-template.md), [고통 TOP 3 뽑는 법](interview/synthesis.md), [후보 리스트 CSV](interview/candidates.csv) | Week 1–2 |
| `service/` | [서비스 범위](service/scope.md), [가격 모델](service/pricing.md), [1장 계약서 초안](service/contract-draft.md) | Week 3–4 |
| `sourcing/` | [업체 견적 요청서](sourcing/rfq-template.md), [업체 DB CSV](sourcing/vendors.csv) | Week 3–4 |
| `pilot/` | [건물 건강진단 리포트](pilot/building-health-report-template.md), [케이스 스터디](pilot/case-study-template.md) | Month 2–3 |
| `ops/` | [건물 대장 CSV](ops/buildings.csv), [민원·이슈 로그 CSV](ops/issue-log.csv), [액션 아이템 200개 CSV](ops/action-items.csv), [법정 점검 캘린더](ops/compliance-calendar.md), [카톡 문구](ops/kakao-templates.md), [월간 보고서](ops/monthly-report-template.md) | 파일럿부터 매일 |
| `research/` | [원자료](research/README.md): 항목별 가격(조례·고시·시장 사례), 경쟁사 DART 재무 요약 | 숫자를 확인할 때 |
| `tools/` | [`savings-calculator.xlsx`](tools/savings-calculator.xlsx): 고통 집계, 견적 비교, 절감액·수수료 계산, 24개월 사업계획과 VC 규모 역산. [`financial-model-36m.xlsx`](tools/financial-model-36m.xlsx): 36개월 월별 재무 모델 v1. [`financial-model-60m-v2.xlsx`](tools/financial-model-60m-v2.xlsx): 권고안 60개월 모델과 기업가치 | Week 2부터 |

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

1. **코드를 새로 작성.** 웹 창구(`app/`)는 이 레포에서 처음부터 새로 쓴 코드입니다. 청진기 코드를 복사하거나 import하거나 fork한 부분이 없습니다.
2. **공유하는 것 없음.** 라이브러리, DB, API 키, 배포 설정, 패키지 이름을 함께 쓰지 않습니다.
3. **안전마진 계산은 다시 만들지 않음.** 건물 건강진단 리포트에 안전마진이 필요하면 청진기에서 나온 **결과값만 사람이 옮겨 적는 칸**을 씁니다.
   이 레포는 그 값을 계산하지 않습니다.
4. **2단계에서 연결할 때도 데이터만 주고받음.** "청진기 출력(리포트·CSV) → 이 레포의 입력"처럼 한 방향 데이터 경계로만 연결하고,
   코드나 모듈은 함께 쓰지 않습니다.

## 고지

이 레포의 계약서·법률 메모는 법률 자문이 아닙니다. 돈을 받고 서비스를 시작하기 전에 변호사·세무사에게
계약서와 수익 구조(특히 수수료 구조)를 검토받으세요. 자세한 내용은 [`docs/legal-checklist.md`](docs/legal-checklist.md)에 있습니다.
