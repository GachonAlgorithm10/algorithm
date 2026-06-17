# modules/m1_shelter/ui_shelter.py

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.data_loader import DataLoader
from core.map_util import render_module_guide

# [알고리즘: 이분 매칭, 헝가리안 알고리즘]
# [자료구조: 이분 그래프, 2D 비용행렬]
try:
    from .shelter import build_cost_matrix, bipartite_matching
except ImportError:
    from shelter import build_cost_matrix, bipartite_matching

# 한글 폰트 깨짐 방지
plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 기준
plt.rcParams['axes.unicode_minus'] = False

_DUMMY_CITIZENS = [
    {"id": "시민_1", "loc": (10, 10), "count": 1},
    {"id": "시민_2", "loc": (20, 15), "count": 1},
    {"id": "시민_3", "loc": (30, 10), "count": 1},
    {"id": "시민_4", "loc": (15, 25), "count": 1},
    {"id": "시민_5", "loc": (25, 20), "count": 1},
]

_DUMMY_SHELTERS = [
    {"id": "알파_대피소", "loc": (15, 12), "capacity": 2, "risk_score": 1.5, "current_population": 0},
    {"id": "베타_대피소", "loc": (28, 12), "capacity": 3, "risk_score": 0.5, "current_population": 1},
    {"id": "감마_대피소", "loc": (20, 25), "capacity": 2, "risk_score": 2.0, "current_population": 0},
]


def _load_real_data(risk_map: dict):
    """DataLoader에서 실데이터를 로드해 citizens/shelters 리스트로 반환.

    citizens: population_density 상위 20개 노드 (성능 — 헝가리안 O(n³))
    shelters: 전체 shelter 노드
    """
    loader = DataLoader()
    all_nodes = loader.nodes
    shelter_nodes = loader.shelter_nodes

    # 시민 그룹: population_density 내림차순 상위 20개
    sorted_by_pop = sorted(
        [n for n in all_nodes if n.get("population_density", 0) > 0],
        key=lambda n: n.get("population_density", 0),
        reverse=True,
    )[:20]
    citizens = [
        {
            "id": n["id"],
            "loc": (n.get("grid_x", 0), n.get("grid_y", 0)),
            "count": n.get("population_density", 1),
        }
        for n in sorted_by_pop
    ]

    # 대피소: 전체 shelter 노드
    shelters = [
        {
            "id": n["id"],
            "loc": (n.get("grid_x", 0), n.get("grid_y", 0)),
            "capacity": n.get("capacity", 100),
            "risk_score": risk_map.get(n["id"], 0.0),
            "current_population": 0,
        }
        for n in shelter_nodes
    ]

    return citizens, shelters


