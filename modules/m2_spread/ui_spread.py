# -*- coding: utf-8 -*-
# module_m2_spread/ui_spread.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from .bfs_spread import BFSFireSpread
from .cellular_automata import CellularAutomataModel

@st.cache_resource
def init_simulation_engine():
    return BFSFireSpread("data/graph_data.json")

def run():
    st.header("🔥 위험 구역 확산 예측")
    st.divider()
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    try:
        bfs_engine = init_simulation_engine()
        ca_engine = CellularAutomataModel(bfs_engine.width, bfs_engine.height)

        # 실제 노드 목록에서 발화점 선택 (id_to_coord 키와 일치)
        node_options = [n["id"] for n in bfs_engine.raw_data["nodes"]]
        node_labels = {
            n["id"]: f'{n["id"]} · {n.get("name", "")}'
            for n in bfs_engine.raw_data["nodes"]
        }
        start_node = st.sidebar.selectbox(
            "발화점 노드 선택",
            options=node_options,
            format_func=lambda nid: node_labels.get(nid, nid),
            index=0,
        )
        wind_direction = st.sidebar.selectbox(
            "기상 조건 (바람 방향)", ["무풍", "북풍", "남풍", "동풍", "서풍"]
        )
        max_time = st.sidebar.slider("최대 시뮬레이션 시간 (BFS 제한 시간)", 5, 30, 15)
        ca_turns = st.sidebar.slider("셀룰러 오토마타 예측 턴 (CA 반복 횟수)", 1, 10, 3)

        run_btn = st.sidebar.button("▶ 시뮬레이션 실행", key="spread_run_btn", type="primary", use_container_width=True)

        if run_btn:
            with st.spinner("🔥 재난 확산 시뮬레이션 연산 중..."):
                fire_time_map = bfs_engine.run_bfs(
                    start_node_id=start_node, max_time=max_time
                )

                current_grid = np.zeros_like(fire_time_map, dtype=int)
                burned_mask = fire_time_map != -1.0

                if np.any(burned_mask):
                    max_t = np.max(fire_time_map[burned_mask])
                    condlist = [
                        fire_time_map == -1.0,
                        fire_time_map <= max_t * 0.33,
                        fire_time_map <= max_t * 0.66
                    ]
                    choicelist = [0, 3, 2]
                    current_grid = np.select(condlist, choicelist, default=1)

                final_hazard_map = np.copy(current_grid)
                for _ in range(ca_turns):
                    final_hazard_map = ca_engine.cellular_automata_step(
                        final_hazard_map, wind_dir=wind_direction
                    )

            # [알고리즘: BFS 확산 모델 / 자료구조: 2D Grid]
            # 격자 위험도 → node_id 문자열 매핑 변환 후 session_state 저장
            HAZARD_TO_RISK = {0: 0.0, 1: 0.33, 2: 0.67, 3: 1.0}
            risk_map = {}
            for node in bfs_engine.raw_data["nodes"]:
                gx = node.get("grid_x")
                gy = node.get("grid_y")
                nid = node.get("id")
                if gx is None or gy is None or nid is None:
                    continue
                if 0 <= gy < final_hazard_map.shape[0] and 0 <= gx < final_hazard_map.shape[1]:
                    risk_map[nid] = HAZARD_TO_RISK.get(int(final_hazard_map[gy, gx]), 0.0)
            st.session_state["risk_map"] = risk_map
            st.success(f"✅ risk_map 저장 완료 — {len(risk_map)}개 노드")

            st.divider()
            st.subheader("📊 결과")
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader(f"예측 분석 보고서 (발화 노드 ID: {start_node})")
                plot_map = final_hazard_map.astype(float)
                plot_map[plot_map == 0] = np.nan

                fig, ax = plt.subplots(figsize=(8, 7))
                ax.imshow(bfs_engine.population_matrix, cmap="gray", alpha=0.15, origin="lower")
                im = ax.imshow(plot_map, cmap="YlOrRd", vmin=1, vmax=3, origin="lower")
                cbar = plt.colorbar(im, ax=ax, ticks=[1, 2, 3])
                cbar.ax.set_yticklabels(['1 (주의)', '2 (위험)', '3 (재난)'])
                cbar.set_label("최종 위험도 단계 (Hazard Level)")
                ax.set_xlabel("격자 X 좌표")
                ax.set_ylabel("격자 Y 좌표")
                st.pyplot(fig)

            with col2:
                st.subheader("위험 구역 요약")
                safe_cnt  = np.sum(final_hazard_map == 0)
                watch_cnt = np.sum(final_hazard_map == 1)
                warn_cnt  = np.sum(final_hazard_map == 2)
                danger_cnt = np.sum(final_hazard_map == 3)
                st.metric("최고 재난 구역 (Level 3)", f"{danger_cnt} 칸")
                st.metric("위험 구역 (Level 2)", f"{warn_cnt} 칸")
                st.metric("주의 구역 (Level 1)", f"{watch_cnt} 칸")
                st.metric("안전 구역 (Level 0)", f"{safe_cnt} 칸")

            st.info("💡 [연동 정보] risk_map이 M1·M3·M4·M5·M7에 자동 전달됩니다.")

        else:
            st.info("💡 왼쪽 사이드바에서 설정을 조정한 뒤 '실행' 버튼을 눌러주세요.")

    except Exception as e:
        st.error(
            f"🚨 데이터 셋업 에러: 전처리 파일(data/graph_data.json)을 먼저 로드해 주세요. 상세 내용: {e}"
        )

if __name__ == "__main__":
    run()
