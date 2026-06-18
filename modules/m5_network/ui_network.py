"""
============================================================
module_m5_network / ui_network.py
비상 통신망 설계 모듈의 Streamlit 화면 (M5 탭)
담당: 최의찬
============================================================
단독 실행:   streamlit run module_m5_network/ui_network.py
app.py 통합: render_network_tab() 또는 run() 호출
"""

from core.data_loader import DataLoader

import plotly.graph_objects as go
from core.data_loader import get_loader
from core.viz_util import style_fig, show

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
    nodes = [1830, 1831, 1890, 1891, 1950, 1951]
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


def _load_real_network(risk_map: dict) -> tuple:
    """
    graph_data.json에서 통신망 노드/엣지를 로드한다.
    통신 거점: shelter + hospital 노드 (graph_data.json 전체 224개)
    엣지 형식: mst_kruskal.py가 기대하는 (from_id, to_id, weight) 튜플
    weight = edge["distance"] * (1 + risk_map.get(from_id, 0))  위험도 반영
    """
    loader = DataLoader()
    nodes = [n["id"] for n in loader.nodes]

    edges = []
    for e in loader.edges:
        from_id = e["from"]
        to_id = e["to"]
        dist = e.get("distance", 0.05)
        risk_penalty = 1 + risk_map.get(from_id, 0.0)
        weight = round(dist * risk_penalty, 4)
        edges.append((from_id, to_id, weight))

    return nodes, edges


def _edge_rows_str(edges):
    """실데이터(문자열 노드)용 엣지 표 행 생성.
    edge_rows()는 내부에서 node_id % 60 정수 연산을 하므로 문자열 노드에 사용 불가.
    """
    return [
        {"출발 node_id": u, "도착 node_id": v, "가중치(거리×위험)": cost}
        for u, v, cost in edges
    ]


def _spof_rows_str(spof_nodes):
    """실데이터(문자열 노드)용 SPOF 표 행 생성."""
    return [
        {"단일 장애점 node_id": node, "위험 설명": "해당 거점 장애 시 통신망 분리 가능"}
        for node in spof_nodes
    ]


def _build_network_graph(node_ids, mst_edges, spof_set, pos, type_lookup):
    """MST 통신망 네트워크 그래프. 노드=거점(grid 좌표), 엣지=MST, SPOF=빨강."""
    # MST 간선 라인 (None 구분자로 한 trace에 모두)
    ex, ey = [], []
    for u, v, _ in mst_edges:
        if u in pos and v in pos:
            ex += [pos[u][0], pos[v][0], None]
            ey += [pos[u][1], pos[v][1], None]
    edge_trace = go.Scatter(
        x=ex, y=ey, mode="lines",
        line=dict(width=0.8, color="rgba(130,150,180,0.45)"),
        hoverinfo="skip", showlegend=False,
    )

    def _markers(ids, color, size, name):
        ids = [i for i in ids if i in pos]
        return go.Scatter(
            x=[pos[i][0] for i in ids], y=[pos[i][1] for i in ids],
            mode="markers", name=f"{name} ({len(ids)})",
            marker=dict(size=size, color=color,
                        line=dict(width=0.5, color="rgba(255,255,255,0.35)")),
            text=[f"{i}<br>{type_lookup.get(i, '')}"
                  f"{'  ⚠️ 단일 장애점' if i in spof_set else ''}" for i in ids],
            hovertemplate="%{text}<extra></extra>",
        )

    normal = [i for i in node_ids if i not in spof_set]
    spofs = [i for i in node_ids if i in spof_set]
    fig = go.Figure(data=[
        edge_trace,
        _markers(normal, "#4C8BF5", 6, "정상 거점"),
        _markers(spofs, "#E03131", 10, "단일 장애점"),
    ])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=1.04, x=1, xanchor="right"),
    )
    # 격자 1:1 비율, 축 눈금 숨김 (지도형 레이아웃)
    fig.update_yaxes(scaleanchor="x", showgrid=True, gridcolor="rgba(128,128,128,0.15)",
                        zeroline=False, showticklabels=False)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)",
                        zeroline=False, showticklabels=False)
    return style_fig(fig, height=620)


