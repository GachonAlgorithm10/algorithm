# 담당: 임성엽 / GachonAlgorithm10
# 데이터 출처: 송파구 피해 구역 더미 데이터 (damage_zones.json, 나하림 DATA-02)
# 데이터 출처: M2 risk_map (위험도 → 복구 효과 가중치)
"""
M7 복구 예산 최적 배분 — 0-1 배낭 문제 DP
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
BUDGET_UNIT_KRW: int = 100  # 1 unit = 100만 원


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class DamageZone:
    zone_id: str
    node_id: str
    damage_area_m2: int
    repair_cost_million: int
    base_effect: int
    risk: float = 0.0

    @property
    def weighted_effect(self) -> int:
        return round(self.base_effect * (1.0 + self.risk))

    @property
    def cost_units(self) -> int:
        return max(1, round(self.repair_cost_million / BUDGET_UNIT_KRW))


# ---------------------------------------------------------------------------
# 0-1 배낭 DP
# ---------------------------------------------------------------------------

def knapsack_dp(
    zones: list[DamageZone], budget_million: int
) -> tuple[int, list[DamageZone]]:
    n = len(zones)
    W = max(1, round(budget_million / BUDGET_UNIT_KRW))

    # [자료구조: 2D DP 테이블]
    # dp[i][w]: 첫 i개 구역에서 예산 w unit 이하로 얻는 최대 효과
    dp: list[list[int]] = [[0] * (W + 1) for _ in range(n + 1)]
    keep: list[list[bool]] = [[False] * (W + 1) for _ in range(n + 1)]

    # [알고리즘: 0-1 배낭 문제 (0-1 Knapsack DP)]
    for i in range(1, n + 1):
        z = zones[i - 1]
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]
            keep[i][w] = False
            if z.cost_units <= w:
                candidate = dp[i - 1][w - z.cost_units] + z.weighted_effect
                if candidate > dp[i][w]:
                    dp[i][w] = candidate
                    keep[i][w] = True

    # 역추적: keep 테이블로 선택된 구역 복원
    selected: list[DamageZone] = []
    w = W
    for i in range(n, 0, -1):
        if keep[i][w]:
            selected.append(zones[i - 1])
            w -= zones[i - 1].cost_units
    selected.reverse()

    return dp[n][W], selected


# ---------------------------------------------------------------------------
# compute
# ---------------------------------------------------------------------------

def compute(data: dict, params: dict) -> dict:
    zones_raw: list = data.get("damage_zones", [])
    risk_map: dict = data.get("risk_map", {})
    budget_million: int = int(params.get("budget_million", 5000))

    zones: list[DamageZone] = [
        DamageZone(
            zone_id=z.get("zone_id", f"zone_{idx:03d}"),
            node_id=z.get("node_id", ""),
            damage_area_m2=int(z.get("damage_area_m2", 0)),
            repair_cost_million=int(z.get("repair_cost_million", 100)),
            base_effect=int(z.get("base_effect", z.get("repair_effect_score", 10))),
            risk=float(risk_map.get(z.get("node_id", ""), 0.0)),
        )
        for idx, z in enumerate(zones_raw)
    ]

    if not zones:
        return {
            "selected_zones": [],
            "total_cost": 0,
            "total_effect": 0,
            "budget_used": 0,
            "budget_remain": budget_million,
        }

    total_effect, selected = knapsack_dp(zones, budget_million)
    selected_ids = {z.zone_id for z in selected}

    selected_zones = [
        {
            "zone_id": z.zone_id,
            "node_id": z.node_id,
            "cost": z.repair_cost_million,
            "base_effect": z.base_effect,
            "risk": round(z.risk, 4),
            "effect": z.weighted_effect,
            "selected": z.zone_id in selected_ids,
        }
        for z in zones
    ]

    total_cost = sum(z.repair_cost_million for z in selected)

    return {
        "selected_zones": selected_zones,
        "total_cost": total_cost,
        "total_effect": total_effect,
        "budget_used": total_cost,
        "budget_remain": max(0, budget_million - total_cost),
    }


# ---------------------------------------------------------------------------
# 샘플 생성 / 결과 변환
# ---------------------------------------------------------------------------

def generate_sample_zones(n: int = 15, seed: int = 42) -> list[dict]:
    rng = np.random.default_rng(seed)
    return [
        {
            "zone_id": f"zone_{i + 1:03d}",
            "node_id": f"node_{int(rng.integers(1, 21)):03d}",
            "damage_area_m2": int(rng.integers(500, 5001)),
            "repair_cost_million": int(rng.integers(50, 1001)),
            "base_effect": int(rng.integers(10, 101)),
        }
        for i in range(n)
    ]


def results_to_rows(result: dict) -> list[dict]:
    rows = [
        {
            "선택": "✅" if z["selected"] else "—",
            "구역ID": z["zone_id"],
            "노드": z["node_id"],
            "복구비용(백만)": z["cost"],
            "위험도": z["risk"],
            "기본효과": z["base_effect"],
            "실효효과": z["effect"],
            "_sel": z["selected"],
        }
        for z in result["selected_zones"]
    ]
    rows.sort(key=lambda r: (not r["_sel"], -r["실효효과"]))
    for r in rows:
        del r["_sel"]
    return rows


# ---------------------------------------------------------------------------
# 단독 실행
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_zones = generate_sample_zones(n=15, seed=42)
    risk_map = {f"node_{i:03d}": round(i * 0.05, 2) for i in range(1, 21)}

    result = compute(
        data={"damage_zones": sample_zones, "risk_map": risk_map},
        params={"budget_million": 3000},
    )
    print(f"선택 구역 수 : {sum(1 for z in result['selected_zones'] if z['selected'])}")
    print(f"예산 사용    : {result['budget_used']} 백만 원")
    print(f"예산 잔여    : {result['budget_remain']} 백만 원")
    print(f"총 복구 효과 : {result['total_effect']}")
    print()
    _sym = {"✅": "[O]", "—": "[-]"}
    for row in results_to_rows(result):
        print({k: _sym.get(v, v) for k, v in row.items()})
