# 담당: 임성엽 / GachonAlgorithm10
"""
M6 UI — 구호물자 수요 산정 탭
"""
import streamlit as st

from .supply import compute, generate_sample_shelter_assign, results_to_rows


def render_supply_tab() -> None:
    st.header("📦 구호물자 수요 산정")

    with st.sidebar:
        st.subheader("M6 재고 설정")
        stock_water = st.number_input(
            "물 재고 (L)", min_value=0, value=500_000, step=10_000, key="m6_stock_water"
        )
        stock_food = st.number_input(
            "식량 재고 (kg)", min_value=0, value=80_000, step=5_000, key="m6_stock_food"
        )
        stock_med = st.number_input(
            "의약품 재고 (unit)", min_value=0, value=20_000, step=1_000, key="m6_stock_med"
        )

    shelter_assign = st.session_state.get("shelter_assign", [])
    risk_map = st.session_state.get("risk_map", {})

    col1, col2 = st.columns(2)
    with col1:
        if shelter_assign:
            st.success("✅ M1 대피소 배정 데이터 연동됨")
        else:
            st.info("M1을 먼저 실행하면 실제 배정 인원 반영")
    with col2:
        if risk_map:
            st.success("✅ M2 위험도 데이터 연동됨")
        else:
            st.info("M2를 먼저 실행하면 실제 위험도 반영")

    run_btn = st.button("수요 산정 실행", key="supply_run_btn", type="primary")

    if run_btn:
        if not shelter_assign:
            shelter_assign = generate_sample_shelter_assign(n=10)

        data = {
            "shelter_assign": shelter_assign,
            "risk_map": risk_map,
            "supplies": {
                "current_stock": {
                    "water_L": stock_water,
                    "food_kg": stock_food,
                    "med_unit": stock_med,
                }
            },
        }
        result = compute(data=data, params={})

        shortage = result["shortage"]
        alloc = result["total_alloc"]

        m1, m2, m3 = st.columns(3)
        m1.metric(
            "물 배분량 (L)",
            f"{alloc['water_L']:,.1f}",
            delta=f"-{shortage['water_L']:,.1f}" if shortage["water_L"] > 0 else None,
            delta_color="inverse",
        )
        m2.metric(
            "식량 배분량 (kg)",
            f"{alloc['food_kg']:,.1f}",
            delta=f"-{shortage['food_kg']:,.1f}" if shortage["food_kg"] > 0 else None,
            delta_color="inverse",
        )
        m3.metric(
            "의약품 배분량 (unit)",
            f"{alloc['med']:,.1f}",
            delta=f"-{shortage['med']:,.1f}" if shortage["med"] > 0 else None,
            delta_color="inverse",
        )

        st.dataframe(results_to_rows(result["supply_demand"]), use_container_width=True)

        st.session_state["supply_demand"] = result["supply_demand"]


def run() -> None:
    render_supply_tab()
