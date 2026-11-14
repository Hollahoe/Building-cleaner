# 원자료 (전략 보고서 근거)

전략 보고서(Claude 문서 "빌딩모아관리 36개월 실행계획"의 '전략 보고서'·'근거 자료' 탭)에 쓴 숫자의 원자료입니다.
각 행의 `verification` 또는 비고 열에 **원문 확인**(법령·조례·고시·DART 공시 원문을 직접 받아 읽음)과
**검색 결과만**(원문 사이트가 막혀 검색 결과로만 확인)을 구분해 두었습니다. 기준일은 2026-11-09입니다.

| 파일 | 내용 |
|---|---|
| `pricing/01_elevator_maintenance.csv` | 승강기 유지관리 월 계약가: 표준유지관리비(2024–2026), 공동주택 평균 계약가, 민간 계약 평균, 실제 사례 |
| `pricing/02_elevator_inspection_fee.csv` | 승강기 검사수수료(행정안전부고시 제2025-35호 별표4, 원문 확인) |
| `pricing/03_fire_inspection.csv` | 소방시설 자체점검 비용: 산정기준 고시, 표준자체점검비, 시장 사례 |
| `pricing/04_septic_fee_by_gu.csv` | 서울 11개 구 정화조 청소 수수료 조례(원문 확인) |
| `pricing/04b_septic_fee_by_capacity.csv` | 건물 유형별 정화조 용량과 구별 연간·월 수수료 계산 |
| `pricing/05_electrical_agency_fee.csv` | 전기안전관리 대행 수수료, 일반용·자가용 구분(전기사업법 시행규칙 제3조) |
| `pricing/06_stairs_cleaning.csv` | 계단·복도 청소 월 정기 단가 |
| `pricing/07_pest_watertank.csv` | 방역·소독, 저수조 청소 단가와 법정 의무 여부 |
| `pricing/08_persona_totals.csv` | 근생·다가구·상가주택 유형별 월 시설비 합계(저/중/고) |
| `competitors/dart_financials_summary.csv` | 숨고(브레이브모바일)·알스퀘어·패스트파이브·두꺼비세상(아파트너)·에스원의 DART 감사보고서·사업보고서 재무 요약 |
| `market/target_seoul_by_gu.csv` | 서울 25개 구별 대상 건물(지상 4–7층, 연면적 300–3,000㎡) 수: 근생 1종·2종, 다가구, 다세대, 업무시설, 승강기·오수정화시설 보유 수. 건축물대장 표제부 583,650건·층별개요 3,034,424건 전수 집계 |
| `market/target_mapo_building_list.csv` | 마포구 대상 건물 6,382동 목록(주소, 법정동, 용도, 층수, 연면적, 일반/집합, 승강기 수, 사용승인일). 소유자 정보는 없습니다 |
| `market/target_mapo_by_beopjeongdong.csv`, `target_mapo_by_haengjeongdong_cluster.csv` | 마포구 법정동·행정동 묶음별 대상 건물 수 |
| `market/target_seoul_crosstab_use_floors_area.csv`, `seoul_sensitivity_use_floorband_areaband.csv` | 용도×층수×연면적 교차표와 층수·면적 기준을 바꿨을 때의 대상 수 |
| `market/target_classification_method_by_gu.csv` | 대상 분류 근거 감사표 |
| `market/seoul_buildings_by_gu_mainuse_register.csv`, `septic_seoul_by_gu_register.csv` | 서울 구별·주용도별 전체 건물 수, 오수정화시설 집계 |
| `market/official_*.csv` | 국토교통부 2025년 건축물현황과 e-나라지표 1226(용도·면적·층수별) |
| `market/elev_*.csv` | 한국승강기안전공단 승강기 보유·설치 현황(2025-12-31, 2026-06-30) 서울·마포 집계 |
| `market/mapo_haengjeongdong_16_official.csv` | 마포구 16개 행정동·26개 법정동 일람표(구청) |
| `market/sources_index.csv` | 위 파일마다 원자료 이름, URL, 기준일, 확인 수준 |
| `competitors/landscape_2026-11.csv` | 경쟁사 28곳: 대상, 서비스, 가격, 계약 방식, 규모, 투자·매출, 하지 않는 것, 법정 점검 기능, 출처, 확인 수준(대부분 검색 결과만) |
| `competitors/fee_benchmarks_2026-11.csv` | 돈이 도는 곳별 가격 기준점 51개: 꼬마빌딩 PM 수수료, 임대관리·관리비 앱 요금, 소형 건물 종합관리 시세, 승강기 교체·방수·외벽 공사비, 상가임대차법 시행령 제8조 |
| `public-data/datasets.csv` | 건물별 법정 의무를 만들 수 있는 공공데이터 34건: 제공 기관, 항목, 갱신 주기, 이용 허락 범위, 인증키 필요 여부 |
| `public-data/mapo_*.csv`, `seoul_elevator_vendor_share.csv` | 승강기안전공단 승강기 설치 현황(2026-06-30)과 2026년 상반기 검사 결과 집계: 유지관리업체 점유율, 검사 유효기간 만료 월, 조건부합격 수, 업체별 조건부합격률 |
| `public-data/mapo_target_elevator_status.csv` | 마포 '일반' 근생 대상 건물에 승강기 자료를 주소로 붙인 결과(조건부합격·만료 임박·15년/25년 이상 건물 수) |
| `official-stats/rent_survey_opex.csv` | 한국부동산원 상업용부동산 임대동향조사(KOSIS): 중대형·소규모 상가와 오피스의 임대료, 공실률, 순영업소득, 운영경비 비중, 그리고 거기서 계산한 ㎡당 운영경비와 600㎡ 기준 금액. 서울 상권별(홍대·합정, 공덕역, 망원역 등) |
| `official-stats/industry_economics.csv` | 통계청 서비스업조사 2023·2024(KOSIS DT_3KB9001·9002): 부동산 관리업, 사업시설 유지관리, 청소업의 사업체 수, 종사자, 매출, 영업이익률, 1인당 매출. 전국·서울, 종사자 규모별 |
| `official-stats/realestate_service_survey.csv` | 국토교통부 부동산서비스산업 실태조사 2024: 부동산 관리업 사업체 수, 매출, 영업이익, 경영 애로 |
| `official-stats/owner_demographics.csv` | 건물주 연령: 국세통계 2024·2025(부동산임대업 사업자 연령·성별), 전국사업체조사 2024(임대업·관리업 대표자 연령) |
| `public-contracts/public_contract_prices.csv`, `public_contract_summary.csv` | 지자체 계약 대장에서 뽑은 승강기 유지관리, 소방안전관리 업무대행, 전기안전관리 대행, 청소, 저수조 청소 실계약 589건과 용역별 중앙값. 업체명은 법인만 남겼습니다 |
| `competitors/headcount_nps.csv`, `headcount_nps_pivot.csv` | 국민연금 가입 사업장 내역(2024-09, 2025-09, 2026-09)에서 뽑은 경쟁사 운영 법인의 가입자 수 |
| `competitors/deals_dart.csv`, `fm_margins_dart.csv` | 국내 관리업체 거래(AJ대원, 자이에스앤디 주택관리 부문, 에스앤아이)의 가격·매출·이익 배수와 관리업체 이익률. DART 공시 기준 |

