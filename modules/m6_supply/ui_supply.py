# 담당: 임성엽 / GachonAlgorithm10
"""
M6 UI — 구호물자 수요 산정 탭
"""
import streamlit as st

from core.map_util import render_module_guide

try:
    from .supply import compute, generate_sample_shelter_assign, results_to_rows
except ImportError:
    from supply import compute, generate_sample_shelter_assign, results_to_rows


def run() -> None:
    # 사이드바 설정
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    st.sidebar.subheader("재고 설정")
    stock_water = st.sidebar.number_input(
        "물 재고 (L)", min_value=0, value=500_000, step=10_000, key="m6_stock_water"
    )
    stock_food = st.sidebar.number_input(
        "식량 재고 (kg)", min_value=0, value=80_000, step=5_000, key="m6_stock_food"
    )
    stock_med = st.sidebar.number_input(
        "의약품 재고 (unit)", min_value=0, value=20_000, step=1_000, key="m6_stock_med"
    )

    run_btn = st.sidebar.button("▶ 수요 산정 실행", key="supply_run_btn", type="primary", use_container_width=True)

    if run_btn:

        shelter_assign = st.session_state.get("shelter_assign", [])
        risk_map = st.session_state.get("risk_map", {})

        # M1 대피소 배정 데이터 연동 상태 알림 배지
        col1, col2 = st.columns(2)
        with col1:
            if shelter_assign:
                st.success("✅ M1 대피소 배정 데이터 연동됨")
            else:
                st.info("💡 M1을 먼저 실행하면 실제 배정 인원 반영")
        with col2:
            # risk_map이 단순 True 값이 아니라 실제 딕셔너리일 때만 연동 성공으로 판정
            if isinstance(risk_map, dict) and risk_map:
                st.success("✅ M2 위험도 데이터 연동됨")
            else:
                st.info("💡 M2를 먼저 실행하면 실제 위험도 반영")

        with st.spinner("구호물자 수요 및 최적 배분 연산 중..."):
            if not shelter_assign:
                shelter_assign = generate_sample_shelter_assign(n=10)

            data = {
                "shelter_assign": shelter_assign,
                # risk_map이 딕셔너리가 아니면 빈 딕셔너리로 넘김
                "risk_map": risk_map if isinstance(risk_map, dict) else {},
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

            st.subheader("📊 전체 물자 배분 요약")
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

            st.write("---")
            st.subheader("📋 대피소별 상세 배분 결과")
            st.dataframe(results_to_rows(result["supply_demand"]), use_container_width=True)

            # 파이프라인 연동 세션 저장 유지
            st.session_state["supply_demand"] = result["supply_demand"]

    else:
        st.write("")
        render_module_guide("M6")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    run()