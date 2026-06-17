# 담당: 임성엽 / GachonAlgorithm10
"""
M7 UI — 복구 예산 최적 배분 탭
"""
import streamlit as st

from core.map_util import render_module_guide

try:
    from .budget import compute, generate_sample_zones, results_to_rows
except ImportError:
    from budget import compute, generate_sample_zones, results_to_rows

def run() -> None:
    # 사이드바 설정
    st.sidebar.header("⚙️ 시뮬레이션 설정")
    st.sidebar.subheader("예산 설정")
    budget_million = st.sidebar.number_input(
        "복구 예산 (백만 원)",
        min_value=100,
        value=3000,
        step=500,
        key="m7_budget_million",
    )

    run_btn = st.sidebar.button("▶ 예산 배분 최적화 실행", key="budget_run_btn", type="primary", use_container_width=True)

    if run_btn:

        risk_map = st.session_state.get("risk_map", {})

        # M2 위험도 데이터 연동 상태 알림 배지
        if isinstance(risk_map, dict) and risk_map:
            st.success("✅ M2 위험도 데이터 연동됨 (위험도가 복구 효과 가중치에 반영됩니다)")
        else:
            st.info("💡 M2 위험구역 확산 예측을 먼저 실행하면 실제 위험도가 복구 효과에 반영됩니다.")

        with st.spinner("0-1 Knapsack DP 알고리즘 기반 예산 최적 배분 연산 중..."):
            sample_zones = generate_sample_zones(n=15, seed=42)

            result = compute(
                data={
                    "damage_zones": sample_zones,
                    # risk_map이 딕셔너리가 아니면 빈 딕셔너리로 넘김
                    "risk_map": risk_map if isinstance(risk_map, dict) else {}
                },
                params={"budget_million": budget_million},
            )

            n_selected = sum(1 for z in result["selected_zones"] if z["selected"])

            st.subheader("📊 예산 배분 요약")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("선택 구역 수", f"{n_selected} 곳")
            m2.metric("예산 사용", f"{result['budget_used']:,} 백만")
            m3.metric("예산 잔여", f"{result['budget_remain']:,} 백만")
            m4.metric("총 복구 효과", f"{result['total_effect']:,}")

            st.write("---")
            st.subheader("📋 지역별 상세 배분 결과")
            st.dataframe(results_to_rows(result), use_container_width=True)

            # 파이프라인 연동 세션 저장 유지
            st.session_state["budget_plan"] = [
                {
                    "zone_id": z["zone_id"],
                    "allocated": z["cost"] if z["selected"] else 0,
                    "effect": z["effect"] if z["selected"] else 0,
                }
                for z in result["selected_zones"]
            ]
    else:
        st.write("")
        render_module_guide("M7")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    run()