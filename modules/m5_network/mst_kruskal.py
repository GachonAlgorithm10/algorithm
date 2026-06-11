"""
============================================================
module_m5_network / mst_kruskal.py
비상 통신망 설계 모듈의 MST 생성 로직
  · Union-Find 자료구조 : 사이클 여부 검사
  · 크루스칼 알고리즘   : 최소 비용 복구 통신망 구축
담당: 최의찬
============================================================
"""

def node_to_xy(node_id, grid_width=60):
    """
    M2 격자 매핑 기준:
    node_id = y * 60 + x
    """
    x = node_id % grid_width
    y = node_id // grid_width
    return f"({x}, {y})"


# ------------------------------------------------------------
# [자료구조: 유니온-파인드(Union-Find)]
# 각 통신 거점이 어떤 연결 집합에 속하는지 관리한다.
# 크루스칼 알고리즘에서 간선을 추가할 때 사이클 발생 여부를 검사한다.
# ------------------------------------------------------------
class UnionFind:
    def __init__(self, nodes):
        self.parent = {}
        self.rank = {}

        for node in nodes:
            self.parent[node] = node
            self.rank[node] = 0

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])

        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b
        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a
        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1

        return True


# ------------------------------------------------------------
# [알고리즘: 크루스칼 알고리즘(Kruskal)]
# 복구 비용이 낮은 간선부터 선택하여 전체 통신 거점을 최소 비용으로 연결한다.
# 사이클이 생기는 간선은 Union-Find를 이용해 제외한다.
# ------------------------------------------------------------
def build_mst(nodes, edges):
    uf = UnionFind(nodes)

    # 복구 비용 기준 오름차순 정렬
    sorted_edges = sorted(edges, key=lambda edge: edge[2])

    mst_edges = []
    total_cost = 0

    for u, v, cost in sorted_edges:
        if uf.union(u, v):
            mst_edges.append((u, v, cost))
            total_cost += cost

    is_connected = len(mst_edges) == len(nodes) - 1

    return mst_edges, total_cost, is_connected


def edge_rows(edges, grid_width=60):
    """Streamlit 표 출력용 데이터로 변환한다."""
    rows = []

    for u, v, cost in edges:
        rows.append({
            "출발 node_id": u,
            "출발 좌표": node_to_xy(u, grid_width),
            "도착 node_id": v,
            "도착 좌표": node_to_xy(v, grid_width),
            "복구 비용": cost,
        })

    return rows


# ------------------------------------------------------------
# 단독 실행 테스트
# ------------------------------------------------------------
if __name__ == "__main__":
    nodes = [1830, 1831, 1890, 1891, 1950, 1951]

    edges = [
        (1830, 1831, 4),
        (1830, 1890, 2),
        (1831, 1890, 1),
        (1831, 1891, 5),
        (1890, 1891, 8),
        (1890, 1950, 10),
        (1891, 1950, 2),
        (1891, 1951, 6),
        (1950, 1951, 3),
    ]

    mst_edges, total_cost, is_connected = build_mst(nodes, edges)

    print("=" * 64)
    print("M5 비상 통신망 설계 - MST 결과")
    print("=" * 64)
    print("선택된 복구 간선:", mst_edges)
    print("총 복구 비용:", total_cost)
    print("전체 연결 여부:", is_connected)