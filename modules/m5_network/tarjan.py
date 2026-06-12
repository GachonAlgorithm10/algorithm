"""
============================================================
module_m5_network / tarjan.py
비상 통신망 설계 모듈의 단일 장애점 탐지 로직
  · 그래프 자료구조       : 통신 거점과 연결 관계 표현
  · Tarjan 알고리즘       : 단절점(SPOF) 탐지
담당: 최의찬
============================================================
"""

try:
    from .mst_kruskal import node_to_xy
except ImportError:
    from mst_kruskal import node_to_xy


# ------------------------------------------------------------
# [자료구조: 그래프(Graph)]
# 통신 거점을 노드로, 복구 연결을 간선으로 표현한다.
# 무방향 그래프이므로 u → v, v → u 양쪽에 모두 저장한다.
# ------------------------------------------------------------
def make_graph(nodes, edges):
    graph = {}

    for node in nodes:
        graph[node] = []

    for edge in edges:
        u = edge[0]
        v = edge[1]

        graph[u].append(v)
        graph[v].append(u)

    return graph


# ------------------------------------------------------------
# [알고리즘: Tarjan 단절점 탐지]
# 특정 노드 하나가 제거되었을 때 통신망이 분리되는지 확인한다.
# 재난 상황에서는 이런 노드를 SPOF(Single Point Of Failure)로 본다.
# 대규모 그래프에서 RecursionError를 방지하기 위해 명시적 스택 기반 반복 DFS로 구현한다.
# ------------------------------------------------------------
def find_articulation_points(nodes, edges):
    graph = make_graph(nodes, edges)

    # 방문 순서(discovery time), low값, 부모 노드 초기화
    disc = {node: -1 for node in nodes}
    low = {node: -1 for node in nodes}
    parent = {node: None for node in nodes}
    result = set()
    timer = [0]

    for start in nodes:
        if disc[start] != -1:
            continue

        # [자료구조: 스택(Stack)] — 반복 DFS용 명시적 스택
        # 각 항목: (현재 노드, 이웃 노드 반복자, 루트 자식 수)
        stack = [(start, iter(graph[start]), [0])]
        disc[start] = low[start] = timer[0]
        timer[0] += 1

        while stack:
            node, children, child_count = stack[-1]

            advanced = False
            for neighbor in children:
                if disc[neighbor] == -1:
                    # 미방문 이웃 → 스택에 push (DFS 진입)
                    parent[neighbor] = node
                    child_count[0] += 1
                    disc[neighbor] = low[neighbor] = timer[0]
                    timer[0] += 1
                    stack.append((neighbor, iter(graph[neighbor]), [0]))
                    advanced = True
                    break
                elif neighbor != parent[node]:
                    # 이미 방문한 조상 → low값 갱신
                    low[node] = min(low[node], disc[neighbor])

            if not advanced:
                # 현재 노드의 모든 이웃 탐색 완료 → 스택에서 pop (DFS 복귀)
                stack.pop()
                if stack:
                    par_node = stack[-1][0]

                    # 복귀 시 부모 노드의 low값 갱신
                    low[par_node] = min(low[par_node], low[node])

                    # 단절점 판별
                    # 루트 노드: DFS 자식이 2개 이상이면 단절점
                    if parent[par_node] is None and stack[-1][2][0] > 1:
                        result.add(par_node)

                    # 루트가 아닌 노드: 자식이 조상으로 돌아갈 수 없으면 단절점
                    if parent[par_node] is not None and low[node] >= disc[par_node]:
                        result.add(par_node)

    return sorted(list(result))


def spof_rows(spof_nodes, grid_width=60):
    """Streamlit 표 출력용 데이터로 변환한다."""
    rows = []

    for node in spof_nodes:
        rows.append({
            "단일 장애점 node_id": node,
            "격자 좌표": node_to_xy(node, grid_width),
            "위험 설명": "해당 거점 장애 시 통신망 분리 가능",
        })

    return rows


# ------------------------------------------------------------
# 단독 실행 테스트
# ------------------------------------------------------------
if __name__ == "__main__":
    nodes = [1830, 1831, 1890, 1891, 1950, 1951]

    mst_edges = [
        (1831, 1890, 1),
        (1830, 1890, 2),
        (1891, 1950, 2),
        (1950, 1951, 3),
        (1831, 1891, 5),
    ]

    spof_nodes = find_articulation_points(nodes, mst_edges)

    print("=" * 64)
    print("M5 비상 통신망 설계 - SPOF 탐지 결과")
    print("=" * 64)
    print("단일 장애점:", spof_nodes)