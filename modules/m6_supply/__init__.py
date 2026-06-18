# 담당: 임성엽 / GachonAlgorithm10
"""
M6 구호물자 수요 산정 모듈
알고리즘: 그리디 배분 (Greedy Allocation)
자료구조: 우선순위 큐 (Priority Queue)
"""
from .supply import (
    BASIS_DAYS,
    FOOD_PER_PERSON_KG,
    MED_PER_PERSON_UNIT,
    WATER_PER_PERSON_L,
    ShelterDemand,
    calc_demand,
    compute,
    generate_sample_shelter_assign,
    greedy_allocate,
    results_to_rows,
)
from .ui_supply import run

__all__ = [
    "WATER_PER_PERSON_L",
    "FOOD_PER_PERSON_KG",
    "MED_PER_PERSON_UNIT",
    "BASIS_DAYS",
    "ShelterDemand",
    "calc_demand",
    "greedy_allocate",
    "compute",
    "generate_sample_shelter_assign",
    "results_to_rows",
    "render_supply_tab",
    "run",
]