## 쓸 때 주의할 점

- **검색 결과만** 표시된 가격은 업체 광고나 기사 요약입니다. 견적서를 받으면 실제 값으로 바꾸세요.
- 건물 유형별 합계의 호실 수, 전력 용량, 정화조 처리대상인원은 가정입니다. 실제 건축물대장으로 다시 확인해야 합니다.
- 시장 집계(`market/`)는 서울 열린데이터광장 건축물대장 2026-11-09 갱신분을 전부 내려받아 직접 센 값입니다. 서울 합계 행('서울합계')이 마지막 줄에 있으니 구별 합을 낼 때 빼세요.
  '일반/집합' 구분은 대장 기준이고, 승강기 수는 대장 기재 또는 승강기안전공단 자료의 도로명주소 매칭입니다.
- 승강기 자료는 1년에 한 번 갱신되는 2026-06-30 기준입니다. 원자료에는 건물명이 있지만 사람 이름일 수 있어 집계만 넣었습니다.
  업체별 조건부합격률은 건물 연식 차이가 섞여 있어 업체 품질 순위로 공개하면 안 됩니다.
- 공공데이터는 이용 제한이 없지만, 문자·이메일 광고는 받는 사람의 사전 동의가 필요합니다(정보통신망법 제50조). 영업은 건물 주소로 보내는 우편과 방문으로 합니다.
- 임대동향조사의 운영경비 금액은 공표값(순영업소득, 비중)으로 계산한 값입니다. ㎡ 기준이 연면적인지 임대면적인지, 운영경비에 무엇이 들어가는지는 확인하지 못했습니다.
- 공공 계약 단가는 민간 근생보다 높습니다(승강기는 표준유지관리비 수준, 청소는 상주 인력). 상한 기준점으로만 쓰세요. 서울 표본은 마포 합정동주민센터 1건뿐입니다.
- 국민연금 자료에는 가입자 3명 이상 법인만 나옵니다. 가입자 수는 직원 수의 근사값입니다.
- DART의 '컨텍터스'(전자기 측정기기 제조사)는 둥지 운영사와 이름만 같은 다른 회사라 넣지 않았습니다. 둥지·자리톡·빌딩케어 운영사는 DART에 공시하지 않습니다.
