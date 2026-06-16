# module_m2_spread/cellular_automata.py
import numpy as np


class CellularAutomataModel:

    def __init__(self, width=60, height=60):
        self.width = width
        self.height = height

    def cellular_automata_step(self, current_grid: np.ndarray, wind_dir="무풍") -> np.ndarray:
        """
        [알고리즘] 셀룰러 오토마타(CA) 규칙 기반 다음 단계 격자 상태 계산
        - 이웃 셀들의 위험도(바람 가중치 반영) 평균이 임계값(Threshold)을 초과하면 현재 셀의 위험도 상승
        """
        # CA의 기본: 이전 단계 격자를 복사하여 '다음 단계 격자'를 새로 만듦 (동시성 확보)
        next_grid = current_grid.copy()

        # 8방향 이웃 오프셋 (Moore 이웃)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),      # 상하좌우
            (-1, -1), (-1, 1), (1, -1), (1, 1)     # 대각선
        ]

        # [전이 규칙] 바람 방향에 따른 이웃 영향도 가중치 설정 (기본값 1.0)
        # [수정 3] 기존에는 북풍/남풍만 대각선 이웃까지 가중치를 올려주고
        # 서풍/동풍은 정면 이웃만 올려서 방향별로 비대칭이었음.
        # 4방향 모두 같은 규칙(정면 2.0, 양쪽 대각선 1.5)으로 통일.
        wind_weights = {d: 1.0 for d in directions}
        if wind_dir == "북풍":
            wind_weights[(-1, 0)] = 2.0
            wind_weights[(-1, -1)] = 1.5
            wind_weights[(-1, 1)] = 1.5
        elif wind_dir == "남풍":
            wind_weights[(1, 0)] = 2.0
            wind_weights[(1, -1)] = 1.5
            wind_weights[(1, 1)] = 1.5
        elif wind_dir == "서풍":
            wind_weights[(0, -1)] = 2.0
            wind_weights[(-1, -1)] = 1.5
            wind_weights[(1, -1)] = 1.5
        elif wind_dir == "동풍":
            wind_weights[(0, 1)] = 2.0
            wind_weights[(-1, 1)] = 1.5
            wind_weights[(1, 1)] = 1.5

        # 임계값 설정 (이웃 위험도 가중 평균이 이 값을 넘으면 전파 시작)
        THRESHOLD = 1.2

        # [수정 4] 경계/모서리 셀은 유효 이웃 수가 적어(3개, 5개) 같은 가중합이라도
        # 평균값이 더 크게 나와 임계값을 쉽게 넘던 "경계 효과" 문제가 있었음.
        # 항상 8로 나누어 정규화하고, 격자 밖은 위험도 0인 셀로 취급(=합산에 영향 없음).
        FIXED_NEIGHBOR_COUNT = 8

        # 전 격자 순회 (주변 이웃을 보고 '내' 상태를 결정하는 역방향 연산)
        for y in range(self.height):
            for x in range(self.width):
                # 이미 최고 재난 단계(3)인 셀은 계산 생략
                if current_grid[y, x] >= 3:
                    continue

                neighbor_sum = 0.0

                for dy, dx in directions:
                    ny, nx = y + dy, x + dx

                    # 격자 경계선 내부 검사 (밖이면 위험도 0으로 간주 -> 합산에 더하지 않음)
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        neighbor_hazard = current_grid[ny, nx]
                        weight = wind_weights.get((dy, dx), 1.0)
                        neighbor_sum += neighbor_hazard * weight

                # 항상 고정된 이웃 수(8)로 나누어 경계/내부 셀 간 평균 기준을 동일하게 맞춤
                neighbor_average = neighbor_sum / FIXED_NEIGHBOR_COUNT

                # [상태 전이 규칙] 이웃의 평균 위험도가 임계값을 넘으면 내 위험도 1단계 상승
                if neighbor_average >= THRESHOLD:
                    next_grid[y, x] = min(current_grid[y, x] + 1, 3)

        return next_grid