def run():
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    data_source = st.sidebar.radio(
        "데이터 소스",
        ["실데이터", "더미 데이터"],
        key="m1_data_source",
    )
    use_real = data_source == "실데이터"

    run_btn = st.sidebar.button("▶ 최적 배정 실행", key="shelter_run_btn", type="primary", use_container_width=True)

    if run_btn:
        risk_map = st.session_state.get("risk_map", {})

        if use_real:
            try:
                citizens, shelters = _load_real_data(risk_map)
            except Exception as e:
                st.warning(f"⚠️ 실데이터 로드 실패 — 더미 데이터로 대체합니다. ({e})")
                citizens, shelters = _DUMMY_CITIZENS, _DUMMY_SHELTERS
        else:
            citizens, shelters = _DUMMY_CITIZENS, _DUMMY_SHELTERS

        with st.spinner("헝가리안 알고리즘 연산 중..."):
            # 매칭용 capacity를 1로 고정: 20 시민×158 대피소 → 20×158 행렬로 성능 제한
            # (실 수용량은 cost_matrix의 혼잡도 계산에만 반영)
            capacities = [1] * len(shelters)

            try:
                cost_mat = build_cost_matrix(citizens, shelters, {})
                match_results = bipartite_matching(cost_mat, capacities)

                # M6 호환 dict 형식으로 변환하여 저장
                st.session_state["shelter_assign"] = [
                    {
                        "shelter_id": shelters[s_idx]["id"],
                        "citizen_id": citizens[c_idx]["id"],
                        "count": count,
                    }
                    for c_idx, s_idx, count in match_results
                ]

                result_data = []
                for c_idx, s_idx, count in match_results:
                    c_info = citizens[c_idx]
                    s_info = shelters[s_idx]
                    raw_distance = np.sqrt(
                        (c_info["loc"][0] - s_info["loc"][0]) ** 2 +
                        (c_info["loc"][1] - s_info["loc"][1]) ** 2
                    )
                    result_data.append({
                        "시민 그룹 ID": c_info["id"],
                        "배정 대피소": s_info["id"],
                        "직선 거리": round(raw_distance, 2),
                        "위험도 점수": round(s_info["risk_score"], 4),
                        "대피소 수용량": s_info["capacity"],
                        "최종 배정 비용": round(cost_mat[c_idx][s_idx], 3),
                    })
                df_results = pd.DataFrame(result_data)

                # 시각화: 실데이터는 상위 20 citizens + 상위 10 shelters(위험도 기준)만 scatter
                if use_real:
                    vis_citizens = citizens  # 이미 20개
                    vis_shelters = sorted(shelters, key=lambda s: s["risk_score"], reverse=True)[:10]
                else:
                    vis_citizens = citizens
                    vis_shelters = shelters
                vis_shelter_ids = {s["id"] for s in vis_shelters}

                st.divider()
                st.subheader("📊 결과")
                col1, col2 = st.columns([3, 2])

                with col1:
                    st.subheader("배정 결과 시각화 (Map)")
                    fig, ax = plt.subplots(figsize=(10, 7))

                    first_s = True
                    for s in vis_shelters:
                        ax.scatter(s["loc"][0], s["loc"][1], c='red', marker='s', s=150,
                                   label='대피소' if first_s else "")
                        first_s = False
                        ax.text(s["loc"][0], s["loc"][1] + 1, s["id"], fontsize=7, ha='center')

                    first_c = True
                    for c in vis_citizens:
                        ax.scatter(c["loc"][0], c["loc"][1], c='blue', marker='o', s=80,
                                   label='시민 그룹' if first_c else "")
                        first_c = False
                        ax.text(c["loc"][0], c["loc"][1] - 1.5, c["id"], fontsize=7, ha='center')

                    # 매칭 선: 시각화 대상 대피소에 배정된 시민만 표시
                    for c_idx, s_idx, count in match_results:
                        if shelters[s_idx]["id"] in vis_shelter_ids:
                            c_loc = citizens[c_idx]["loc"]
                            s_loc = shelters[s_idx]["loc"]
                            ax.plot([c_loc[0], s_loc[0]], [c_loc[1], s_loc[1]], 'k--', alpha=0.5)

                    ax.set_title("헝가리안 알고리즘 기반 이분 매칭 결과", pad=20)
                    ax.margins(x=0.1, y=0.15)
                    ax.legend()
                    ax.grid(True, linestyle=':', alpha=0.6)
                    plt.tight_layout()
                    st.pyplot(fig, use_container_width=True)

                with col2:
                    st.subheader("배정 요약")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("시민 그룹", f"{len(citizens)}개")
                    m2.metric("대피소", f"{len(shelters)}곳")
                    match_rate = (len(match_results) / len(citizens) * 100 if citizens else 0.0)
                    st.metric("알고리즘 매칭률", f"{match_rate:.1f}%")
                    st.write("---")
                    st.subheader("상세 배정 분석표")
                    st.dataframe(df_results, use_container_width=True)

            except ValueError as ve:
                st.warning(f"⚠️ 배정 한계 초과: {ve}")
                st.info("💡 시민 수가 대피소 정원보다 많습니다. 대피소를 추가하거나 인원을 조절해주세요.")
            except Exception as e:
                st.error(f"🚨 알고리즘 연산 중 오류 발생: {e}")
    else:
        st.write("")
        st.markdown("#### 📍 송파구 초기 거점 맵")

        from core.map_util import render_status_badge, render_map

        render_status_badge()

        dummy_nodes = {
            "node_001": {"type": "shelter", "lat": 37.512, "lng": 127.102, "name": "송파 제1대피소", "capacity": 150},
            "node_002": {"type": "shelter", "lat": 37.505, "lng": 127.110, "name": "송파 제2대피소", "capacity": 200},
            "node_003": {"type": "hospital", "lat": 37.515, "lng": 127.095, "name": "송파 중앙병원", "capacity": 50}
        }
        render_map(dummy_nodes)

        st.divider()
        render_module_guide("M1")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    run()
