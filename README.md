# 🚨 대규모 재난 대피 및 물류 최적화 시스템
> **가천대학교 알고리즘 기말 프로젝트** | Team GachonAlgorithm10

---

## 📌 프로젝트 개요

대규모 재난(화재, 침수 등) 발생 시 **시민 대피 경로 최적화**, **위험 구역 확산 예측**, **부상자 이송 우선순위 결정**, **비상 통신망 복구 설계**를 통합적으로 지원하는 서비스 프로토타입입니다.

| 항목 | 내용 |
|------|------|
| 개발 기간 | 2026년 ~ 2026년 6월 19일 |
| 제출 기한 | 2026년 6월 19일 (금) 자정 |
| 실행 환경 | Python 3.10+, Streamlit |
| GitHub Org | [GachonAlgorithm10](https://github.com/GachonAlgorithm10) |

---

## 👥 팀원 및 역할 분담

| 이름 | 역할 | 담당 모듈 | 알고리즘 | 자료구조 | 추가 담당 |
|------|------|-----------|----------|----------|-----------|
| 임성엽 (팀장) | 기획 / 백엔드 통합 | **M3** 부상자 이송 우선순위 결정 | SJF 스케줄링, 다목적 최적화 | Min Heap, 우선순위 큐 | GitHub 브랜치 관리, `app.py` 통합 |
| 나하림 | 데이터 엔지니어링 | **M2** 위험 구역 확산 예측 | BFS 기반 확산 모델, 셀룰러 오토마타 | 2D Grid, Queue | 공공데이터 CSV 수집 및 graph_data 전처리 |
| 김도현 | 프론트엔드 | **M1** 대피소 수용량 배분 | 이분 매칭, 헝가리안 알고리즘 | 이분 그래프, 2D 비용 행렬 | Streamlit 웹 대시보드 UI/UX 개발 |
| 최의찬 | 발표 / 문서화 | **M5** 비상 통신망 설계 | 크루스칼(MST), Tarjan 알고리즘 | 그래프, Union-Find | 프로젝트 설명서(PDF) 및 발표 영상 제작 |

---

## 🗂️ 모듈 상세 설명

### M1 · 대피소 수용량 배분 (`module_m1_shelter/`) — 김도현
> 시민 집합과 대피소 집합 간의 최적 배정 문제를 이분 매칭으로 해결합니다.

- 이분 그래프로 시민 ↔ 대피소 관계 모델링
- 헝가리안 알고리즘으로 전체 이동 비용 최소화
- 2차원 비용 행렬: 이동 거리 + 혼잡도 가중치 반영

---

### M2 · 위험 구역 확산 예측 (`module_m2_spread/`) — 나하림
> 화재·침수 등 재난의 공간적 확산을 시뮬레이션합니다.

- 2D 격자(Grid)로 실제 지형 추상화
- BFS(너비 우선 탐색) 기반 확산 모델로 도달 시간 계산
- 셀룰러 오토마타로 바람·지형 조건에 따른 동적 변화 표현

---

### M3 · 부상자 이송 우선순위 결정 (`module_m3_triage/`) — 임성엽
> 중증도 + 골든타임 기반으로 구급차 이송 순서를 실시간 결정합니다.

- Min Heap 기반 우선순위 큐: O(log n) 삽입·삭제
- SJF 스케줄링으로 대기 시간 최소화
- 다목적 최적화로 병상 수·이동 거리 종합 고려

---

### M5 · 비상 통신망 설계 (`module_m5_network/`) — 최의찬
> 재난으로 파괴된 통신망을 최소 비용으로 복구하는 경로를 설계합니다.

- 크루스칼 알고리즘 + Union-Find로 MST(최소 신장 트리) 구축
- Tarjan 알고리즘으로 단일 장애점(SPOF) 단절점 탐지 및 보강

---

## 🏗️ 아키텍처

```
GachonAlgorithm10/
│
├── app.py                      # Streamlit 메인 진입점 (임성엽 통합)
├── requirements.txt            # 의존성 라이브러리 (버전 고정)
├── data/                       # 공공데이터 CSV 및 graph_data (나하림)
│   ├── preprocess.py           # CSV → graph_data.json 전처리 스크립트
│   ├── graph_data.json         # 인접 리스트 딕셔너리
│   └── raw/                    # 원본 CSV (출처 표기 포함)
│
├── module_m1_shelter/          # 대피소 배분 모듈 (김도현)
│   ├── __init__.py
│   ├── matching.py             # 이분 매칭 / 헝가리안
│   └── ui_shelter.py           # Streamlit UI
│
├── module_m2_spread/           # 확산 예측 모듈 (나하림)
│   ├── __init__.py
│   ├── bfs_spread.py           # BFS 확산 모델
│   ├── cellular_automata.py    # 셀룰러 오토마타
│   └── ui_spread.py            # Streamlit UI
│
├── module_m3_triage/           # 부상자 이송 모듈 (임성엽)
│   ├── __init__.py
│   ├── priority_queue.py       # Min Heap / 세그먼트 트리
│   ├── optimizer.py            # 가중합 스코어링 / SJF
│   └── ui_triage.py            # Streamlit UI
│
└── module_m5_network/          # 통신망 복구 모듈 (최의찬)
    ├── __init__.py
    ├── mst_kruskal.py          # 크루스칼 + Union-Find
    ├── tarjan.py               # Tarjan SPOF 탐지
    └── ui_network.py           # Streamlit UI
```

---

## 🌿 브랜치 전략

```
main          ← 최종 제출용 (팀장 머지만)
  └─ dev      ← 통합 테스트용
       ├─ feature/m1-shelter    (김도현)
       ├─ feature/m2-spread     (나하림)
       ├─ feature/m3-triage     (임성엽)
       └─ feature/m5-network    (최의찬)
```

> **PR 규칙**: `dev` 브랜치로만 PR 요청 → 팀장 코드 리뷰 후 머지

> **브랜치 보호**: GitHub Settings → Branches → `main` 브랜치에 `Require pull request before merging` 설정 권장 (직접 push 방지)

---

## ⚙️ 실행 방법

```bash
# 1. 레포지토리 클론
git clone https://github.com/GachonAlgorithm10/<repo-name>.git
cd <repo-name>

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행
streamlit run app.py
```

---

## 📦 주요 라이브러리

```text
streamlit
numpy
pandas
scipy
networkx
matplotlib
plotly
```

> **버전 고정**: 개발 환경 세팅 후 `pip freeze > requirements.txt` 로 버전을 고정해 주세요. 라이브러리 버전 충돌을 방지합니다.

---

## 📋 코드 작성 공통 규칙

```python
# 자료구조·알고리즘 사용 부분에 반드시 주석 명시
# 형식: # [자료구조: 이름] / # [알고리즘: 이름]

# --- M1 대피소 배분 ---
# [알고리즘: 헝가리안 알고리즘]
def assign_shelters(cost_matrix):
    ...

# --- M2 확산 예측 ---
# [자료구조: 2D 격자(Grid)]
# [알고리즘: BFS 기반 확산 모델]
def bfs_spread(grid, start):
    ...

# --- M3 부상자 이송 ---
# [자료구조: 최소 힙(Min Heap)]
import heapq
# [알고리즘: 최단작업우선 스케줄링(SJF)]
def sjf_schedule(patients):
    ...

# --- M5 통신망 설계 ---
# [자료구조: 유니온-파인드(Union-Find)]
# [알고리즘: 최소신장트리(크루스칼)]
def build_mst(edges):
    ...
```

---

## 🗓️ 마일스톤

| 단계 | 내용 | 기한 |
|------|------|------|
| ✅ 기획 | 모듈 배분 확정, 브랜치 세팅 | 6/3 |
| 🔲 개발 | 각자 모듈 핵심 로직 구현 완료 | 6/8 |
| 🔲 통합 | app.py 통합 + 버그 수정 | 6/10 |
| 🔲 초안 제출 | UI, 설명서 초안 완성 | 6/11 |
| 🔲 마무리 | 설명서 완성, 영상 녹화, 최종 제출 | 6/19 자정 |

---

## 📞 협업 채널 (Discord)

| 채널 | 용도 |
|------|------|
| `#공지-및-일정` | 마일스톤·데드라인 공지 |
| `#깃허브-알림` | PR·Push 봇 알림 |
| `#데이터-공유` | graph_data 파일 공유 |
| `#아키텍처-통합` | app.py 병합 이슈 조율 |
| `#프론트엔드-ui` | 화면 레이아웃 피드백 |
| `#알고리즘-디버깅` | 코드 에러 리뷰 |
| `#문서-발표-준비` | 설명서·영상 피드백 |
