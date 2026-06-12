# 담당: 임성엽 / GachonAlgorithm10
"""
M4 구조자원 배치 모듈 — 헝가리안 알고리즘 기반 자원-현장 최적 배치
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# 헝가리안 알고리즘 — import 시도 후 인라인 fallback
# ---------------------------------------------------------------------------
# [알고리즘: 헝가리안 알고리즘 (Hungarian Algorithm)]
# [자료구조: 이분 그래프 (Bipartite Graph)]
# [자료구조: 2D 비용행렬 (Cost Matrix)]

try:
    from modules.m1_shelter.shelter import _hungarian
except Exception:
    try:
        from ..m1_shelter.shelter import _hungarian
    except Exception:
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


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class Resource:
    rid: str
    rtype: str
    skill: str
    location_node: str
    assigned_site: str = ""
    cost: float = 0.0


@dataclass
class Site:
    site_id: str
    node_id: str
    risk: float
    demand: int
    location: tuple


# ---------------------------------------------------------------------------
# 비용 행렬 구성
# ---------------------------------------------------------------------------

def _extract_node_num(node_id: str) -> Optional[int]:
    try:
        return int(node_id.replace("node_", ""))
    except (ValueError, AttributeError):
        return None


def _get_preferred_skills(site_id: str) -> list:
    if site_id.startswith("search_rescue"):
        return ["search_rescue", "first_aid"]
    elif site_id.startswith("first_aid"):
        return ["first_aid", "search_rescue"]
    elif site_id.startswith("heavy"):
        return ["heavy_equipment"]
    return []


def _normalize_cols(mat: np.ndarray) -> np.ndarray:
    result = mat.copy().astype(float)
    for j in range(mat.shape[1]):
        col_max = mat[:, j].max()
        if col_max > 0:
            result[:, j] /= col_max
    return result


def build_resource_cost_matrix(
    resources: list[Resource], sites: list[Site]
) -> np.ndarray:
    """
    [자료구조: 2D 비용행렬 (Cost Matrix)]
    shape: (len(resources), len(sites))
    최종: dist_norm×0.5 + risk_norm×0.3 + skill_norm×0.2
    """
    n, m = len(resources), len(sites)
    dist_mat = np.zeros((n, m), dtype=float)
    risk_mat = np.zeros((n, m), dtype=float)
    skill_mat = np.zeros((n, m), dtype=float)

    for i, res in enumerate(resources):
        r_num = _extract_node_num(res.location_node)
        for j, site in enumerate(sites):
            s_num = _extract_node_num(site.node_id)
            if r_num is not None and s_num is not None:
                dist_mat[i, j] = abs(r_num - s_num)
            else:
                dist_mat[i, j] = abs(site.location[0] - site.location[1])

            risk_mat[i, j] = 1.0 - site.risk

            preferred = _get_preferred_skills(site.site_id)
            skill_mat[i, j] = 0.0 if (not preferred or res.skill in preferred) else 1.0

    dist_norm = _normalize_cols(dist_mat)
    risk_norm = _normalize_cols(risk_mat)
    skill_norm = _normalize_cols(skill_mat)

    return dist_norm * 0.5 + risk_norm * 0.3 + skill_norm * 0.2


# ---------------------------------------------------------------------------
# 배정
# ---------------------------------------------------------------------------

def assign_resources(
    resources: list[Resource],
    sites: list[Site],
    cost_matrix: np.ndarray,
) -> list[Resource]:
    """
    [알고리즘: 헝가리안 알고리즘 (Hungarian Algorithm)]
    [자료구조: 이분 그래프 (Bipartite Graph)]
    각 site를 demand만큼 가상 슬롯으로 복제 후 최적 배정 수행.
    """
    # [자료구조: 이분 그래프 (Bipartite Graph)]
    # demand 기반 슬롯 복제 — site_map[slot] = 원래 site 인덱스
    site_map: list[int] = []
    for j, site in enumerate(sites):
        for _ in range(site.demand):
            site_map.append(j)

    total_slots = len(site_map)
    if total_slots == 0:
        return resources

    n_res = len(resources)

    # n <= m 조건 충족: 슬롯보다 자원이 많으면 dummy 슬롯(고비용) 추가
    dummy_slots = max(0, n_res - total_slots)
    DUMMY_COST = 1e9

    # [자료구조: 2D 비용행렬 (Cost Matrix)]
    expanded: list[list[float]] = []
    for i in range(n_res):
        row = [float(cost_matrix[i, site_map[k]]) for k in range(total_slots)]
        row += [DUMMY_COST] * dummy_slots
        expanded.append(row)

    # [알고리즘: 헝가리안 알고리즘 (Hungarian Algorithm)]
    assignment = _hungarian(expanded)

    for i, res in enumerate(resources):
        slot = assignment[i] if i < len(assignment) else -1
        if 0 <= slot < total_slots:
            j = site_map[slot]
            res.assigned_site = sites[j].site_id
            res.cost = float(cost_matrix[i, j])

    return resources


# ---------------------------------------------------------------------------
# compute
# ---------------------------------------------------------------------------

def compute(data: dict, params: dict) -> dict:
    volunteers_raw: list = data.get("volunteers", [])
    graph_nodes: list = data.get("graph_nodes", [])
    risk_map: dict = data.get("risk_map", {})
    n_sites: int = params.get("n_sites", 5)

    resources = [
        Resource(
            rid=v.get("id", f"vol_{idx:03d}"),
            rtype=v.get("type", "volunteer"),
            skill=v.get("skill", ""),
            location_node=v.get("node_id", "node_001"),
        )
        for idx, v in enumerate(volunteers_raw)
    ]

    if risk_map:
        sorted_nodes = sorted(
            graph_nodes,
            key=lambda n: risk_map.get(n.get("id", ""), 0.0),
            reverse=True,
        )
        selected = sorted_nodes[:n_sites]
    else:
        selected = graph_nodes[:n_sites]

    sites = [
        Site(
            site_id=f"site_{node.get('id', f'node_{idx:03d}')}",
            node_id=node.get("id", f"node_{idx:03d}"),
            risk=risk_map.get(node.get("id", ""), 0.5),
            demand=1,
            location=(node.get("grid_x", idx), node.get("grid_y", idx)),
        )
        for idx, node in enumerate(selected)
    ]

    if not resources or not sites:
        return {
            "assignments": [],
            "total_cost": 0.0,
            "unassigned": [r.rid for r in resources],
        }

    cost_matrix = build_resource_cost_matrix(resources, sites)
    assign_resources(resources, sites, cost_matrix)

    assignments = []
    unassigned = []
    for r in resources:
        if r.assigned_site:
            assignments.append({
                "resource_id": r.rid,
                "resource_type": r.rtype,
                "skill": r.skill,
                "site_id": r.assigned_site,
                "cost": r.cost,
            })
        else:
            unassigned.append(r.rid)

    total_cost = sum(a["cost"] for a in assignments)
    return {"assignments": assignments, "total_cost": total_cost, "unassigned": unassigned}


# ---------------------------------------------------------------------------
# 샘플 생성 / 결과 변환
# ---------------------------------------------------------------------------

def generate_sample_resources(n: int = 10, seed: int = 42) -> list[Resource]:
    rng = np.random.default_rng(seed)
    skills = ["first_aid", "search_rescue", "heavy_equipment", "logistics"]
    return [
        Resource(
            rid=f"vol_{i + 1:03d}",
            rtype="volunteer",
            skill=skills[int(rng.integers(0, len(skills)))],
            location_node=f"node_{int(rng.integers(1, 20)):03d}",
        )
        for i in range(n)
    ]


def generate_sample_sites(n: int = 4, seed: int = 7) -> list[Site]:
    rng = np.random.default_rng(seed)
    return [
        Site(
            site_id=f"site_{i + 1:03d}",
            node_id=f"node_{int(rng.integers(1, 20)):03d}",
            risk=float(rng.uniform(0.2, 1.0)),
            demand=int(rng.integers(1, 4)),
            location=(int(rng.integers(0, 60)), int(rng.integers(0, 60))),
        )
        for i in range(n)
    ]


def results_to_rows(resources: list[Resource]) -> list[dict]:
    return [
        {
            "자원ID": r.rid,
            "유형": r.rtype,
            "스킬": r.skill,
            "출발노드": r.location_node,
            "배정현장": r.assigned_site or "-",
            "배치비용": round(r.cost, 4),
        }
        for r in resources
    ]


# ---------------------------------------------------------------------------
# 단독 실행
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _resources = generate_sample_resources(n=10, seed=42)
    _sites = generate_sample_sites(n=4, seed=7)
    _cost_matrix = build_resource_cost_matrix(_resources, _sites)
    _assigned = assign_resources(_resources, _sites, _cost_matrix)

    print(f"자원 수: {len(_assigned)}")
    for _row in results_to_rows(_assigned):
        print(_row)
