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

## 쓸 때 주의할 점

- **검색 결과만** 표시된 가격은 업체 광고나 기사 요약입니다. 견적서를 받으면 실제 값으로 바꾸세요.
- 건물 유형별 합계의 호실 수, 전력 용량, 정화조 처리대상인원은 가정입니다. 실제 건축물대장으로 다시 확인해야 합니다.
- 시장 집계(`market/`)는 서울 열린데이터광장 건축물대장 2026-11-09 갱신분을 전부 내려받아 직접 센 값입니다. 서울 합계 행('서울합계')이 마지막 줄에 있으니 구별 합을 낼 때 빼세요.
  '일반/집합' 구분은 대장 기준이고, 승강기 수는 대장 기재 또는 승강기안전공단 자료의 도로명주소 매칭입니다.
- DART의 '컨텍터스'(전자기 측정기기 제조사)는 둥지 운영사와 이름만 같은 다른 회사라 넣지 않았습니다. 둥지·자리톡·빌딩케어 운영사는 DART에 공시하지 않습니다.
