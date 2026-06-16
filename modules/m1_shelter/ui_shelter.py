# modules/m1_shelter/ui_shelter.py

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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


def run():
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    # UI 테스트용 가상 데이터 세팅 (시민 5명, 대피소 3곳)
    dummy_citizens = [
        {"id": "시민_1", "loc": (10, 10), "count": 1},
        {"id": "시민_2", "loc": (20, 15), "count": 1},
        {"id": "시민_3", "loc": (30, 10), "count": 1},
        {"id": "시민_4", "loc": (15, 25), "count": 1},
        {"id": "시민_5", "loc": (25, 20), "count": 1}
    ]

    dummy_shelters = [
        {"id": "알파_대피소", "loc": (15, 12), "capacity": 2, "risk_score": 1.5, "current_population": 0},
        {"id": "베타_대피소", "loc": (28, 12), "capacity": 3, "risk_score": 0.5, "current_population": 1},
        {"id": "감마_대피소", "loc": (20, 25), "capacity": 2, "risk_score": 2.0, "current_population": 0}
    ]

    run_btn = st.sidebar.button("▶ 최적 배정 실행", key="shelter_run_btn", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("헝가리안 알고리즘 연산 중..."):
            capacities = [s["capacity"] for s in dummy_shelters]

            try:
                # [알고리즘: 헝가리안 알고리즘] 비용 행렬 생성 후 최적 배정
                cost_mat = build_cost_matrix(dummy_citizens, dummy_shelters, {})
                match_results = bipartite_matching(cost_mat, capacities)

                st.session_state["shelter_assign"] = match_results

                result_data = []
                for c_idx, s_idx, count in match_results:
                    c_info = dummy_citizens[c_idx]
                    s_info = dummy_shelters[s_idx]
                    raw_distance = np.sqrt(
                        (c_info["loc"][0] - s_info["loc"][0])**2 +
                        (c_info["loc"][1] - s_info["loc"][1])**2
                    )
                    result_data.append({
                        "시민 ID": c_info["id"],
                        "배정 대피소": s_info["id"],
                        "직선 거리": round(raw_distance, 2),
                        "위험도 점수": s_info["risk_score"],
                        "대피소 상태": f"{s_info['current_population']}/{s_info['capacity']} 명",
                        "최종 배정 비용": round(cost_mat[c_idx][s_idx], 3)
                    })
                df_results = pd.DataFrame(result_data)

                st.divider()
                st.subheader("📊 결과")
                col1, col2 = st.columns([3, 2])

                with col1:
                    st.subheader("배정 결과 시각화 (Map)")
                    fig, ax = plt.subplots(figsize=(10, 7))

                    for s in dummy_shelters:
                        ax.scatter(s["loc"][0], s["loc"][1], c='red', marker='s', s=150,
                                   label='대피소' if s["id"] == "알파_대피소" else "")
                        ax.text(s["loc"][0], s["loc"][1]+1,
                                f"{s['id']}\n(수용:{s['capacity']}명)", fontsize=9, ha='center')

                    for c in dummy_citizens:
                        ax.scatter(c["loc"][0], c["loc"][1], c='blue', marker='o', s=80,
                                   label='대피 시민' if c["id"] == "시민_1" else "")
                        ax.text(c["loc"][0], c["loc"][1]-1.5, c["id"], fontsize=9, ha='center')

                    # [알고리즘: 이분 매칭] 매칭 결과 경로 시각화
                    for c_idx, s_idx, count in match_results:
                        c_loc = dummy_citizens[c_idx]["loc"]
                        s_loc = dummy_shelters[s_idx]["loc"]
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
                    m1.metric("총 인원", f"{len(dummy_citizens)}명")
                    m2.metric("총 수용량", f"{sum(capacities)}명")
                    match_rate = (len(match_results) / len(dummy_citizens) * 100
                                  if dummy_citizens else 0.0)
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
