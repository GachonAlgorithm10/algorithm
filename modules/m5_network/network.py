"""
M5 비상 통신망 설계 모듈
담당: 최의찬
알고리즘: 크루스칼(Kruskal's MST), Tarjan(SPOF 탐지)
자료구조: 그래프(Graph), Union-Find(Disjoint Set Union)
"""
import streamlit as st
import networkx as nx

# [자료구조: 그래프 (Graph)]
# 통신 거점(노드) + 연결선(엣지)으로 구성된 무방향 가중치 그래프
# networkx.Graph 또는 인접 리스트 딕셔너리로 표현

# [자료구조: Union-Find (Disjoint Set Union)]
# 크루스칼 MST에서 사이클 판별에 사용
# parent[], rank[] 배열로 구현. find(x) / union(x, y) 연산

# [알고리즘: 크루스칼 알고리즘 (Kruskal's MST)]
# 엣지를 가중치 오름차순 정렬 후 사이클 없이 선택 → 최소신장트리 생성
# 최소 비용으로 모든 거점을 연결하는 통신망 설계

# [알고리즘: Tarjan 알고리즘 (SPOF 탐지 — 단절점 탐색)]
# DFS 기반. 제거 시 그래프가 분리되는 단절점(Single Point of Failure) 탐지
# 통신망에서 복구 우선 거점 식별에 활용


# Union-Find 구현
class UnionFind:
    """
    [자료구조: Union-Find (Disjoint Set Union)]
    크루스칼 MST 사이클 판별용.
    """
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 경로 압축
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """합집합. 이미 같은 집합이면 False(사이클) 반환."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def kruskal_mst(nodes: list, edges: list) -> list:
    """
    [알고리즘: 크루스칼 알고리즘]
    [자료구조: Union-Find]
    최소신장트리(MST) 엣지 목록 반환.

    Args:
        nodes: ["node_001", "node_002", ...]
        edges: [{"from": str, "to": str, "weight": float}, ...]

    Returns:
        list: MST에 포함된 엣지 목록 [{"from", "to", "weight"}, ...]
    """
    node_idx = {node: i for i, node in enumerate(nodes)}
    uf = UnionFind(len(nodes))

    # [알고리즘: 크루스칼] 가중치 오름차순 정렬
    sorted_edges = sorted(edges, key=lambda e: e["weight"])

    mst_edges = []
    for edge in sorted_edges:
        u = node_idx[edge["from"]]
        v = node_idx[edge["to"]]
        if uf.union(u, v):          # 사이클 없으면 MST에 추가
            mst_edges.append(edge)

    return mst_edges


def tarjan_spof(nodes: list, edges: list) -> list:
    """
    [알고리즘: Tarjan 알고리즘 — 단절점(SPOF) 탐지]
    DFS로 단절점(Article Point) 탐색.

    Args:
        nodes: 노드 id 목록
        edges: 엣지 목록

    Returns:
        list: 단절점(SPOF)인 노드 id 목록
    """
    # networkx를 활용하거나 직접 DFS 구현
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for e in edges:
        G.add_edge(e["from"], e["to"], weight=e["weight"])

    # TODO: Tarjan 단절점 탐색 직접 구현
    #   (networkx articulation_points는 참고용 — 실제 구현은 DFS로)
    spof_nodes = list(nx.articulation_points(G))
    return spof_nodes


def run():
    st.header("📡 M5 비상 통신망 설계")
    st.caption(
        "담당: 최의찬 | "
        "알고리즘: 크루스칼(MST), Tarjan(SPOF 탐지) | "
        "자료구조: 그래프, Union-Find"
    )

    # TODO: Streamlit UI 구현
    st.info("구현 중입니다.")
