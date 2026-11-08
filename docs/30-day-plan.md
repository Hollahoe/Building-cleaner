# 실행 플랜: 30일 + 파일럿 60일

> 체크리스트는 노션으로 가져오면 할 일 블록이 됩니다. 항목 옆 링크가 그 일을 할 때 쓰는 템플릿입니다.

## Day 0: 오늘 할 일

- [ ] 멘토님께 후속 메시지 보내기: 소규모 건물주 2–3분 인터뷰 연결 요청 → [카톡 문구 1번](../ops/kakao-templates.md#1-멘토님께-후속-메시지)
- [ ] 회사 취업규칙·근로계약서에서 **겸업 금지 조항** 확인 → [법률 체크리스트 0번](legal-checklist.md#0-돈-받기-전에)
- [ ] 노션 워크스페이스 만들고 이 레포 가져오기 → [README](../README.md#노션으로-옮기기)

## Week 1–2: 인터뷰 (말만 듣기)

- [ ] 소규모 건물주 후보 10명 리스트 만들기 → [`interview/candidates.csv`](../interview/candidates.csv)
  - 경로: 멘토님, 지인, 부모님 지인, 부동산 카페, 상가 번영회
- [ ] 섭외 메시지 보내기 → [카톡 문구 2–3번](../ops/kakao-templates.md#2-인터뷰-섭외-지인-소개)
- [ ] 인터뷰 질문 5개를 고정하고 진행하기 → [`interview/guide.md`](../interview/guide.md)
  1. 관리하면서 제일 돈 아깝다고 느낀 게 뭐예요?
  2. 제일 머리 아픈 민원이 뭐예요?
  3. 지금 관리비가 월 얼마예요? 어디에 제일 많이 나가요?
  4. 청소, 승강기, 소방, 보험, 세무 중에 직접 알아보시는 게 있어요?
  5. 관리업체를 바꿀 생각이 있으세요? 왜요?
- [ ] 인터뷰 1건마다 기록지 쓰기(당일 안에) → [`interview/note-template.md`](../interview/note-template.md)
- [ ] 10명이 끝나면 고통 TOP 3 뽑기 → [`interview/synthesis.md`](../interview/synthesis.md), 엑셀 `고통집계` 시트
  - `[가설]` 조언의 예상: 1위 청소, 2위 승강기·소방 유지보수, 3위 공실·임대관리. **결과를 이 예상에 맞춰 해석하지 말 것.**
- [ ] 인터뷰한 분들께 "정리해서 리포트 보내드릴게요" 약속하고 카톡 유지 → [카톡 문구 4번](../ops/kakao-templates.md#4-인터뷰-직후-감사-인사)

## Week 3–4: 서비스 정의, 가격 정하기

- [ ] **[법률 체크리스트](legal-checklist.md) 전체 읽기.** 수수료 구조를 정하기 전에 반드시 확인
- [ ] 공동구매 항목 5개 확정 → [`service/scope.md`](../service/scope.md)
  - 조언의 후보: 청소 용역, 승강기 유지보수, 소방 점검, 건물 종합보험, 세무·법률 자문
  - 보험과 세무·법률은 "현황 정리만 하고 수수료 0원"으로 운영하는 안을 권장(이유는 scope.md 참고)
- [ ] 항목별로 업체 2곳씩 견적 받기: "건물 1채 / 3채 / 5채 / 10채 묶으면 얼마까지 되나요?" → [`sourcing/rfq-template.md`](../sourcing/rfq-template.md), [`sourcing/vendors.csv`](../sourcing/vendors.csv)
  - 업체의 등록·신고 여부 확인(승강기 유지관리업 등록, 건물위생관리업 신고 등)
- [ ] 받은 견적을 엑셀 `견적비교` 시트에 입력 → [`tools/savings-calculator.xlsx`](../tools/savings-calculator.xlsx)
- [ ] 가격 모델 정하기 → [`service/pricing.md`](../service/pricing.md)
  - A) 월 구독 19.9만–29.9만 원 + 공동구매 수수료 `[가설]`
  - B) 관리비 절감분의 30% 수수료 `[가설]`, "절감 못 하면 돈 안 받겠습니다"
  - 처음에는 B가 설득하기 쉬움
- [ ] 1장짜리 계약서 만들기(해주는 것, 안 해주는 것, 책임 범위) → [`service/contract-draft.md`](../service/contract-draft.md)
- [ ] 계약서와 수수료 구조를 변호사에게 1회 검토받기

## Month 2: 파일럿 3개 건물

- [ ] 파일럿 건물 3개 잡기: 30–100평 꼬마빌딩, 상가주택, 원룸 건물. 큰 건물은 제외 → [`ops/buildings.csv`](../ops/buildings.csv)
- [ ] 건물마다 법정 점검 대상 여부와 다음 일정 정리 → [`ops/compliance-calendar.md`](../ops/compliance-calendar.md)
- [ ] 건물마다 건강진단 리포트 1장 만들어 드리기(관리비 구조, 법정 점검 현황, 리스크 3개) → [`pilot/building-health-report-template.md`](../pilot/building-health-report-template.md)
  - 이 리포트가 영업 자료가 됩니다. 안전마진 칸은 청진기 결과값을 옮겨 적기만 하고, 이 레포에서는 계산하지 않음
- [ ] 공동구매 1건이라도 실제로 성사시키기(예: 청소 업체 변경). 바꾸기 전과 후 고지서를 확보
- [ ] 민원·업체 연락은 전부 이슈 로그에 기록 → [`ops/issue-log.csv`](../ops/issue-log.csv)
- [ ] 매달 건물주께 월간 보고 보내기 → [`ops/monthly-report-template.md`](../ops/monthly-report-template.md)

## Month 3: 케이스 만들기, 정리

- [ ] 파일럿 3건을 케이스 스터디로 정리: 바꾸기 전·후 관리비, 민원 건수, 절감액 → [`pilot/case-study-template.md`](../pilot/case-study-template.md)
- [ ] 멘토님과 2차 미팅: "직접 뛰어보니 이렇게 나왔습니다. 이제 이 부분을 반자동으로 만들려고 합니다" → [카톡 문구 8번](../ops/kakao-templates.md#8-멘토님-2차-미팅-요청)
- [ ] [단계 전환 기준](strategy.md#단계-전환-기준)으로 2단계 진입 여부 판단
- [ ] 본업 점검: 저녁과 주말 시간을 확보할 수 있는지 판단하고, 안 되면 연봉은 유지하면서 정시 퇴근이 가능한 곳으로 이직 준비
