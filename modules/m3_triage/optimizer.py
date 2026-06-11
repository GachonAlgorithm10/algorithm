"""
============================================================
module_m3_triage / optimizer.py
부상자 이송 모듈의 '알고리즘 + 의사결정 로직'
  · 가중합 스코어링 : 누가 의학적으로 더 급한가 (중증도+대기시간)
  · SJF             : 구급차별 운행 순서 (이송시간 짧은 순)
  · 배정/스케줄 파이프라인 진입점 run_triage()
담당: 임성엽
============================================================
설계 원칙 (부품끼리 역할이 겹치지 않게 분리):
  · 점수(가중합)는 '의학적 긴급도'만 판단 → 이송시간 제외
  · 운행 순서(SJF)는 '효율'만 판단 → 이송시간 사용
  → 중증도 우선 '배정' / 운행은 SJF 로 분리해서
    'SJF가 경증 환자를 먼저 처리하는' 트리아지 충돌을 방지.
"""

import random
from dataclasses import dataclass, field

# 패키지로 실행하든(python -m), 폴더 안에서 직접 실행하든 동작하도록
try:
    from .priority_queue import MinPriorityQueue, SegmentTree
except ImportError:
    from priority_queue import MinPriorityQueue, SegmentTree


# ------------------------------------------------------------
# 환자 데이터 모델
# ------------------------------------------------------------
@dataclass
class Patient:
    pid: int
    severity: int        # 중증도 1(경증) ~ 5(중증)
    wait_time: int       # 대기시간(분)
    transport_time: int  # 이송 소요시간(분) — 추후 거리 util에서 공급
    score: float = field(default=0.0)        # 가중합 우선순위 점수
    assigned: str = field(default="")        # 배정된 구급차 id
    trip_order: int = field(default=0)       # 해당 구급차 내 운행 순서


# ------------------------------------------------------------
# [알고리즘: 가중합 스코어링(Weighted Sum Scoring)]
# 의학적 긴급도만 점수화한다. (이송시간은 일부러 제외 → SJF가 담당)
# severity, wait_time 을 0~1로 정규화 후 가중합.
# ------------------------------------------------------------
def compute_scores(patients, w_sev=0.7, w_wait=0.3):
    max_wait = max((p.wait_time for p in patients), default=1) or 1
    for p in patients:
        sev_norm = p.severity / 5.0
        wait_norm = p.wait_time / max_wait
        p.score = w_sev * sev_norm + w_wait * wait_norm
    return patients


# ------------------------------------------------------------
# 배정 단계 : 환자를 구급차에 배정한다.
#   · 일반 구급차 → Min Heap 으로 전체 최우선 환자 추출
#   · 중증 전담   → 세그먼트 트리로 중증도 4~5 구간 최우선 환자 조회
# ------------------------------------------------------------
def assign_patients(patients, ambulances, critical_min_severity=4):
    # 중증도 기준 정렬 (세그먼트 트리의 '구간 = 중증도 범위'를 위해)
    ordered = sorted(patients, key=lambda p: p.severity)
    pos = {p.pid: i for i, p in enumerate(ordered)}  # pid -> 정렬 인덱스
    by_pid = {p.pid: p for p in ordered}

    # 자료구조 구축 (priority_queue.py)
    seg = SegmentTree([p.score for p in ordered])     # 세그먼트 트리
    heap = MinPriorityQueue()                          # 최소 힙
    for p in ordered:
        heap.push(p.score, p.pid)

    # 중증도 4~5에 해당하는 정렬 인덱스 구간 (고정)
    crit_idxs = [i for i, p in enumerate(ordered)
                 if p.severity >= critical_min_severity]
    crit_range = (min(crit_idxs), max(crit_idxs)) if crit_idxs else None

    done = set()  # 이미 배정된 pid

    def pick_general():
        pid = heap.pop_best(done)
        if pid is not None:
            return by_pid[pid]
        # 힙이 비었는데도 미배정자가 남은 예외 상황 대비 폴백
        rest = [p for p in ordered if p.pid not in done]
        return max(rest, key=lambda p: p.score) if rest else None

    # 구급차를 번갈아 가며 한 명씩 배정 (라운드로빈)
    amb_cycle = 0
    while len(done) < len(ordered):
        amb = ambulances[amb_cycle % len(ambulances)]
        amb_cycle += 1
        picked = None

        if amb["type"] == "critical" and crit_range is not None:
            # 세그먼트 트리로 중증도 구간 내 최우선 조회
            score, idx = seg.query(crit_range[0], crit_range[1])
            if idx != -1:
                picked = ordered[idx]

        if picked is None:  # 일반 구급차 또는 중증 구간이 비었을 때
            picked = pick_general()

        if picked is None:
            break  # 더 배정할 환자 없음

        picked.assigned = amb["id"]
        done.add(picked.pid)
        seg.update(pos[picked.pid], -1.0)  # 세그먼트 트리에서 비활성화

    return ordered


