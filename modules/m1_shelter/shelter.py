"""
M1 대피소 수용량 배분 모듈
담당: 김도현
알고리즘: 이분 매칭(Bipartite Matching), 헝가리안 알고리즘(Hungarian Algorithm)
자료구조: 이분 그래프(Bipartite Graph), 2D 비용행렬(Cost Matrix)
"""
import streamlit as st
import numpy as np

# [자료구조: 이분 그래프 (Bipartite Graph)]
# 시민 집단(좌측) ↔ 대피소(우측) 간 매칭을 위한 그래프
# 인접 리스트 형태로 표현: {시민_id: [대피소_id, ...], ...}

# [자료구조: 2D 비용행렬 (Cost Matrix)]
# cost[i][j] = 시민 집단 i → 대피소 j 이동 비용(거리/시간)
# scipy.optimize.linear_sum_assignment 또는 직접 구현에 사용

# [알고리즘: 이분 매칭 (Bipartite Matching)]
# 시민 집단과 대피소를 1:1 또는 다대일로 최적 매칭
# DFS 기반 증가 경로 탐색

# [알고리즘: 헝가리안 알고리즘 (Hungarian Algorithm)]
# 최소 비용 할당 문제(Assignment Problem) 해결
# 시간복잡도 O(n^3)


def build_cost_matrix(citizens: list, shelters: list, graph_data: dict) -> np.ndarray:
    """
    [자료구조: 2D 비용행렬]
    시민 집단과 대피소 간 이동 비용 행렬 생성.

    Args:
        citizens: [{"id", "loc", "count"}, ...]
        shelters: [{"id", "loc", "capacity", "risk_score", "current_population"}, ...]
        graph_data: 공통 graph_data.json (현 단계 미사용)

    Returns:
        np.ndarray: shape (len(citizens), len(shelters))
    """
    n, m = len(citizens), len(shelters)

    # [자료구조: 2D 비용행렬 (Cost Matrix)]
    dist_mat = np.zeros((n, m))
    risk_mat = np.zeros((n, m))
    cong_mat = np.zeros((n, m))

    for i, c in enumerate(citizens):
        cx, cy = c["loc"]
        for j, s in enumerate(shelters):
            sx, sy = s["loc"]
            dist_mat[i, j] = np.sqrt((cx - sx) ** 2 + (cy - sy) ** 2)
            risk_mat[i, j] = s["risk_score"]
            cap = s["capacity"] if s["capacity"] > 0 else 1
            cong_mat[i, j] = s["current_population"] / cap

    def _normalize_cols(mat: np.ndarray) -> np.ndarray:
        result = mat.copy()
        for j in range(m):
            col_max = mat[:, j].max()
            if col_max > 0:
                result[:, j] /= col_max
        return result

    dist_norm = _normalize_cols(dist_mat)
    risk_norm = _normalize_cols(risk_mat)
    cong_norm = _normalize_cols(cong_mat)

    return dist_norm * 0.5 + risk_norm * 0.3 + cong_norm * 0.2


def _hungarian(cost: list) -> list:
    """
    [알고리즘: 헝가리안 알고리즘 (Hungarian Algorithm)]
    n×m (n <= m) 비용 리스트에서 각 행에 최소 비용 열 배정.
    포텐셜 기반 구현 — O(n · m²), scipy 미사용 순수 Python.
    Returns: assignment[i] = j (0-indexed), 미배정 시 -1
    """
    n = len(cost)
    if n == 0:
        return []
    m = len(cost[0])

    INF = float('inf')
    u = [0.0] * (n + 1)   # 행 포텐셜 (1-indexed)
    v = [0.0] * (m + 1)   # 열 포텐셜 (1-indexed, v[0]=더미)
    p = [0] * (m + 1)     # p[j] = 열 j에 배정된 행(1-indexed), 0=미배정
    way = [0] * (m + 1)   # 증가 경로 역추적

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)

        # 변형 다익스트라로 최단 증가 경로 탐색
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = -1
            for j in range(1, m + 1):
                if not used[j]:
                    # 슬랙: cost[i0][j] - u[i0] - v[j]
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            # 포텐셜 갱신으로 방문한 경로의 슬랙을 0으로 유지
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break

        # 증가 경로를 역추적하며 배정 플립
        while j0:
            p[j0] = p[way[j0]]
            j0 = way[j0]

    assignment = [-1] * n
    for j in range(1, m + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1
    return assignment


def bipartite_matching(cost_matrix: np.ndarray, capacities: list) -> list:
    """
    [알고리즘: 이분 매칭 + 헝가리안]
    비용행렬 기반 최적 배정 수행.

    Args:
        cost_matrix: build_cost_matrix 결과
        capacities: 대피소별 수용 인원 [int, ...]

    Returns:
        list: [(시민_idx, 대피소_idx, 배정인원), ...]

    Raises:
        ValueError: 총 수용량이 시민 수보다 적을 때
    """
    n_citizens = cost_matrix.shape[0]
    total_cap = sum(capacities)

    if total_cap < n_citizens:
        raise ValueError(
            f"총 수용량({total_cap}명)이 시민 수({n_citizens}명)보다 적습니다."
        )

    # [자료구조: 이분 그래프 (Bipartite Graph)]
    # 수용량 처리: 대피소 j를 capacities[j]개 가상 노드로 분할(노드 복제)
    cols = []
    shelter_map = []  # 가상 열 인덱스 → 원래 대피소 인덱스
    for j, cap in enumerate(capacities):
        for _ in range(cap):
            cols.append(cost_matrix[:, j].tolist())
            shelter_map.append(j)

    # (n_citizens × total_cap) 비용 리스트 구성
    expanded = [[cols[col][row] for col in range(total_cap)]
                for row in range(n_citizens)]

    # [알고리즘: 헝가리안 알고리즘 (Hungarian Algorithm)]
    assignment = _hungarian(expanded)

    # [알고리즘: 이분 매칭 (Bipartite Matching)]
    # 가상 열 인덱스를 원래 대피소 인덱스로 역매핑
    results = []
    for c_idx, virtual_col in enumerate(assignment):
        if virtual_col >= 0:
            results.append((c_idx, shelter_map[virtual_col], 1))

    return results


def run():
    st.header("🏠 M1 대피소 수용량 배분")
    st.caption("담당: 김도현 | 알고리즘: 이분 매칭, 헝가리안 | 자료구조: 이분 그래프, 2D 비용행렬")

    # TODO: Streamlit UI 구현
    st.info("구현 중입니다.")
