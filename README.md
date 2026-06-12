# 재난 대응 통합 의사결정 시스템
> **가천대학교 알고리즘 기말 프로젝트** | Team GachonAlgorithm10

재난(화재·침수) 발생부터 복구까지, 상황실 운영자의 의사결정을 알고리즘으로 지원하는 관제 대시보드 프로토타입입니다.

| 항목 | 내용 |
|------|------|
| 대상 지역 | 서울특별시 송파구 |
| 실행 환경 | Python 3.10+, Streamlit |
| 제출 기한 | 2026년 6월 19일 (금) 자정 |
| GitHub Org | [GachonAlgorithm10](https://github.com/GachonAlgorithm10) |

---

## 팀원 및 역할

| 이름 | 역할 | 담당 모듈 | 알고리즘 | 자료구조 |
|------|------|-----------|----------|----------|
| 임성엽 (팀장) | 기획·백엔드 통합 | **M3** 부상자 이송 우선순위<br>**M4** 구조자원 배치<br>**M6** 구호물자 수요 산정<br>**M7** 복구 예산 최적 배분 | SJF 스케줄링, 가중합 스코어링,<br>그리디 배분, 0-1 Knapsack DP | Min Heap, 세그먼트 트리,<br>우선순위 큐, DP 테이블 |
| 나하림 | 데이터 엔지니어링 | **M2** 위험구역 확산 예측 | BFS 확산 모델, 셀룰러 오토마타 | 2D Grid, Queue |
| 김도현 | 프론트엔드 | **M1** 대피소 수용량 배분 | 이분 매칭, 헝가리안 | 이분 그래프, 2D 비용행렬 |
| 최의찬 | 발표·문서화 | **M5** 비상 통신망 설계 | 크루스칼(MST), Tarjan(SPOF) | 그래프, Union-Find |

추가 담당: 임성엽 — GitHub 브랜치 관리, `app.py` 통합, `core/` 공유 유틸 / 나하림 — 공공데이터 수집·전처리 / 김도현 — Streamlit 대시보드 UI/UX / 최의찬 — 프로젝트 설명서(PDF)·발표 영상

---

## 재난 대응 타임라인 (모듈 흐름)

```
재난 발생
    │
    ▼
[1단계: 상황 파악]
    M2  위험구역 확산 예측       BFS + 셀룰러 오토마타
    │
    │  risk_map (node_id → 위험도 0~1) 을 아래 모든 단계에 전달
    ▼
[2단계: 즉각 대응]
    M1  대피소 수용량 배분       헝가리안 + 이분 매칭
    M3  부상자 이송 우선순위     SJF + 가중합 스코어링
    M4  구조자원 배치            헝가리안 (M1 로직 재사용)
    │
    │  M1 출력(대피소별 배정 인원)을 M6에 전달
    ▼
[3단계: 구호]
    M6  구호물자 수요 산정       그리디 + 우선순위 큐
    │
    ▼
[4단계: 복구]
    M5  비상 통신망 복구         크루스칼 MST + Tarjan SPOF
    M7  복구 예산 최적 배분      0-1 Knapsack DP
```

**모듈 연결 규칙**: `st.session_state`로 상류 모듈의 출력을 공유합니다.  
M2를 먼저 실행하면 M1·M3·M4·M5·M7의 비용/우선순위 계산에 실제 위험도가 반영됩니다.  
M2 미실행 시 각 모듈은 기본값으로 단독 실행됩니다 (과제 독립 실행 요건 충족).

---

## 모듈 상세

### M1 · 대피소 수용량 배분 (`modules/m1_shelter/`) — 김도현
> 시민 집합과 대피소 집합 간 최적 배정 문제를 이분 매칭으로 해결합니다.

- 이분 그래프로 시민 ↔ 대피소 관계 모델링
- 헝가리안 알고리즘으로 전체 이동 비용 최소화 (순수 Python 직접 구현)
- 수용량 처리: 대피소를 capacity만큼 노드 복제하여 1:1 매칭으로 변환
- 2D 비용행렬: 이동 거리 + 위험도(risk_map) + 혼잡도 가중 반영

### M2 · 위험구역 확산 예측 (`modules/m2_spread/`) — 나하림
> 화재·침수 등 재난의 공간적 확산을 시뮬레이션합니다.

- 60×60 2D 격자로 송파구 지형 추상화
- BFS 기반 확산 모델로 위험 도달 시간 계산
- 셀룰러 오토마타로 바람·지형 조건에 따른 동적 변화 표현
- 출력 `risk_map`은 전 모듈의 공통 입력

### M3 · 부상자 이송 우선순위 결정 (`modules/m3_triage/`) — 임성엽
> 중증도 + 골든타임 기반으로 구급차 이송 순서를 실시간 결정합니다.

- 가중합 스코어링으로 중증도·대기시간을 단일 우선순위 점수로 환산
- Min Heap으로 전체 최우선 환자 O(log n) 추출
- 세그먼트 트리로 중증도 구간(4~5) 내 최우선 환자 조회
- SJF 스케줄링으로 구급차별 운행 순서(이송시간 최소화) 결정
- 설계 원칙: 중증도 우선 배정 → 운행 순서만 SJF (트리아지 원칙과 충돌 없음)

### M4 · 구조자원 배치 (`modules/m4_resource/`) — 임성엽
> 자원봉사자·구조 장비를 재난 현장에 최적 배치합니다.

- M1의 헝가리안 매칭 로직을 재사용 (알고리즘 확장성 검증)
- M1이 시민을 대피소로 보내는 방향이라면, M4는 구조 자원을 현장으로 보내는 역방향
- risk_map 위험도가 높은 현장에 우선 배치

### M5 · 비상 통신망 설계 (`modules/m5_network/`) — 최의찬
> 재난으로 파괴된 통신망을 최소 비용으로 복구하는 경로를 설계합니다.

- 크루스칼 알고리즘 + Union-Find로 MST(최소 신장 트리) 구축
- Tarjan 알고리즘으로 단일 장애점(SPOF) 단절점 탐지 및 보강
- 통신 거점: 대피소·병원 노드를 비상 통신 거점으로 사용

### M6 · 구호물자 수요 산정 (`modules/m6_supply/`) — 임성엽
> 대피소별 배정 인원 기반으로 물·식량·의약품 수요를 계산하고 배분합니다.

- M1 출력(`shelter_assign`)을 입력으로 대피소별 필요 물자량 산정
- 그리디 배분: 위험도·인원 기반 우선순위 순으로 한정 물자 배분
- 우선순위 큐로 배분 순서 관리

### M7 · 복구 예산 최적 배분 (`modules/m7_budget/`) — 임성엽
> 한정된 복구 예산으로 피해 지역 복구 효과를 최대화합니다.

- 0-1 Knapsack DP: 예산 제한 내에서 복구 효과 합계 최대화
- risk_map 위험도를 피해 심각도 → 복구 효과 가중치로 연결
- 2D DP 테이블로 (지역, 예산) 상태 공간 탐색

---

## 폴더 구조

```
algorithm/
│
├── app.py                        # Streamlit 메인 진입점
├── requirements.txt              # 의존성 라이브러리 (버전 고정)
│
├── core/                         # 전 모듈 공유 유틸
│   ├── data_loader.py            # processed/ 로드 + session_state 배선 (임성엽)
│   └── distance_util.py          # 다익스트라 이송시간 유틸 (임성엽)
│
├── data/
│   ├── raw/                      # 원본 공공데이터 CSV (출처 주석 필수)
│   │   ├── 송파구_민방위대피소.csv    # 출처: 공공데이터포털·행정안전부
│   │   └── 송파구_격자인구.csv       # 출처: 통계청 SGIS 100m 격자
│   ├── preprocess.py             # raw → processed 변환 (나하림)
│   └── processed/                # 모듈이 읽는 유일한 데이터 소스
│       ├── graph_data.json       # 공통 그래프 토대
│       ├── patients.json         # M3용 부상자 (KTAS 분포 기반 생성)
│       ├── volunteers.json       # M4용 자원봉사자·장비
│       ├── supplies.json         # M6용 물자 카탈로그
│       └── damage_zones.json     # M7용 피해 지역
│
└── modules/
    ├── __init__.py
    ├── m1_shelter/               # 대피소 배분 (김도현)
    │   ├── __init__.py           # run() + compute() 노출
    │   ├── shelter.py
    │   └── ui_shelter.py
    ├── m2_spread/                # 확산 예측 (나하림)
    │   ├── __init__.py
    │   ├── bfs_spread.py
    │   ├── cellular_automata.py
    │   └── ui_spread.py
    ├── m3_triage/                # 부상자 이송 (임성엽)
    │   ├── __init__.py
    │   ├── priority_queue.py
    │   ├── optimizer.py
    │   └── ui_triage.py
    ├── m4_resource/              # 구조자원 배치 (임성엽)
    │   ├── __init__.py
    │   ├── resource.py
    │   └── ui_resource.py
    ├── m5_network/               # 통신망 복구 (최의찬)
    │   ├── __init__.py
    │   ├── mst_kruskal.py
    │   ├── tarjan.py
    │   └── ui_network.py
    ├── m6_supply/                # 구호물자 수요 (임성엽)
    │   ├── __init__.py
    │   ├── supply.py
    │   └── ui_supply.py
    └── m7_budget/                # 복구 예산 배분 (임성엽)
        ├── __init__.py
        ├── budget.py
        └── ui_budget.py
```

---

## 데이터 스키마 (인터페이스 계약)

### graph_data.json

모든 모듈이 읽는 공통 토대입니다. **preprocess.py 외에는 이 파일을 직접 수정하지 않습니다.**

```json
{
  "meta": {
    "region": "서울특별시 송파구",
    "sources": ["행정안전부 민방위대피소(공공데이터포털)", "통계청 SGIS 100m 격자인구"],
    "created": "YYYY-MM-DD"
  },
  "simulation_settings": {
    "grid_width": 60,
    "grid_height": 60,
    "cell_size_m": 100
  },
  "nodes": [
    {
      "id": "node_001",
      "name": "2호선 종합운동장역",
      "type": "shelter",
      "lat": 37.511, "lng": 127.0734,
      "grid_x": 5, "grid_y": 36,
      "capacity": 22288,
      "population_density": 8500
    }
  ],
  "edges": [
    {"from": "node_001", "to": "node_002", "distance": 1.15, "weight": 1.38}
  ],
  "grid_mapping": {
    "node_001": {"row": 36, "col": 5}
  }
}
```

**노드 타입 정의**

| type | 의미 | 주 사용 모듈 |
|------|------|--------------|
| `shelter` | 민방위 대피소 (비상 통신 거점 겸용) | M1, M5 |
| `hospital` | 병원 (비상 통신 거점 겸용) | M3, M5 |

> M5 통신망 복구는 별도 통신 허브 노드 없이 shelter·hospital 노드 간 MST를 구성합니다.

**필드 규칙**

- `id`: 문자열 (`"node_001"`). 격자 인덱싱은 `grid_x`, `grid_y` 필드를 사용하고 id 문자열 파싱은 금지
- `population_density`: 통계청 SGIS 격자 인구 기반 실데이터
- `distance = 0`인 엣지(동일 좌표 시설): `data_loader`가 로드 시 0.05km로 자동 클램프
- 같은 격자칸에 노드가 여러 개인 경우: 해당 칸의 위험도를 칸 내 모든 노드에 동일 적용

### session_state 키 목록 (모듈 간 데이터 공유 계약)

| 키 | 생성 모듈 | 소비 모듈 | 형식 |
|----|-----------|-----------|------|
| `risk_map` | M2 | M1, M3, M4, M5, M7 | `{node_id: float 0~1}` |
| `shelter_assign` | M1 | M6 | `[{citizen_grp, shelter_id, count}]` |
| `transport_order` | M3 | — | `[{patient_id, priority, eta}]` |
| `resource_assign` | M4 | — | `[{vol_id, site_id, cost}]` |
| `supply_demand` | M6 | — | `{shelter_id: {water, food, med}}` |
| `network_plan` | M5 | — | `{mst_edges: [], spof_nodes: []}` |
| `budget_plan` | M7 | — | `[{zone_id, allocated, effect}]` |

---

## 모듈 인터페이스 규약

모든 모듈은 아래 두 함수를 `__init__.py`에서 노출합니다.

```python
def run() -> None:
    """Streamlit UI 진입점. app.py가 호출."""

def compute(data: dict, params: dict) -> dict:
    """순수 로직. UI 없이 단독 테스트 가능."""
```

`run()`과 `compute()`를 분리하는 이유: UI 작업이 로직 완성을 기다리지 않고  
더미 dict 기반으로 병렬 진행될 수 있습니다. 로직 변경이 UI를 깨뜨리지 않습니다.

---

## app.py 통합 구조

```python
import streamlit as st
from modules import m1_shelter, m2_spread, m3_triage, m4_resource
from modules import m5_network, m6_supply, m7_budget

# 역할 선택 진입 화면 (인증 없음)
# "통합 관제" / "대피·구호" / "복구 계획"

# 사이드바 타임라인 그룹핑 — 선택된 모듈의 run() 1개만 호출
menu = st.sidebar.radio("단계 선택", [
    "위험구역 확산 예측",
    "대피소 배정",
    "부상자 이송",
    "구조자원 배치",
    "구호물자 수요",
    "통신망 복구",
    "복구 예산 배분",
])
```

- 각 모듈은 사이드바 '실행' 버튼 클릭 시에만 결과 출력 (버튼 key 모듈별 고유화)
- UI에는 모듈 코드명(M1~M7)·담당자·알고리즘 캡션을 노출하지 않음 (코드 주석으로만 표기)

---

## 코드 작성 공통 규칙

자료구조·알고리즘 사용 부분에 아래 형식으로 주석을 필수 표기합니다.

```python
# [자료구조: 최소 힙(Min Heap)]
# [자료구조: 세그먼트 트리(Segment Tree)]
# [자료구조: Union-Find]
# [알고리즘: SJF 스케줄링(Shortest Job First)]
# [알고리즘: 가중합 스코어링(Weighted Sum Scoring)]
# [알고리즘: BFS 기반 확산 모델]
# [알고리즘: 헝가리안(Hungarian Algorithm)]
# [알고리즘: 크루스칼(Kruskal MST)]
# [알고리즘: 0-1 배낭 문제(Knapsack DP)]
```

데이터를 사용하는 파일 상단에 출처를 표기합니다.

```python
# 데이터 출처: 행정안전부 민방위대피소 (공공데이터포털 data.go.kr)
# 데이터 출처: 통계청 SGIS 100m 격자인구
```

---

## 브랜치 전략

```
main          ← 최종 제출용 (팀장 머지만)
  └─ dev      ← 통합 테스트용
       ├─ feature/m1-shelter    (김도현)
       ├─ feature/m2-spread     (나하림)
       ├─ feature/m3-triage     (임성엽)
       ├─ feature/m4-resource   (임성엽)
       ├─ feature/m5-network    (최의찬)
       ├─ feature/m6-supply     (임성엽)
       └─ feature/m7-budget     (임성엽)
```

> **PR 규칙**: `dev` 브랜치로만 PR 요청 → 팀장 코드 리뷰 후 머지

---

## 실행 방법

```bash
# 1. 레포지토리 클론
git clone https://github.com/GachonAlgorithm10/algorithm.git
cd algorithm

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 전체 앱 실행
streamlit run app.py

# 4. 모듈 단독 실행 (개발/테스트용)
streamlit run modules/m1_shelter/ui_shelter.py
streamlit run modules/m2_spread/ui_spread.py
streamlit run modules/m3_triage/ui_triage.py
streamlit run modules/m4_resource/ui_resource.py
streamlit run modules/m5_network/ui_network.py
streamlit run modules/m6_supply/ui_supply.py
streamlit run modules/m7_budget/ui_budget.py
```

---

## 협업 채널 (Discord)

| 채널 | 용도 |
|------|------|
| `#공지-및-일정` | 마일스톤·데드라인 공지 |
| `#깃허브-알림` | PR·Push 봇 알림 |
| `#데이터-공유` | 데이터 파일 공유 및 스키마 논의 |
| `#아키텍처-통합` | app.py 병합·session_state 조율 |
| `#프론트엔드-ui` | 화면 레이아웃 피드백 |
| `#알고리즘-디버깅` | 코드 에러 리뷰 |
| `#문서-발표-준비` | 설명서·영상 피드백 |
