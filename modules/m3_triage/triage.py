"""
M3 부상자 이송 우선순위 결정 모듈
담당: 임성엽
알고리즘: SJF 스케줄링(Shortest Job First), 가중합 스코어링(Weighted Sum Scoring)
자료구조: 최소 힙(Min Heap), 우선순위 큐(Priority Queue)

※ 설계 메모
- SJF 기본 철학(짧은 작업 먼저)을 이송 맥락에 적용:
  "이송 소요시간이 짧은 환자"를 우선 처리해 총 대기시간 최소화.
- 단, 순수 SJF는 중증 환자를 후순위로 밀 수 있음.
  → 가중합 스코어링으로 중증도·거리·대기시간을 종합해 보정.
  → 설명서 ⑤·⑥에서 이 결합 논리를 명확히 기술할 것.
"""
import heapq
import streamlit as st
import pandas as pd

# [자료구조: 최소 힙 (Min Heap)]
# Python heapq 모듈 사용. 우선순위 점수가 낮을수록(= 위급할수록) 먼저 pop.
# 내부 표현: (score, patient_id, patient_dict)

# [자료구조: 우선순위 큐 (Priority Queue)]
# 최소 힙 위에서 동작하는 추상 자료구조.
# push: heapq.heappush / pop: heapq.heappop

# [알고리즘: 가중합 스코어링 (Weighted Sum Scoring)]
# 복수 기준(중증도·거리·대기시간)을 단일 우선순위 점수로 환산.
# score = -(w1*severity + w2*(1/(distance+ε)) + w3*wait_time)
# 음수 취해 Min Heap에서 높은 우선순위가 먼저 나오도록 처리.

# [알고리즘: SJF 스케줄링 (Shortest Job First)]
# 힙에서 순서대로 pop → 이송 스케줄 생성.
# 이송 소요시간 = f(distance). 짧은 이송이 먼저 처리되는 SJF 구조.


def calculate_priority_score(
    severity: int,
    distance: float,
    wait_time: int,
    w1: float = 0.5,
    w2: float = 0.3,
    w3: float = 0.2,
) -> float:
    """
    [알고리즘: 가중합 스코어링]
    부상자 우선순위 점수 계산. 값이 작을수록 먼저 이송.

    Args:
        severity : 중증도 (1=경증, 2=중등, 3=중증)
        distance : 최인접 병원까지 이송 거리 (km)
        wait_time: 현재 대기 시간 (분)
        w1, w2, w3: 가중치 (합 = 1.0 권장)

    Returns:
        float: 우선순위 점수 (낮을수록 먼저 이송)
    """
    epsilon = 1e-6  # 거리 0 방지
    # TODO: 스코어 공식 구현 — 부호 반전(음수)으로 Min Heap 호환
    score = 0.0
    return score


def build_priority_queue(patients: list) -> list:
    """
    [자료구조: 최소 힙 + 우선순위 큐]
    환자 리스트 → 우선순위 힙 생성.

    Args:
        patients: [
            {"id": str, "severity": int, "distance": float, "wait": int},
            ...
        ]

    Returns:
        list: heapq 힙 (score, patient_id, patient_dict)
    """
    # [자료구조: 최소 힙 (Min Heap)]
    heap = []
    for p in patients:
        score = calculate_priority_score(p["severity"], p["distance"], p["wait"])
        heapq.heappush(heap, (score, p["id"], p))
    return heap


def schedule_transport(heap: list) -> list:
    """
    [알고리즘: SJF 스케줄링]
    힙에서 순서대로 pop → 이송 순서 결정.

    Returns:
        list: 이송 순서대로 정렬된 환자 목록
              [{"rank": int, "id": str, ...patient_fields}, ...]
    """
    schedule = []
    rank = 1
    temp_heap = heap[:]  # 원본 힙 보존
    while temp_heap:
        score, pid, patient = heapq.heappop(temp_heap)
        schedule.append({"rank": rank, **patient, "priority_score": score})
        rank += 1
    return schedule


def run():
    st.header("🚑 M3 부상자 이송 우선순위 결정")
    st.caption(
        "담당: 임성엽 | "
        "알고리즘: SJF 스케줄링, 가중합 스코어링 | "
        "자료구조: Min Heap, 우선순위 큐"
    )

    # TODO: Streamlit UI 구현
    st.info("구현 중입니다.")