def render_network_tab():
    """app.py 의 M5 탭에서 이 함수를 호출한다."""
    import streamlit as st
    from core.map_util import render_module_guide

    # --- 사이드바 ---
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    use_real = True

    if use_real:
        lite_mode = st.sidebar.checkbox(
            "⚡ 경량 모드 (엣지 3,000개 제한)",
            value=False,
            key="m5_lite_mode",
        )
        st.sidebar.info("실데이터: 224노드 / 최대 15,071엣지")
    else:
        lite_mode = False
        dummy_nodes, dummy_edges = generate_sample_network()
        st.sidebar.markdown("#### 거점 노드")
        st.sidebar.write(dummy_nodes)
        st.sidebar.markdown("#### 복구 후보 간선")
        st.sidebar.dataframe(edge_rows(dummy_edges), use_container_width=True)

    run_btn = st.sidebar.button("▶ 통신망 설계 실행", key="network_run_btn", type="primary", use_container_width=True)

    if run_btn:
        risk_map = st.session_state.get("risk_map", {})

        # M2 연동 배지
        if isinstance(risk_map, dict) and risk_map:
            st.success("✅ M2 위험도 데이터 연동됨 — 위험 경로 가중치 반영")
        else:
            st.info("ℹ️ M2 미실행 시 기본 거리 기반 MST 계산")

        # 데이터 로드
        if use_real:
            try:
                nodes, edges = _load_real_network(risk_map)
            except Exception as e:
                st.warning(f"⚠️ 실데이터 로드 실패 — 더미 데이터로 대체합니다. ({e})")
                nodes, edges = generate_sample_network()
                use_real = False
        else:
            nodes, edges = generate_sample_network()

        # 경량 모드: weight 기준 상위 3,000개 엣지로 제한
        if lite_mode and use_real:
            edges = sorted(edges, key=lambda e: e[2])[:3000]

        n_label = f"{len(nodes)}노드, {len(edges)}엣지"
        with st.spinner(f"크루스칼 MST 연산 중 ({n_label})..."):
            mst_edges, total_cost, is_connected = build_mst(nodes, edges)

        # session_state 저장 (spof_nodes는 아래에서 채움)
        st.session_state["network_plan"] = {
            "mst_edges": mst_edges,
            "spof_nodes": [],
        }

        st.divider()
        st.subheader("📊 결과")

        if not is_connected:
            st.error("🚨 일부 거점이 연결되지 않았습니다. 후보 간선 데이터를 확인해야 합니다.")
            st.info("💡 비연결 그래프에서는 SPOF 탐지를 수행할 수 없습니다.")
        else:
            with st.spinner("Tarjan 단절점 탐지 중..."):
                spof_nodes = find_articulation_points(nodes, mst_edges)
            st.session_state["network_plan"]["spof_nodes"] = spof_nodes
            spof_set = set(spof_nodes)

            # 좌표 / 유형 매핑
            if use_real:
                _l = get_loader()
                pos = {n["id"]: (n["grid_x"], n["grid_y"]) for n in _l.nodes}
                type_lookup = {n["id"]: n.get("type", "") for n in _l.nodes}
            else:
                pos = {nid: (nid % 60, nid // 60) for nid in nodes}
                type_lookup = {nid: "거점" for nid in nodes}

            # KPI 카드
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("통신 거점", f"{len(nodes)} 곳")
            c2.metric("MST 간선", f"{len(mst_edges)} 개")
            c3.metric("총 복구 비용", round(total_cost, 2))
            c4.metric("단일 장애점(SPOF)", f"{len(spof_nodes)} 개")

            # 네트워크 그래프 (주요 시각물)
            st.markdown("#### 최소 비용 복구 통신망")
            st.caption("파란 노드=정상 거점, 빨간 노드=단일 장애점(장애 시 통신망 분리 위험). 노드에 마우스를 올리면 상세 정보가 표시됩니다.")
            show(_build_network_graph(nodes, mst_edges, spof_set, pos, type_lookup))

            # 연결 상태 요약
            st.success("✅ 모든 거점이 최소 비용 복구 통신망으로 연결되었습니다.")
            if spof_nodes:
                st.warning(f"⚠️ 단일 장애점 {len(spof_nodes)}개 — MST(트리) 구조 특성상 잎 노드를 제외한 모든 거점이 장애 시 통신망 분리를 유발할 수 있습니다.")

            # 상세 표 (기본 접힘)
            with st.expander("📋 상세 데이터 (MST 간선 / SPOF 목록)"):
                st.markdown("**최소 비용 복구 통신망 (MST 간선)**")
                if use_real:
                    st.dataframe(_edge_rows_str(mst_edges), use_container_width=True, height=300)
                else:
                    st.dataframe(edge_rows(mst_edges), use_container_width=True)
                st.markdown("**단일 장애점(SPOF) 목록**")
                st.dataframe(
                    [{"node_id": n, "유형": type_lookup.get(n, "")} for n in spof_nodes],
                    use_container_width=True, height=300,
                )
    else:
        st.write("")
        render_module_guide("M5")


def run():
    """app.py에서 run() 방식으로 호출할 경우를 대비한 함수."""
    render_network_tab()


# 단독 실행 (streamlit run)
if __name__ == "__main__":
    render_network_tab()
