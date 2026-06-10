"""
============================================================
module_m3_triage / priority_queue.py
부상자 이송 모듈에서 쓰는 '자료구조' 모음
  · Min Heap (최소 힙)      : 전체에서 최우선 환자 추출
  · 세그먼트 트리            : 중증도 구간 내 최우선 환자 조회
담당: 임성엽
============================================================
"""

import heapq


# ------------------------------------------------------------
# [자료구조: 최소 힙(Min Heap)]
# heapq는 최소 힙이므로 점수에 -1을 곱해 넣어 '최대 우선순위 추출'로 활용.
# 이미 배정된 환자(done)는 꺼낼 때 건너뛰는 지연 삭제(lazy deletion) 방식.
# ------------------------------------------------------------
class MinPriorityQueue:
    def __init__(self):
        self._heap = []

    def push(self, score, pid):
        heapq.heappush(self._heap, (-score, pid))

    def pop_best(self, done):
        """done에 없는 최우선 환자 pid를 반환. 없으면 None."""
        while self._heap:
            neg_score, pid = heapq.heappop(self._heap)
            if pid not in done:
                return pid
        return None

    def __len__(self):
        return len(self._heap)


# ------------------------------------------------------------
# [자료구조: 세그먼트 트리(Segment Tree)]
# 중증도 순으로 정렬된 환자 배열에 대해 '구간 최대 우선순위 점수'를
# O(log n)에 조회한다. 특정 중증도 구간만 담당하는 중증 전담 구급차가
# 해당 구간 내 최우선 환자를 빠르게 찾기 위해 사용.
# (단일 최우선 환자 추출은 Min Heap이, 구간 조회는 세그먼트 트리가 담당)
# ------------------------------------------------------------
class SegmentTree:
    def __init__(self, scores):
        self.n = len(scores)
        self.size = 1
        while self.size < max(self.n, 1):
            self.size *= 2
        # 각 노드: (점수, 원본 인덱스). 비어있으면 (-1, -1)
        self.tree = [(-1.0, -1)] * (2 * self.size)
        for i, s in enumerate(scores):
            self.tree[self.size + i] = (s, i)
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = max(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, idx, value):
        # 환자가 이미 배정되면 -1로 비활성화
        i = self.size + idx
        self.tree[i] = (value, idx)
        i //= 2
        while i >= 1:
            self.tree[i] = max(self.tree[2 * i], self.tree[2 * i + 1])
            i //= 2

    def query(self, lo, hi):
        # [lo, hi] 폐구간 내 최대 점수와 그 인덱스 반환
        res = (-1.0, -1)
        lo += self.size
        hi += self.size + 1
        while lo < hi:
            if lo & 1:
                res = max(res, self.tree[lo]); lo += 1
            if hi & 1:
                hi -= 1; res = max(res, self.tree[hi])
            lo //= 2; hi //= 2
        return res
