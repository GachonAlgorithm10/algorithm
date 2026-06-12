"""
============================================================
module_m5_network / ui_network.py
비상 통신망 설계 모듈의 Streamlit 화면 (M5 탭)
담당: 최의찬
============================================================
단독 실행:   streamlit run module_m5_network/ui_network.py
app.py 통합: render_network_tab() 또는 run() 호출
"""

try:
    from .mst_kruskal import build_mst, edge_rows
    from .tarjan import find_articulation_points, spof_rows
except ImportError:
    from mst_kruskal import build_mst, edge_rows
    from tarjan import find_articulation_points, spof_rows


def generate_sample_network():
    """
    M5 단독 실행/테스트용 통신망 데이터.

    M2 위험 구역 확산 예측 모듈과 연결하기 위해
    node_id = y * 60 + x 형식을 사용한다.

    실제 통합 단계에서는 M2의 graph_data 또는 위험 구역 결과에서
    주요 거점 node_id를 받아와서 nodes, edges를 교체하면 된다.
    """

    # [자료구조: 그래프(Graph)]
    # 거점 노드는 M2 격자 결과와 매핑하기 쉽도록 정수 node_id로 구성한다.
    nodes = [
        1830,  # 예시 거점 1
        1831,  # 예시 거점 2
        1890,  # 예시 거점 3
        1891,  # 예시 거점 4
        1950,  # 예시 거점 5
        1951,  # 예시 거점 6
    ]

    # 간선 형식: (출발 node_id, 도착 node_id, 복구 비용)
    edges = [
        (1830, 1831, 4),
        (1830, 1890, 2),
        (1831, 1890, 1),
        (1831, 1891, 5),
        (1890, 1891, 8),
        (1890, 1950, 10),
        (1891, 1950, 2),
        (1891, 1951, 6),
        (1950, 1951, 3),
    ]

    return nodes, edges


def render_network_tab():
    """app.py 의 M5 탭에서 이 함수를 호출한다."""
    import streamlit as st

    st.header("📡 비상 통신망 설계")
    st.divider()

    nodes, edges = generate_sample_network()

    # --- 사이드바 입력 데이터 ---
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    st.sidebar.markdown("#### 거점 노드")
    st.sidebar.write(nodes)
    st.sidebar.caption("M2 연동 기준: node_id = y * 60 + x")
    st.sidebar.markdown("#### 복구 후보 간선")
    st.sidebar.dataframe(edge_rows(edges), use_container_width=True)
    run_btn = st.sidebar.button("▶ 통신망 설계 실행", key="network_run_btn", type="primary", use_container_width=True)

    if run_btn:
        # [알고리즘: 크루스칼 알고리즘]
        mst_edges, total_cost, is_connected = build_mst(nodes, edges)

        st.divider()
        st.subheader("📊 결과")

        st.markdown("#### 최소 비용 복구 통신망 MST")
        st.dataframe(edge_rows(mst_edges), use_container_width=True)

        st.markdown("#### 총 복구 비용")
        st.metric(label="Total Recovery Cost", value=total_cost)

        st.markdown("#### 연결 상태")
        if is_connected:
            st.success("✅ 모든 거점이 최소 비용 복구 통신망으로 연결되었습니다.")

            # [알고리즘: Tarjan 단절점 탐지]
            # MST 기준으로 SPOF를 탐지한다.
            spof_nodes = find_articulation_points(nodes, mst_edges)

            st.markdown("#### 단일 장애점(SPOF) 탐지 결과")
            if spof_nodes:
                st.warning("⚠️ 단일 장애점이 탐지되었습니다.")
                st.dataframe(spof_rows(spof_nodes), use_container_width=True)
            else:
                st.success("✅ 단일 장애점이 없습니다.")
        else:
            st.error("🚨 일부 거점이 연결되지 않았습니다. 후보 간선 데이터를 확인해야 합니다.")
            st.info("💡 비연결 그래프에서는 SPOF 탐지를 수행할 수 없습니다.")
    else:
        st.info("💡 왼쪽 사이드바에서 설정을 조정한 뒤 '실행' 버튼을 눌러주세요.")


def run():
    """
    M2 ui_spread.py처럼 app.py에서 run() 방식으로 호출할 경우를 대비한 함수.
    """
    render_network_tab()


# 단독 실행 (streamlit run)
if __name__ == "__main__":
    render_network_tab()
