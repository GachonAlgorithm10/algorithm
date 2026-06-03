"""
M2 위험 구역 확산 예측 모듈
담당: 나하림
알고리즘: BFS 확산 모델(BFS-based Spread Model), 셀룰러 오토마타(Cellular Automata)
자료구조: 2D 격자(2D Grid), 큐(Queue)
"""
import streamlit as st
import numpy as np
from collections import deque

# [자료구조: 2D 격자 (2D Grid)]
# 지역을 격자로 표현. grid[row][col] = 위험도 레벨(0=안전, 1=주의, 2=위험, 3=재난)
# np.ndarray (H x W) 사용

# [자료구조: 큐 (Queue)]
# BFS 확산 탐색에 사용. collections.deque로 구현 (O(1) popleft)

# [알고리즘: BFS 확산 모델 (BFS-based Spread Model)]
# 재난 발생 지점에서 인접 격자로 단계적 확산 시뮬레이션
# 일반 BFS와 달리 가중치(지형·바람 등)를 반영한 확산 속도 적용

# [알고리즘: 셀룰러 오토마타 (Cellular Automata)]
# 각 셀이 이웃 셀의 상태에 따라 다음 상태를 결정하는 규칙 기반 모델
# Moore 이웃(8방향) 또는 Von Neumann 이웃(4방향) 사용


def init_grid(rows: int, cols: int) -> np.ndarray:
    """
    [자료구조: 2D 격자]
    초기 안전 격자 생성.

    Returns:
        np.ndarray: shape (rows, cols), 초기값 0(안전)
    """
    return np.zeros((rows, cols), dtype=int)


def bfs_spread(grid: np.ndarray, source: tuple, steps: int) -> np.ndarray:
    """
    [알고리즘: BFS 확산 모델]
    [자료구조: 큐]
    재난 발생점(source)으로부터 BFS로 위험 구역 확산 시뮬레이션.

    Args:
        grid: 초기 격자 (init_grid 결과)
        source: 재난 발생 격자 좌표 (row, col)
        steps: 확산 단계 수

    Returns:
        np.ndarray: 확산 후 위험도 격자
    """
    result = grid.copy()
    rows, cols = result.shape

    # [자료구조: 큐 (Queue)] — deque로 BFS 탐색
    queue = deque()
    queue.append((source[0], source[1], 0))  # (row, col, depth)
    result[source[0]][source[1]] = 3  # 발생지 = 최고 위험

    visited = set()
    visited.add(source)

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Von Neumann 4방향

    # TODO: BFS 확산 로직 구현 (가중치 반영)
    while queue:
        r, c, depth = queue.popleft()
        if depth >= steps:
            continue
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                # TODO: 위험도 레벨 계산 (depth 기반 감쇠)
                queue.append((nr, nc, depth + 1))

    return result


def cellular_automata_step(grid: np.ndarray) -> np.ndarray:
    """
    [알고리즘: 셀룰러 오토마타]
    현재 격자 상태에서 다음 단계 상태 계산.
    이웃 셀의 위험도 평균이 임계값 초과 시 위험 전파.

    Returns:
        np.ndarray: 다음 단계 격자
    """
    # TODO: CA 규칙 구현
    next_grid = grid.copy()
    return next_grid


def get_grid_node_mapping(grid: np.ndarray, graph_data: dict) -> dict:
    """
    격자 좌표 ↔ graph_data 노드 id 매핑 반환.
    M1·M5가 그래프 노드 기준으로 동작하므로 이 매핑이 연결 고리.
    graph_data.json의 grid_mapping 필드 활용.

    Returns:
        dict: {(row, col): "node_id", ...}
    """
    mapping = {}
    for node_id, pos in graph_data.get("grid_mapping", {}).items():
        if "_comment" in node_id:
            continue
        mapping[(pos["row"], pos["col"])] = node_id
    return mapping


def run():
    st.header("🔥 M2 위험 구역 확산 예측")
    st.caption("담당: 나하림 | 알고리즘: BFS 확산 모델, 셀룰러 오토마타 | 자료구조: 2D 격자, 큐")

    # TODO: Streamlit UI 구현
    st.info("구현 중입니다.")
