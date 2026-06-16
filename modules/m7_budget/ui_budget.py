# 담당: 임성엽 / GachonAlgorithm10
"""
M7 UI — 복구 예산 최적 배분 탭
"""
import streamlit as st

from .budget import compute, generate_sample_zones, results_to_rows


def render_budget_tab() -> None:
    st.header("💰 복구 예산 최적 배분")

    with st.sidebar:
        st.subheader("M7 예산 설정")
        budget_million = st.number_input(
            "복구 예산 (백만 원)",
            min_value=100,
            value=3000,
            step=500,
            key="m7_budget_million",
        )

    risk_map: dict = st.session_state.get("risk_map", {})
    if risk_map:
        st.success("✅ M2 위험도 데이터 연동됨")
    else:
        st.info("M2를 먼저 실행하면 위험도가 복구 효과에 반영됨")

    run_btn = st.button("예산 배분 최적화 실행", key="budget_run_btn", type="primary")

    if run_btn:
        sample_zones = generate_sample_zones(n=15, seed=42)

        result = compute(
            data={"damage_zones": sample_zones, "risk_map": risk_map},
            params={"budget_million": budget_million},
        )

        n_selected = sum(1 for z in result["selected_zones"] if z["selected"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("선택 구역 수", n_selected)
        m2.metric("예산 사용 (백만)", f"{result['budget_used']:,}")
        m3.metric("예산 잔여 (백만)", f"{result['budget_remain']:,}")
        m4.metric("총 복구 효과", result["total_effect"])

        st.dataframe(results_to_rows(result), use_container_width=True)

        st.session_state["budget_plan"] = [
            {
                "zone_id": z["zone_id"],
                "allocated": z["cost"] if z["selected"] else 0,
                "effect": z["effect"] if z["selected"] else 0,
            }
            for z in result["selected_zones"]
        ]


def run() -> None:
    render_budget_tab()
