"""
============================================================
module_m5_network  (M5 · 비상 통신망 설계)
담당: 최의찬 / GachonAlgorithm10
============================================================
구성:
  mst_kruskal.py  — 자료구조: Union-Find / 알고리즘: 크루스칼 MST
  tarjan.py       — 자료구조: 그래프 / 알고리즘: Tarjan 단절점 탐지
  ui_network.py   — Streamlit 화면

app.py 통합 규약:
  from modules import m5_network
  m5_network.run()
"""

from .mst_kruskal import node_to_xy, UnionFind, build_mst, edge_rows
from .tarjan import make_graph, find_articulation_points, spof_rows
from .ui_network import render_network_tab, generate_sample_network, run

__all__ = [
    "node_to_xy",
    "UnionFind",
    "build_mst",
    "edge_rows",
    "make_graph",
    "find_articulation_points",
    "spof_rows",
    "render_network_tab",
    "generate_sample_network",
    "run",
]
