# CONTRIBUTING — 코드 작성 규칙

> 모든 팀원이 작업 시작 전에 읽어야 합니다.  
> 이 문서의 규칙을 따르지 않으면 `app.py` 통합 시 충돌이 발생합니다.

---

## 1. 모듈 인터페이스 규칙

모든 모듈은 `__init__.py`에서 아래 두 함수만 노출합니다.

```python
# modules/mX_xxx/__init__.py

from .xxx import compute
from .ui_xxx import run

__all__ = ["compute", "run"]
```

### compute()

순수 로직 함수입니다. Streamlit import 없이 단독 실행 가능해야 합니다.

```python
def compute(data: dict, params: dict) -> dict:
    """
    Args:
        data  : data_loader에서 로드한 데이터
                필수 키: "graph"  (graph_data.json 전체)
                선택 키: 모듈별 추가 데이터 (아래 모듈별 규칙 참조)
        params: UI 슬라이더·입력값 (dict)
    Returns:
        dict  : 모듈별 출력 (아래 session_state 키 규칙 참조)
    """
```

### run()

Streamlit UI 함수입니다. `app.py`가 호출합니다.

```python
def run() -> None:
    """
    - 실행 버튼 클릭 전: 안내 메시지만 표시
    - 실행 버튼 클릭 후: compute() 호출 → 결과 출력 → session_state 저장
    - UI에 모듈 코드명(M1~M7)·담당자명 노출 금지
    """
```

### 모듈별 compute() 입출력 명세

| 모듈 | data 추가 키 | params 키 | 반환 키 |
|------|-------------|-----------|---------|
| M1 | `"risk_map"` (선택) | `"num_citizens"` | `"shelter_assign"` |
| M2 | — | `"start_node"`, `"time_steps"` | `"risk_map"` |
| M3 | `"patients"`, `"risk_map"` (선택) | `"num_ambulances"` | `"transport_order"` |
| M4 | `"volunteers"`, `"risk_map"` (선택) | `"num_sites"` | `"resource_assign"` |
| M5 | `"risk_map"` (선택) | — | `"network_plan"` |
| M6 | `"shelter_assign"`, `"supplies"` | — | `"supply_demand"` |
| M7 | `"damage_zones"`, `"risk_map"` (선택) | `"budget_million"` | `"budget_plan"` |

선택 키가 없으면 해당 모듈은 기본값으로 단독 실행합니다.

---

## 2. session_state 규칙

### 키 이름 — 반드시 아래 이름 그대로 사용합니다. 임의 변경 금지.

| 키 | 타입 | 쓰는 모듈 | 읽는 모듈 |
|----|------|-----------|-----------|
| `"risk_map"` | `dict[str, float]` | M2 | M1, M3, M4, M5, M7 |
| `"shelter_assign"` | `list[dict]` | M1 | M6 |
| `"transport_order"` | `list[dict]` | M3 | — |
| `"resource_assign"` | `list[dict]` | M4 | — |
| `"supply_demand"` | `dict[str, dict]` | M6 | — |
| `"network_plan"` | `dict` | M5 | — |
| `"budget_plan"` | `list[dict]` | M7 | — |

### 쓰기 규칙

`run()` 안에서 `compute()` 호출 직후 저장합니다.

```python
def run():
    if st.button("실행", key="triage_run_btn"):
        result = compute(data, params)
        st.session_state["transport_order"] = result["transport_order"]
        # 결과 출력
```

### 읽기 규칙

상류 모듈 출력이 없으면 기본값으로 대체합니다. `KeyError` 절대 금지.

```python
# 올바른 예
risk_map = st.session_state.get("risk_map", {})

# 금지
risk_map = st.session_state["risk_map"]  # KeyError 발생 가능
```

---

## 3. 실행 버튼 key 규칙

버튼 key가 중복되면 `StreamlitDuplicateElementId` 에러가 발생합니다.  
아래 key를 그대로 사용합니다.

| 모듈 | 버튼 key |
|------|----------|
| M1 | `shelter_run_btn` |
| M2 | `spread_run_btn` |
| M3 | `triage_run_btn` |
| M4 | `resource_run_btn` |
| M5 | `network_run_btn` |
| M6 | `supply_run_btn` |
| M7 | `budget_run_btn` |

---

## 4. 데이터 로드 규칙

모든 모듈은 `core/data_loader.py`를 통해서만 데이터를 로드합니다.  
모듈 내부에서 직접 파일 경로를 지정하거나 `open()`으로 읽지 않습니다.

```python
# 올바른 예
from core.data_loader import load_graph, load_patients

# 금지
with open("data/processed/graph_data.json") as f:  # 직접 읽기 금지
    data = json.load(f)
```

---

## 5. 파일·폴더 네이밍 규칙

```
modules/mX_xxx/          모듈 폴더 — mX 번호 + 기능명 소문자
    __init__.py          compute() + run() 노출만
    xxx.py               로직 (Streamlit import 없음)
    ui_xxx.py            Streamlit UI
feature/mX-xxx           브랜치명 — 하이픈 구분
```

금지 패턴:
- `module_xxx/` (단수형 + 언더스코어) — 사용 금지
- `Module_M1/` (대문자) — 사용 금지

---

## 6. 주석 규칙

자료구조·알고리즘 사용 부분에 반드시 표기합니다.

```python
# [자료구조: 최소 힙(Min Heap)]
# [자료구조: 세그먼트 트리(Segment Tree)]
# [자료구조: 2D DP 테이블]
# [자료구조: Union-Find]
# [자료구조: 이분 그래프]
# [자료구조: 2D 비용행렬]
# [자료구조: 2D Grid]
# [알고리즘: SJF 스케줄링(Shortest Job First)]
# [알고리즘: 가중합 스코어링(Weighted Sum Scoring)]
# [알고리즘: 헝가리안(Hungarian Algorithm)]
# [알고리즘: 이분 매칭(Bipartite Matching)]
# [알고리즘: BFS 기반 확산 모델]
# [알고리즘: 셀룰러 오토마타(Cellular Automata)]
# [알고리즘: 크루스칼(Kruskal MST)]
# [알고리즘: Tarjan SPOF 탐지]
# [알고리즘: 그리디 배분(Greedy)]
# [알고리즘: 0-1 배낭 문제(Knapsack DP)]
```

데이터 파일 사용 시 상단에 출처 표기합니다.

```python
# 데이터 출처: 행정안전부 민방위 대피소 (공공데이터포털 data.go.kr)
# 데이터 출처: 서울시 병원 현황 (서울 열린데이터광장 data.seoul.go.kr/OA-16182)
# 데이터 출처: 서울시 250m 격자 생활인구 (data.seoul.go.kr/OA-22784)
```

---

## 7. PR 규칙

- `dev` 브랜치로만 PR 요청 (main 직접 push 금지)
- PR 제목 형식: `[M1] 헝가리안 수용량 처리 구현`
- PR 본문에 완료된 이슈 번호 명시: `closes #이슈번호`
- 팀장 리뷰 후 머지
