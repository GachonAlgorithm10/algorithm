# 담당: 임성엽 / GachonAlgorithm10
"""
M4 UI — 구조자원 배치 탭
"""
import streamlit as st

from .resource import (
    assign_resources,
    build_resource_cost_matrix,
    generate_sample_resources,
    generate_sample_sites,
    results_to_rows,
)


def render_resource_tab() -> None:
    st.header("🚒 구조자원 배치")

    with st.sidebar:
        st.subheader("M4 파라미터")
        n_resources = st.slider("자원 수", min_value=4, max_value=30, value=10, key="m4_n_resources")
        n_sites_val = st.slider("현장 수", min_value=2, max_value=8, value=4, key="m4_n_sites")

    risk_map: dict = st.session_state.get("risk_map", {})
    if risk_map:
        st.success("✅ M2 위험도 데이터 연동됨")
    else:
        st.info("M2를 먼저 실행하면 실제 위험도 반영")

    run_btn = st.button("배치 최적화 실행", key="resource_run_btn", type="primary")

    if run_btn:
        resources = generate_sample_resources(n=n_resources, seed=42)
        sites = generate_sample_sites(n=n_sites_val, seed=7)

        for site in sites:
            site.risk = risk_map.get(site.node_id, site.risk)

        cost_matrix = build_resource_cost_matrix(resources, sites)
        assigned = assign_resources(resources, sites, cost_matrix)

        n_assigned = sum(1 for r in assigned if r.assigned_site)
        n_unassigned = len(assigned) - n_assigned
        total_cost = sum(r.cost for r in assigned if r.assigned_site)

        col1, col2, col3 = st.columns(3)
        col1.metric("배정완료", n_assigned)
        col2.metric("미배정", n_unassigned)
        col3.metric("총배치비용", f"{total_cost:.4f}")

        st.dataframe(results_to_rows(assigned), use_container_width=True)

        st.session_state["resource_assign"] = [
            {"vol_id": r.rid, "site_id": r.assigned_site, "cost": r.cost}
            for r in assigned
            if r.assigned_site
        ]


def run() -> None:
    render_resource_tab()
