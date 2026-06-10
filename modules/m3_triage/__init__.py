"""
============================================================
modules.m3_triage  (M3 · 부상자 이송 우선순위 결정)
담당: 임성엽 / GachonAlgorithm10
============================================================
구성:
  priority_queue.py — 자료구조: Min Heap, 세그먼트 트리
  optimizer.py      — 알고리즘: 가중합 스코어링, SJF
  ui_triage.py      — Streamlit 화면

app.py 통합 규약:
  from modules import m3_triage
  m3_triage.run()
"""

from .optimizer import (
    Patient,
    run_triage,
    compute_scores,
    assign_patients,
    schedule_by_sjf,
    generate_sample_patients,
    results_to_rows,
)
from .priority_queue import MinPriorityQueue, SegmentTree
from .ui_triage import render_triage_tab


def run():
    """app.py의 M3 탭 진입점."""
    render_triage_tab()


__all__ = [
    "Patient",
    "run_triage",
    "compute_scores",
    "assign_patients",
    "schedule_by_sjf",
    "generate_sample_patients",
    "results_to_rows",
    "MinPriorityQueue",
    "SegmentTree",
    "render_triage_tab",
    "run",
]
