# 담당: 임성엽 / GachonAlgorithm10
# 데이터 출처: WHO 재난 표준 (water 3L/인/일, food 0.6kg/인/일, med 0.1unit/인)
# 데이터 출처: M1 출력 shelter_assign (대피소별 배정 인원)
"""
M6 구호물자 수요 산정 — 그리디 배분 알고리즘
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass

import numpy as np

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
WATER_PER_PERSON_L: float = 3.0
FOOD_PER_PERSON_KG: float = 0.6
MED_PER_PERSON_UNIT: float = 0.1
BASIS_DAYS: int = 3


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class ShelterDemand:
    shelter_id: str
    population: int
    risk: float
    need_water_L: float = 0.0
    need_food_kg: float = 0.0
    need_med: float = 0.0
    alloc_water_L: float = 0.0
    alloc_food_kg: float = 0.0
    alloc_med: float = 0.0

    @property
    def priority_score(self) -> float:
        return self.risk * 0.6 + min(self.population / 1000, 1.0) * 0.4


# ---------------------------------------------------------------------------
# 수요 계산
# ---------------------------------------------------------------------------

def calc_demand(shelter: ShelterDemand) -> ShelterDemand:
    shelter.need_water_L = shelter.population * WATER_PER_PERSON_L * BASIS_DAYS
    shelter.need_food_kg = shelter.population * FOOD_PER_PERSON_KG * BASIS_DAYS
    shelter.need_med = shelter.population * MED_PER_PERSON_UNIT
    return shelter


# ---------------------------------------------------------------------------
# 그리디 배분
# ---------------------------------------------------------------------------

def greedy_allocate(
    shelters: list[ShelterDemand],
    stock_water_L: float,
    stock_food_kg: float,
    stock_med: float,
) -> list[ShelterDemand]:
    # [자료구조: 우선순위 큐 (Priority Queue)]
    # (-priority_score, index) — 최대 힙을 최소 힙으로 구현
    heap: list[tuple[float, int]] = []
    for idx, s in enumerate(shelters):
        heapq.heappush(heap, (-s.priority_score, idx))

    remaining_water = stock_water_L
    remaining_food = stock_food_kg
    remaining_med = stock_med

    # [알고리즘: 그리디 배분 (Greedy Allocation)]
    # 우선순위 높은 대피소부터 재고를 소진될 때까지 배분
    while heap:
        if remaining_water <= 0 and remaining_food <= 0 and remaining_med <= 0:
            break

        _, idx = heapq.heappop(heap)
        s = shelters[idx]

        s.alloc_water_L = min(s.need_water_L, remaining_water)
        s.alloc_food_kg = min(s.need_food_kg, remaining_food)
        s.alloc_med = min(s.need_med, remaining_med)

        remaining_water -= s.alloc_water_L
        remaining_food -= s.alloc_food_kg
        remaining_med -= s.alloc_med

    return shelters


# ---------------------------------------------------------------------------
# compute
# ---------------------------------------------------------------------------

def compute(data: dict, params: dict) -> dict:
    shelter_assign: list = data.get("shelter_assign", [])
    graph_nodes: list = data.get("graph_nodes", [])
    risk_map: dict = data.get("risk_map", {})
    supplies_raw: dict = data.get("supplies", {})

    stock = supplies_raw.get(
        "current_stock",
        supplies_raw.get(
            "total_stock",
            {"water_L": 500_000, "food_kg": 80_000, "med_unit": 20_000},
        ),
    )
    stock_water = float(stock.get("water_L", 500_000))
    stock_food = float(stock.get("food_kg", 80_000))
    stock_med = float(stock.get("med_unit", 20_000))

    # 대피소별 인원 집계
    # NOTE: M1(김도현)이 shelter_assign을 {"shelter_id":..., "count":...} dict 형식으로
    # 저장하기 전까지의 임시 방어 코드. 근본 수정은 M1 측에서 진행 필요.
    pop_map: dict[str, int] = {}
    for entry in shelter_assign:
        if isinstance(entry, dict):
            sid = entry.get("shelter_id", "")
            count = int(entry.get("count", 0))
        elif isinstance(entry, (tuple, list)) and len(entry) >= 3:
            # M1 미수정 버전 호환: (citizen_idx, shelter_idx, count)
            # shelter_idx만으로는 shelter_id를 알 수 없으므로 건너뜀
            continue
        else:
            continue
        pop_map[sid] = pop_map.get(sid, 0) + count

    # shelter_assign 비어있으면 graph_nodes에서 더미 인원 생성
    if not pop_map:
        for node in graph_nodes:
            if node.get("type") == "shelter":
                nid = node.get("id", "")
                pop_map[nid] = int(node.get("population_density", 0) * 0.05)

    shelters: list[ShelterDemand] = []
    for sid, pop in pop_map.items():
        risk = risk_map.get(sid, 0.0)
        sd = ShelterDemand(shelter_id=sid, population=pop, risk=risk)
        calc_demand(sd)
        shelters.append(sd)

    shelters = greedy_allocate(shelters, stock_water, stock_food, stock_med)

    supply_demand: dict = {}
    for s in shelters:
        supply_demand[s.shelter_id] = {
            "population": s.population,
            "risk": round(s.risk, 4),
            "priority": round(s.priority_score, 4),
            "need_water_L": round(s.need_water_L, 1),
            "need_food_kg": round(s.need_food_kg, 1),
            "need_med": round(s.need_med, 1),
            "alloc_water_L": round(s.alloc_water_L, 1),
            "alloc_food_kg": round(s.alloc_food_kg, 1),
            "alloc_med": round(s.alloc_med, 1),
        }

    total_need_water = round(sum(s.need_water_L for s in shelters), 1)
    total_need_food = round(sum(s.need_food_kg for s in shelters), 1)
    total_need_med = round(sum(s.need_med for s in shelters), 1)
    total_alloc_water = round(sum(s.alloc_water_L for s in shelters), 1)
    total_alloc_food = round(sum(s.alloc_food_kg for s in shelters), 1)
    total_alloc_med = round(sum(s.alloc_med for s in shelters), 1)

    return {
        "supply_demand": supply_demand,
        "total_need": {
            "water_L": total_need_water,
            "food_kg": total_need_food,
            "med": total_need_med,
        },
        "total_alloc": {
            "water_L": total_alloc_water,
            "food_kg": total_alloc_food,
            "med": total_alloc_med,
        },
        "shortage": {
            "water_L": round(max(0.0, total_need_water - total_alloc_water), 1),
            "food_kg": round(max(0.0, total_need_food - total_alloc_food), 1),
            "med": round(max(0.0, total_need_med - total_alloc_med), 1),
        },
    }


# ---------------------------------------------------------------------------
# 샘플 생성 / 결과 변환
# ---------------------------------------------------------------------------

def generate_sample_shelter_assign(n: int = 8, seed: int = 42) -> list[dict]:
    rng = np.random.default_rng(seed)
    node_pool = [f"node_{i:03d}" for i in range(1, 11)]
    return [
        {
            "shelter_id": node_pool[int(rng.integers(0, len(node_pool)))],
            "count": int(rng.integers(50, 501)),
        }
        for _ in range(n)
    ]


def results_to_rows(supply_demand_dict: dict) -> list[dict]:
    rows = [
        {
            "대피소": sid,
            "배정인원": v["population"],
            "위험도": v["risk"],
            "우선순위": v["priority"],
            "필요(물,L)": v["need_water_L"],
            "필요(식량,kg)": v["need_food_kg"],
            "필요(의약품)": v["need_med"],
            "배분(물,L)": v["alloc_water_L"],
            "배분(식량,kg)": v["alloc_food_kg"],
            "배분(의약품)": v["alloc_med"],
        }
        for sid, v in supply_demand_dict.items()
    ]
    return sorted(rows, key=lambda r: r["우선순위"], reverse=True)


# ---------------------------------------------------------------------------
# 단독 실행
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_assign = generate_sample_shelter_assign(n=8, seed=42)
    result = compute(data={"shelter_assign": sample_assign}, params={})
    print("=== 총 수요 ===")
    print(result["total_need"])
    print("=== 총 배분 ===")
    print(result["total_alloc"])
    print("=== 부족분 ===")
    print(result["shortage"])
    print("=== 대피소별 ===")
    for row in results_to_rows(result["supply_demand"]):
        print(row)
