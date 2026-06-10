"""
============================================================
data/distance_util.py
graph_data.json 기반 거리/이송시간 계산 유틸리티
담당: 임성엽 (app.py 통합용)
============================================================
[역할]
M3(부상자 이송)·M1(대피소 배분)에서 필요한 '이송시간(분)'을
graph_data.json의 도로망을 기반으로 계산해서 제공한다.

[사용 방법]
from data.distance_util import DistanceUtil

util = DistanceUtil("data/graph_data.json")
minutes = util.transport_minutes("node_001", "node_002")

[M3 연결 방법]
generate_sample_patients() 대신 실제 데이터를 넣을 때:
    for patient in patients:
        patient.transport_time = util.transport_minutes(
            patient.location_node, nearest_hospital_node
        )
============================================================
"""

import json
import heapq
from typing import Optional


# 구급차 평균 이동 속도 (km/h). 실제 운용 기준: 도심 40~60 km/h.
# 재난 상황 가중치를 고려해 보수적으로 설정.
AMBULANCE_SPEED_KMH = 40.0


class DistanceUtil:
    def __init__(self, graph_data_path: str = "data/graph_data.json"):
        """
        graph_data.json을 로드하고 인접 리스트를 구축한다.
        나하림의 preprocess.py 결과물을 그대로 받는다.
        """
        with open(graph_data_path, "r", encoding="utf-8") as f:
            self.graph_data = json.load(f)

        # [자료구조: 인접 리스트 딕셔너리 (Adjacency List)]
        # {node_id: [(neighbor_id, distance_km), ...]}
        self.adj: dict[str, list[tuple[str, float]]] = {}
        for node in self.graph_data["nodes"]:
            self.adj[node["id"]] = []
        for edge in self.graph_data["edges"]:
            u, v, d = edge["from"], edge["to"], edge["distance"]
            self.adj[u].append((v, d))
            self.adj[v].append((u, d))  # 양방향

    def shortest_distance_km(
        self, start: str, end: str
    ) -> Optional[float]:
        """
        Dijkstra 알고리즘으로 start → end 최단 거리(km) 반환.
        경로가 없으면 None 반환.

        [알고리즘: 다익스트라(Dijkstra) — 최단 경로 탐색]
        [자료구조: 최소 힙(Min Heap) — 미방문 노드 중 최소 거리 추출]
        ※ 본 함수는 app.py 통합 유틸리티용이며,
          모듈별 고유 알고리즘(M1/M2/M3/M5) 배정과는 별개임.
        """
        if start not in self.adj or end not in self.adj:
            return None
        if start == end:
            return 0.0

        # 최소 힙: (거리, 노드id)
        heap = [(0.0, start)]
        dist: dict[str, float] = {start: 0.0}

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, float("inf")):
                continue
            if u == end:
                return d
            for v, w in self.adj.get(u, []):
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))

        return None  # 경로 없음

    def transport_minutes(
        self,
        start: str,
        end: str,
        speed_kmh: float = AMBULANCE_SPEED_KMH,
        fallback_minutes: int = 30,
    ) -> int:
        """
        start → end 이송 소요시간(분, 정수) 반환.
        경로가 없으면 fallback_minutes 반환.

        Args:
            start: 출발 노드 id
            end:   도착 노드 id
            speed_kmh:        구급차 이동 속도 (기본 40 km/h)
            fallback_minutes: 경로 없을 때 기본값 (기본 30분)
        Returns:
            int: 이송 소요시간(분)
        """
        km = self.shortest_distance_km(start, end)
        if km is None:
            return fallback_minutes
        minutes = (km / speed_kmh) * 60
        return max(1, round(minutes))

    def get_nodes_by_type(self, node_type: str) -> list[dict]:
        """
        type 기준으로 노드 필터링.
        예: get_nodes_by_type("hospital") → 병원 노드 목록
        M3에서 '가장 가까운 병원' 탐색에 활용.
        """
        return [
            n for n in self.graph_data["nodes"]
            if n.get("type") == node_type
        ]

    def nearest_node(
        self, start: str, node_type: str
    ) -> Optional[tuple[str, int]]:
        """
        start에서 가장 가까운 특정 타입 노드를 반환.
        Returns: (node_id, transport_minutes) 또는 None
        """
        candidates = self.get_nodes_by_type(node_type)
        best = None
        best_time = float("inf")
        for node in candidates:
            nid = node["id"]
            if nid == start:
                continue
            t = self.transport_minutes(start, nid)
            if t < best_time:
                best_time = t
                best = nid
        return (best, int(best_time)) if best else None


# ------------------------------------------------------------
# 단독 실행 테스트 (python -m data.distance_util)
# graph_data.json의 샘플 노드 기준으로 동작 확인
# ------------------------------------------------------------
if __name__ == "__main__":
    import os

    # 샘플 graph_data.json이 없으면 인메모리로 생성
    SAMPLE_PATH = "data/graph_data.json"
    if not os.path.exists(SAMPLE_PATH):
        import tempfile, json as _json
        sample = {
            "nodes": [
                {"id": "node_001", "name": "중구 대피소 A",  "type": "shelter",  "lat": 37.5636, "lng": 126.9976, "capacity": 200},
                {"id": "node_002", "name": "중구 병원 B",    "type": "hospital", "lat": 37.5600, "lng": 127.0010, "capacity": 80},
                {"id": "node_003", "name": "중구 통신 허브", "type": "hub",      "lat": 37.5580, "lng": 126.9950, "capacity": 0},
            ],
            "edges": [
                {"from": "node_001", "to": "node_002", "distance": 0.8, "weight": 0.8},
                {"from": "node_002", "to": "node_003", "distance": 1.2, "weight": 1.2},
                {"from": "node_001", "to": "node_003", "distance": 1.5, "weight": 1.5},
            ],
            "grid_mapping": {}
        }
        os.makedirs("data", exist_ok=True)
        with open(SAMPLE_PATH, "w", encoding="utf-8") as f:
            _json.dump(sample, f, ensure_ascii=False, indent=2)
        print("[테스트] 샘플 graph_data.json 생성")

    util = DistanceUtil(SAMPLE_PATH)

    print("=" * 50)
    print("distance_util 동작 테스트")
    print("=" * 50)

    pairs = [
        ("node_001", "node_002"),
        ("node_001", "node_003"),
        ("node_002", "node_003"),
    ]
    for s, e in pairs:
        km = util.shortest_distance_km(s, e)
        mins = util.transport_minutes(s, e)
        print(f"{s} → {e} : {km:.1f} km / {mins} 분")

    print()
    result = util.nearest_node("node_001", "hospital")
    if result:
        print(f"node_001 에서 가장 가까운 병원: {result[0]} ({result[1]}분)")
