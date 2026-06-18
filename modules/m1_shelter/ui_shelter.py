# modules/m1_shelter/ui_shelter.py

import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

from core.data_loader import DataLoader, get_loader
from core.map_util import render_module_guide

# [알고리즘: 이분 매칭, 헝가리안 알고리즘]
# [자료구조: 이분 그래프, 2D 비용행렬]
try:
    from .shelter import build_cost_matrix, bipartite_matching
except ImportError:
    from shelter import build_cost_matrix, bipartite_matching

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


def _build_assignment_map(match_results, citizens, shelters, node_lookup):
    """시민 그룹 → 배정 대피소 연결선을 송파구 지도에 표시."""
    m = folium.Map(location=[37.505, 127.115], zoom_start=13, tiles="cartodbpositron")
    drawn = set()
    for c_idx, s_idx, count in match_results:
        cid, sid = citizens[c_idx]["id"], shelters[s_idx]["id"]
        cn, sn = node_lookup.get(cid), node_lookup.get(sid)
        if not cn or not sn:
            continue
        folium.PolyLine([[cn["lat"], cn["lng"]], [sn["lat"], sn["lng"]]],
                        color="#4C8BF5", weight=1.5, opacity=0.55, dash_array="4").add_to(m)
        folium.CircleMarker([cn["lat"], cn["lng"]], radius=5, color="#1971C2",
                            fill=True, fill_opacity=0.9,
                            popup=folium.Popup(f"시민 그룹<br>위치: {cn.get('name', cid)}<br>인원: {count}", max_width=250)).add_to(m)
        if sid not in drawn:
            cap = shelters[s_idx].get("capacity", 0)
            folium.Marker([sn["lat"], sn["lng"]],
                          icon=folium.Icon(color="red", icon="home", prefix="fa"),
                          popup=folium.Popup(f"대피소: {sn.get('name', sid)}<br>수용량: {cap:,}명", max_width=250)).add_to(m)
            drawn.add(sid)
    return m


def run():
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    use_real = True

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

                match_rate = (len(match_results) / len(citizens) * 100 if citizens else 0.0)
                used_shelters = len({shelters[s_idx]["id"] for _, s_idx, _ in match_results})

                st.divider()
                st.subheader("📊 결과")
                st.success(
                    f"✅ {len(citizens)}개 시민 그룹을 {used_shelters}개 대피소에 배정 완료 "
                    f"(매칭률 {match_rate:.0f}%). 지도의 파란 선은 각 그룹이 이동해야 할 대피소를 가리킵니다."
                )

                if use_real:
                    node_lookup = {n["id"]: n for n in get_loader().nodes}
                    fmap = _build_assignment_map(match_results, citizens, shelters, node_lookup)
                    st_folium(fmap, use_container_width=True, height=520, returned_objects=[])
                else:
                    st.info("더미 모드는 실제 좌표가 없어 지도를 생략합니다. 아래 표에서 배정 결과를 확인하세요.")

                k1, k2, k3 = st.columns(3)
                k1.metric("시민 그룹", f"{len(citizens)} 개")
                k2.metric("배정 대피소", f"{used_shelters} 곳")
                k3.metric("알고리즘 매칭률", f"{match_rate:.1f}%")

                with st.expander("📋 상세 배정 분석표"):
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