# ------------------------------------------------------------
# [알고리즘: SJF 스케줄링(Shortest Job First)]
# 각 구급차에 배정된 환자들의 '운행 순서'를 이송시간 짧은 순으로 정렬.
# 짧은 작업을 먼저 끝내 더 많은 환자를 빨리 이송(처리량 극대화).
# ※ '누구를 태울지(배정)'는 이미 중증도 우선으로 끝났고,
#    여기서는 '태운 사람들을 어떤 동선으로 도느냐'만 정한다.
# ------------------------------------------------------------
def schedule_by_sjf(patients, ambulances):
    for amb in ambulances:
        group = [p for p in patients if p.assigned == amb["id"]]
        group.sort(key=lambda p: p.transport_time)  # SJF
        for order, p in enumerate(group, start=1):
            p.trip_order = order
    return patients


# ------------------------------------------------------------
# 전체 파이프라인 진입점 (app.py / ui_triage.py 에서 호출)
# ------------------------------------------------------------
def run_triage(patients, ambulances, critical_min_severity=4):
    compute_scores(patients)
    patients = assign_patients(patients, ambulances, critical_min_severity)
    patients = schedule_by_sjf(patients, ambulances)
    patients.sort(key=lambda p: (p.assigned, p.trip_order))
    return patients


# ------------------------------------------------------------
# 시뮬레이션 데이터 생성 (단독 실행/테스트용)
#   실제 재난이 아니므로 환자 속성은 난수로 생성한다.
#   transport_time 은 추후 app.py 거리 util(graph_data) 값으로 대체.
# ------------------------------------------------------------
def generate_sample_patients(n=12, seed=42):
    random.seed(seed)
    return [Patient(
        pid=i,
        severity=random.randint(1, 5),
        wait_time=random.randint(0, 60),
        transport_time=random.randint(5, 40),
    ) for i in range(1, n + 1)]


def results_to_rows(patients):
    """st.dataframe 에 바로 넣을 수 있는 dict 리스트로 변환."""
    return [{
        "구급차": p.assigned,
        "운행순서": p.trip_order,
        "환자ID": p.pid,
        "중증도": p.severity,
        "대기(분)": p.wait_time,
        "이송시간(분)": p.transport_time,
        "우선순위점수": round(p.score, 3),
    } for p in patients]


# ------------------------------------------------------------
# 단독 실행 (python -m module_m3_triage.optimizer  또는 폴더 내 직접 실행)
# ------------------------------------------------------------
if __name__ == "__main__":
    ambulances = [
        {"id": "A1", "type": "general"},
        {"id": "A2", "type": "general"},
        {"id": "A3", "type": "critical"},  # 중증도 4~5 전담
    ]
    result = run_triage(generate_sample_patients(n=12), ambulances)

    print("=" * 64)
    print("M3 부상자 이송 우선순위 - 배정/스케줄 결과")
    print("=" * 64)
    print(f"{'구급차':<6}{'순서':<5}{'환자':<5}{'중증도':<6}{'대기':<6}{'이송':<6}{'점수':<8}")
    print("-" * 64)
    for p in result:
        print(f"{p.assigned:<7}{p.trip_order:<6}{p.pid:<6}{p.severity:<7}"
              f"{p.wait_time:<7}{p.transport_time:<7}{round(p.score, 3):<8}")
    print("-" * 64)
    print("일반 구급차(A1,A2): 전체 최우선 환자를 Min Heap으로 추출")
    print("중증 전담(A3)      : 중증도 4~5 구간을 세그먼트 트리로 조회")
    print("각 구급차 운행순서  : SJF(이송시간 짧은 순)")
