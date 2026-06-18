# 담당: 임성엽 / GachonAlgorithm10
"""
M4 UI — 구조자원 배치 탭
"""
import streamlit as st
import plotly.graph_objects as go
from core.viz_util import style_fig, show

from core.map_util import render_module_guide

try:
    from .resource import (
        Resource,
        assign_resources,
        build_resource_cost_matrix,
        generate_sample_resources,
        generate_sample_sites,
        results_to_rows,
    )
except ImportError:
    from resource import (
        Resource,
        assign_resources,
        build_resource_cost_matrix,
        generate_sample_resources,
        generate_sample_sites,
        results_to_rows,
    )


SKILL_KO = {
    "ambulance": "구급차",
    "excavator": "굴착기",
    "psychological_support": "심리지원",
    "logistics": "물류",
    "generator": "발전기",
    "search_rescue": "수색구조",
    "fire_truck": "소방차",
}


def _real_to_resource(raw: dict) -> Resource:
    """실데이터 dict → Resource 객체 변환 어댑터.
    실데이터 키: id, type, location_node, skill
    Resource 키: rid, rtype, skill, location_node, assigned_site, cost
    """
    return Resource(
        rid=str(raw.get("id", "")),
        rtype=str(raw.get("type", "volunteer")),
        skill=str(raw.get("skill", "")),
        location_node=str(raw.get("location_node", "node_001")),
    )


def run() -> None:
    # 사이드바 설정
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    use_real = True

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
            # 자원(봉사자/장비) 로드 — sites는 실데이터 없으므로 더미 유지
            if use_real:
                try:
                    from core.data_loader import DataLoader
                    resources = [_real_to_resource(r) for r in DataLoader().volunteers]
                except Exception as e:
                    st.warning(f"⚠️ 실데이터 로드 실패 — 더미 데이터로 대체합니다. ({e})")
                    resources = generate_sample_resources(n=10, seed=42)
            else:
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

            st.markdown("#### 자원 배치 현황")
            cc1, cc2 = st.columns([1, 1])
            with cc1:
                donut = go.Figure([go.Pie(
                    labels=["배정 완료", "대기 자원"], values=[n_assigned, n_unassigned],
                    hole=0.55, marker_colors=["#2F9E44", "#495057"], sort=False,
                )])
                donut.update_layout(title_text="배정 / 대기")
                show(style_fig(donut, height=340))
            with cc2:
                skill_cnt = {}
                for r in assigned:
                    if r.assigned_site:
                        skill_cnt[r.skill] = skill_cnt.get(r.skill, 0) + 1
                bar = go.Figure([go.Bar(
                    x=list(skill_cnt.values()),
                    y=[SKILL_KO.get(k, k) for k in skill_cnt.keys()], orientation="h",
                    marker_color="#4C8BF5", text=list(skill_cnt.values()), textposition="outside",
                )])
                bar.update_layout(title_text="배정 자원 스킬 구성", xaxis_title="배정 수")
                show(style_fig(bar, height=340))

            st.caption(f"💡 가용 현장 {n_sites_val}곳에 최적 자원을 배치했습니다. 나머지 {n_unassigned}건은 대기 자원입니다.")
            with st.expander("📋 상세 배치 결과 (전체 자원)"):
                st.dataframe(results_to_rows(assigned), use_container_width=True, height=360)

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
