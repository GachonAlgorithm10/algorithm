# module_m2_spread/bfs_spread.py
import json
import numpy as np
from collections import deque


class BFSFireSpread:

    def __init__(self, graph_data_path):
        """[자료구조] JSON 그래프 데이터를 로드하여 2D 격자(Grid) 공간으로 추상화"""
        with open(graph_data_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

        self.width = self.raw_data["simulation_settings"]["grid_width"]
        self.height = self.raw_data["simulation_settings"]["grid_height"]

        # 2D 인구 밀도 매트릭스 초기화 (60x60)
        self.population_matrix = np.zeros((self.height, self.width))

        # [수정 1] 노드 ID -> (grid_x, grid_y) 명시적 매핑 테이블 생성
        # 기존에는 run_bfs 안에서 id % width, id // width 로 좌표를 "추론"했는데,
        # 이는 JSON의 노드 ID가 0부터 빠짐없이 row-major로 부여되어 있다는 가정이 깨지면
        # 시작점이 완전히 틀린 좌표로 잡히는 문제가 있었음.
        # 이미 population_matrix를 채울 때 grid_x/grid_y를 읽고 있으므로,
        # 같은 루프에서 id -> 좌표 딕셔너리도 함께 만들어 직접 조회하도록 변경.
        self.id_to_coord = {}
        for node in self.raw_data["nodes"]:
            x, y = node["grid_x"], node["grid_y"]
            self.population_matrix[y, x] = node["population_density"]
            self.id_to_coord[node["id"]] = (x, y)

    def run_bfs(self, start_node_id, max_time=15):
        """[알고리즘] 큐(Queue) 기반 확산 시뮬레이션 (SPFA 방식의 BFS 확장)

        ※ 셀 간 확산 속도가 인구밀도에 따라 0.2 / 1.0으로 달라지는 가중치 그래프이므로,
          단순 BFS만으로는 최단 도달 시간이 보장되지 않음. 그래서 이미 방문한 셀이라도
          더 빠른 경로가 발견되면 갱신 후 재투입하는 SPFA(큐 기반 Bellman-Ford) 방식으로
          동작하도록 구현되어 있음 (아래 [버그 수정 1], [버그 수정 2] 부분).
        """
        # [수정 1] id_to_coord에서 직접 좌표 조회 (id 연산 추론 제거)
        if start_node_id not in self.id_to_coord:
            raise ValueError(f"존재하지 않는 노드 ID: {start_node_id}")
        start_x, start_y = self.id_to_coord[start_node_id]

        # -1.0은 아직 불길이 도달하지 않은 안전 구역을 의미
        fire_map = np.full((self.height, self.width), -1.0, dtype=float)

        # BFS 구현을 위한 큐(Queue) 선언: (현재_y, 현재_x, 도달_시간)
        queue = deque([(start_y, start_x, 0.0)])
        fire_map[start_y, start_x] = 0.0

        # 대각선 포함 상하좌우 8방향 탐색 오프셋
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        while queue:
            curr_y, curr_x, curr_t = queue.popleft()

            # [버그 수정 1] 큐에서 나온 값이 그사이 더 짧은 경로로 갱신되었다면 이전 쓰레기 값은 패스
            if curr_t > fire_map[curr_y, curr_x]:
                continue

            for dy, dx in directions:
                next_y, next_x = curr_y + dy, curr_x + dx

                # 격자 경계선 내부 검사
                if 0 <= next_y < self.height and 0 <= next_x < self.width:
                    pop_weight = self.population_matrix[next_y, next_x]

                    # [가중치 부여] 인구 밀집 구역은 확산 속도 가속(0.2초 추가), 공터는 일반 확산(1.0초 추가)
                    speed_weight = 0.2 if pop_weight > 0 else 1.0
                    next_t = curr_t + speed_weight

                    # [버그 수정 1] 제한 시간을 넘는 확산은 애초에 큐에 넣지 않음
                    if next_t > max_time:
                        continue

                    # [버그 수정 2] 아직 방문 안 했거나(-1.0), 새로 계산한 도달 시간(next_t)이 기존 도달 시간보다 더 빠른 경우 갱신
                    if fire_map[next_y, next_x] == -1.0 or next_t < fire_map[next_y, next_x]:
                        fire_map[next_y, next_x] = next_t
                        queue.append((next_y, next_x, next_t))

        return fire_map

    def to_hazard_level(self, fire_map, current_time, max_time=15):
        """[수정 2 - 모듈 연결] BFS 결과(연속 도달 시간)를 CA 모듈이 쓰는
        이산 위험 단계(0~3)로 변환. CellularAutomataModel.cellular_automata_step()의
        초기 입력(current_grid)으로 바로 넘길 수 있는 형태를 만들어,
        BFS 출력과 CA 입력 사이의 빈 연결 고리를 채움.

        - 미도달(-1.0): 0단계 (안전)
        - 도달 직후: 1단계
        - 도달 후 일정 시간 경과: 2단계
        - 도달 후 충분히 오래 경과(또는 발화점 인근): 3단계
        """
        hazard = np.zeros_like(fire_map, dtype=int)

        reached = fire_map >= 0
        elapsed = current_time - fire_map  # 불이 도달한 후 얼마나 지났는지

        hazard[reached] = 1
        hazard[reached & (elapsed >= max_time * 0.3)] = 2
        hazard[reached & (elapsed >= max_time * 0.6)] = 3

        return hazard
