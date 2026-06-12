"""
============================================================
modules.m1_shelter  (M1 · 대피소 수용량 배분)
담당: 김도현 / GachonAlgorithm10
============================================================
구성:
  shelter.py    — 알고리즘: 이분 매칭, 헝가리안 / 자료구조: 이분 그래프, 2D 비용행렬
  ui_shelter.py — Streamlit 화면

app.py 통합 규약:
  from modules import m1_shelter
  m1_shelter.run()
"""

from .shelter import build_cost_matrix, bipartite_matching
from .ui_shelter import run

__all__ = [
    "build_cost_matrix",
    "bipartite_matching",
    "run",
]
