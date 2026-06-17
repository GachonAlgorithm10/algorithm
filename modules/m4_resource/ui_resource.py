# 담당: 임성엽 / GachonAlgorithm10
"""
M4 UI — 구조자원 배치 탭
"""
import streamlit as st

from core.map_util import render_module_guide

try:
    from .resource import (
        assign_resources,
        build_resource_cost_matrix,
        generate_sample_resources,
        generate_sample_sites,
        results_to_rows,
    )
except ImportError:
    from resource import (
        assign_resources,
        build_resource_cost_matrix,
        generate_sample_resources,
        generate_sample_sites,
        results_to_rows,
    )


def run() -> None:
    # 사이드바 설정
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    n_resources = st.sidebar.slider("자원 수", min_value=4, max_value=30, value=10, key="m4_n_resources")
    n_sites_val = st.sidebar.slider("현장 수", min_value=2, max_value=8, value=4, key="m4_n_sites")

    run_btn = st.sidebar.button("▶ 배치 최적화 실행", key="resource_run_btn", type="primary", use_container_width=True)

    if run_btn:

        # M2 위험도 데이터 연동 상태 알림 배지
        risk_map = st.session_state.get("risk_map", {})
        if isinstance(risk_map, dict) and risk_map:
            st.success("✅ M2 위험도 데이터 연동됨 (risk_map 기반 가중치 반영)")
        else:
            st.info("💡 M2 위험구역 확산 예측을 먼저 실행하면 실제 재난 위험도가 반영됩니다.")

        with st.spinner("구조자원 최적 배치 연산 중..."):
            resources = generate_sample_resources(n=n_resources, seed=42)
            sites = generate_sample_sites(n=n_sites_val, seed=7)

            # risk_map이 정상적인 딕셔너리일 때만 위험도 덮어쓰기
            if isinstance(risk_map, dict):
                for site in sites:
                    site.risk = risk_map.get(site.node_id, site.risk)

            cost_matrix = build_resource_cost_matrix(resources, sites)
            assigned = assign_resources(resources, sites, cost_matrix)

            n_assigned = sum(1 for r in assigned if r.assigned_site)
            n_unassigned = len(assigned) - n_assigned
            total_cost = sum(r.cost for r in assigned if r.assigned_site)

            st.subheader("📊 결과 요약")
            col1, col2, col3 = st.columns(3)
            col1.metric("배정 완료", f"{n_assigned} 건")
            col2.metric("미배정", f"{n_unassigned} 건")
            col3.metric("총 배치 비용", f"{total_cost:.4f}")

            st.subheader("📋 상세 배치 결과")
            st.dataframe(results_to_rows(assigned), use_container_width=True)

        st.session_state["resource_assign"] = [
            {"vol_id": r.rid, "site_id": r.assigned_site, "cost": r.cost}
            for r in assigned
            if r.assigned_site
        ]
    else:
        st.write("")
        render_module_guide("M4")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    run()