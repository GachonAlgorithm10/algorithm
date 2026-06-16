"""
============================================================
modules.m2_spread  (M2 · 위험 구역 확산 예측)
담당: 나하림 / GachonAlgorithm10
============================================================
구성:
  bfs_spread.py      — 알고리즘: BFS 확산 모델 / 자료구조: 2D 격자, 큐
  cellular_automata.py — 알고리즘: 셀룰러 오토마타
  ui_spread.py       — Streamlit 화면

app.py 통합 규약:
  from modules import m2_spread
  m2_spread.run()
"""

from .ui_spread import run

__all__ = ["run"]
