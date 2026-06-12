# 담당: 임성엽 / GachonAlgorithm10
"""
core/data_loader.py — 그래프·부가 데이터 로드 및 session_state 초기화
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import streamlit as st

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
EDGE_DISTANCE_MIN_KM = 0.05

# ---------------------------------------------------------------------------
# session_state 기본값
# ---------------------------------------------------------------------------
SESSION_STATE_DEFAULTS: dict = {
    "risk_map": {},        # {node_id: float 0~1}  — M2 생성
    "shelter_assign": [],  # [{citizen_grp, shelter_id, count}]  — M1 생성
    "transport_order": [], # [{patient_id, priority, eta}]  — M3 생성
    "resource_assign": [], # [{vol_id, site_id, cost}]  — M4 생성
    "supply_demand": {},   # {shelter_id: {water, food, med}}  — M6 생성
    "network_plan": {},    # {mst_edges: [], spof_nodes: []}  — M5 생성
    "budget_plan": [],     # [{zone_id, allocated, effect}]  — M7 생성
}

# [자료구조: 딕셔너리 / 리스트 — session_state 키-값 저장소]
def init_session_state() -> None:
    """이미 값이 있는 키는 덮어쓰지 않는다. app.py 최상단에서 1회 호출."""
    for key, default in SESSION_STATE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


# ---------------------------------------------------------------------------
# DataLoader
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).resolve().parent.parent  # repository root


class DataLoader:
    def __init__(self, processed_dir: Optional[str] = None) -> None:
        self._dir = Path(processed_dir) if processed_dir else _BASE_DIR / "data" / "processed"
        self._cache: dict = {}

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------
    def _load_json(self, path: Path) -> dict | list:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _clamp_edges(self, data: dict) -> dict:
        for edge in data.get("edges", []):
            if edge.get("distance", 1) <= 0:
                edge["distance"] = EDGE_DISTANCE_MIN_KM
        return data

    # ------------------------------------------------------------------
    # graph_data
    # ------------------------------------------------------------------
    @property
    def graph_data(self) -> dict:
        if "graph_data" in self._cache:
            return self._cache["graph_data"]

        processed_path = self._dir / "graph_data.json"
        fallback_path = _BASE_DIR / "data" / "graph_data.json"

        if processed_path.exists():
            data = self._load_json(processed_path)
        elif fallback_path.exists():
            data = self._load_json(fallback_path)
        else:
            raise FileNotFoundError(
                f"[DATA-01] graph_data.json not found in {processed_path} or {fallback_path}"
            )

        self._clamp_edges(data)
        self._cache["graph_data"] = data
        return data

    @property
    def nodes(self) -> list:
        return self.graph_data["nodes"]

    @property
    def edges(self) -> list:
        return self.graph_data["edges"]

    @property
    def shelter_nodes(self) -> list:
        return [n for n in self.nodes if n.get("type") == "shelter"]

    @property
    def hospital_nodes(self) -> list:
        return [n for n in self.nodes if n.get("type") == "hospital"]

    @property
    def simulation_settings(self) -> dict:
        defaults = {"grid_width": 60, "grid_height": 60, "cell_size_m": 100}
        return {**defaults, **self.graph_data.get("simulation_settings", {})}

    @property
    def grid_mapping(self) -> dict:
        raw = self.graph_data.get("grid_mapping", {})
        return {k: v for k, v in raw.items() if k != "_comment"}

    # ------------------------------------------------------------------
    # 노드 조회
    # ------------------------------------------------------------------
    def get_node_by_id(self, node_id: str) -> Optional[dict]:
        for node in self.nodes:
            if node.get("id") == node_id:
                return node
        return None

    def get_risk(self, node_id: str, default: float = 0.0) -> float:
        return st.session_state.get("risk_map", {}).get(node_id, default)

    # ------------------------------------------------------------------
    # 부가 데이터 프로퍼티 (FileNotFoundError → DATA-02)
    # ------------------------------------------------------------------
    def _load_processed(self, filename: str) -> dict | list:
        path = self._dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"[DATA-02] {filename} not found: {path}"
            )
        return self._load_json(path)

    @property
    def patients(self) -> list:
        if "patients" not in self._cache:
            data = self._load_processed("patients.json")
            self._cache["patients"] = data["patients"] if isinstance(data, dict) else data
        return self._cache["patients"]

    @property
    def volunteers(self) -> list:
        if "volunteers" not in self._cache:
            data = self._load_processed("volunteers.json")
            self._cache["volunteers"] = data["volunteers"] if isinstance(data, dict) else data
        return self._cache["volunteers"]

    @property
    def supplies(self) -> dict | list:
        if "supplies" not in self._cache:
            data = self._load_processed("supplies.json")
            if isinstance(data, dict):
                data = {k: v for k, v in data.items() if k != "_comment"}
            self._cache["supplies"] = data
        return self._cache["supplies"]

    @property
    def damage_zones(self) -> list:
        if "damage_zones" not in self._cache:
            data = self._load_processed("damage_zones.json")
            self._cache["damage_zones"] = data["damage_zones"] if isinstance(data, dict) else data
        return self._cache["damage_zones"]


# ---------------------------------------------------------------------------
# 싱글턴
# ---------------------------------------------------------------------------
_loader_instance: Optional[DataLoader] = None


def get_loader() -> DataLoader:
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DataLoader()
    return _loader_instance


# ---------------------------------------------------------------------------
# 단독 실행
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    loader = DataLoader()
    try:
        gd = loader.graph_data
        print(f"노드 수: {len(loader.nodes)}")
        print(f"엣지 수: {len(loader.edges)}")
    except FileNotFoundError as e:
        print(f"경고: {e}")
