# modules_m1_shelter/shelter.py

import numpy as np
from scipy.optimize import linear_sum_assignment

# 재난 유형 및 상황에 따라 조절 가능한 시스템 가중치 상수
WEIGHT_DISTANCE = 0.5
WEIGHT_RISK = 0.3
WEIGHT_CONGESTION = 0.2

def build_cost_matrix(citizens: list, shelters: list, graph_data: dict) -> np.ndarray:

    n, m = len(citizens), len(shelters)
    cost_matrix = np.zeros((n, m))

    # graph_data "nodes" 탐색 후 {"노드ID": (lat, lng)} 딕셔너리 생성
    node_coords = {}
    if graph_data and "nodes" in graph_data:
        for node in graph_data["nodes"]:
            node_coords[str(node["id"])] = (node.get("lat", 0), node.get("lng", 0))

    # 실제 거리 계산
    raw_dist = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            # 시민 및 대피소 노드 ID 추출
            node_c = str(citizens[i].get('location_node', ''))
            node_s = str(shelters[j].get('location_node', ''))

            # 데이터 존재 시 위경도 기반 직선 거리 계산
            if node_c in node_coords and node_s in node_coords:
                lat1, lng1 = node_coords[node_c]
                lat2, lng2 = node_coords[node_s]
                raw_dist[i][j] = np.sqrt((lat1 - lat2)**2 + (lng1 - lng2)**2)
            else:
                # 데이터 부재 시 UI 테스트용 임시 좌표 사용
                loc_c = citizens[i].get('loc', (0,0))
                loc_s = shelters[j].get('loc', (0,0))
                raw_dist[i][j] = np.sqrt((loc_c[0] - loc_s[0])**2 + (loc_c[1] - loc_s[1])**2)

    # 최대 거리 기준 0~1 정규화
    max_dist = np.max(raw_dist) if np.max(raw_dist) > 0 else 1.0

    # 최대 위험도 기준 0~1 정규화
    raw_risks = [s.get('risk_score', 0) for s in shelters]
    max_risk = max(raw_risks) if raw_risks and max(raw_risks) > 0 else 1.0

    # 2차원 비용 행렬 생성
    for i in range(n):
        for j in range(m):
            s = shelters[j]
            norm_dist = raw_dist[i][j] / max_dist
            safe_risk = s.get('risk_score', 0) / max_risk
            
            capacity = s.get('capacity', 1)
            current_pop = s.get('current_population', 0)
            
            # 혼잡도 페널티 계산
            # 대피소 정원(capacity)이 0 이하일 때 발생하는 에러 방지
            if capacity <= 0:   
                occupancy_penalty = 2.0

            #(현재 인원이 정원보다 많으면 2.0, 아니면 (현재인원/정원)으로 계산해 변수에 저장)
            else:
                occupancy_penalty = 2.0 if current_pop >= capacity else current_pop / capacity

            # 가중치 반영: (거리*0.5) + (위험도*0.3) + (혼잡도*0.2)
            cost_matrix[i][j] = (WEIGHT_DISTANCE * norm_dist) + \
                                (WEIGHT_RISK * safe_risk) + \
                                (WEIGHT_CONGESTION * (occupancy_penalty / 2)) # occupancy_penalty는 최대 2.0이므로 다른 변수들과 0~1 스케일을 맞추기 위해 / 2 적용

    return cost_matrix

def bipartite_matching(cost_matrix: np.ndarray, capacities: list) -> list:
 
    n, m = cost_matrix.shape
    total_capacity = sum(capacities)

    # 예외 처리: 수용 불가
    if n > total_capacity:
        raise ValueError(f" 수용량 부족: 시민({n}명) > 대피소 정원({total_capacity}명)")

    # [자료구조: 이분 그래프용 노드 리스트]
    # 노드 복제 (대피소를 capacity만큼 복제해 1:1로 풀기)
    expanded_cost_matrix = np.zeros((n, total_capacity))
    slot_to_shelter_map = [] # 복제된 슬롯이 원래 몇 번 대피소인지 기억하는 리스트

    col_idx = 0
    for j in range(m):
        cap = capacities[j]
        for core_idx in range(cap):
            slot_to_shelter_map.append(j)
            
            # 슬롯 페널티 (배정 순서가 뒤로 갈수록 가중치 추가)
            slot_penalty = core_idx / cap if cap > 0 else 0
            extra_congestion_cost = WEIGHT_CONGESTION * (slot_penalty / 2)

            # N명의 시민 행렬에 복제된 열 추가
            for i in range(n):
                expanded_cost_matrix[i][col_idx] = cost_matrix[i][j] + extra_congestion_cost
            col_idx += 1

    # [알고리즘: 헝가리안 알고리즘]
    # 헝가리안 알고리즘 실행
    row_ind, col_ind = linear_sum_assignment(expanded_cost_matrix)

    result = []
    # 결과 매핑: (시민 인덱스, 원래 대피소 인덱스, 배정 인원 1명)
    for r, c in zip(row_ind, col_ind):
        original_shelter_idx = slot_to_shelter_map[c]
        result.append((r, original_shelter_idx, 1))

    return result