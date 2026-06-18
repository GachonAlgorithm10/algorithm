# 담당: 임성엽 / GachonAlgorithm10
"""
M6 UI — 구호물자 수요 산정 탭
"""
import streamlit as st
import plotly.graph_objects as go
from core.viz_util import style_fig, show

from core.map_util import render_module_guide

from core.data_loader import get_loader

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
            # 부족 대피소 우선 추출 (예외 우선)
            sd = result["supply_demand"]
            _nl = get_loader()
            shortages = []
            for sid, v in sd.items():
                sw = round(v["need_water_L"] - v["alloc_water_L"], 1)
                sf = round(v["need_food_kg"] - v["alloc_food_kg"], 1)
                sm = round(v["need_med"] - v["alloc_med"], 1)
                if sw > 0.1 or sf > 0.1 or sm > 0.1:
                    shortages.append({"대피소": _nl.name_of(sid), "부족(물,L)": sw,
                                      "부족(식량,kg)": sf, "부족(의약품)": sm})

            if shortages:
                st.error(f"🚨 {len(shortages)}개 대피소 물자 부족 — 추가 배송이 필요합니다.")
                shortages.sort(key=lambda r: r["부족(물,L)"], reverse=True)
                st.markdown("#### 물자 부족 대피소 (부족량 큰 순)")
                st.dataframe(shortages, use_container_width=True, height=320)
            else:
                st.success("✅ 전 대피소 물자 수요 100% 충족 — 추가 배송 불필요.")

            # 보조 지표: 물자별 충족률
            need, alloc = result["total_need"], result["total_alloc"]
            def _rate(a, n):
                return round(a / n * 100, 1) if n > 0 else 100.0
            cats = ["물", "식량", "의약품"]
            rates = [_rate(alloc["water_L"], need["water_L"]),
                     _rate(alloc["food_kg"], need["food_kg"]),
                     _rate(alloc["med"], need["med"])]
            colors = ["#2F9E44" if r >= 99.9 else "#E8590C" for r in rates]
            st.markdown("#### 물자별 수요 충족률")
            fig = go.Figure([go.Bar(x=cats, y=rates, marker_color=colors,
                                    text=[f"{r}%" for r in rates], textposition="outside")])
            fig.update_layout(yaxis_title="충족률 (%)", yaxis_range=[0, 110])
            fig.add_hline(y=100, line_dash="dash", line_color="rgba(128,128,128,0.5)")
            show(style_fig(fig, height=320))

            with st.expander("📋 대피소별 상세 배분 결과 (전체)"):
                _rows = results_to_rows(result["supply_demand"])
                _keep = ["대피소", "배정인원", "위험도", "우선순위",
                         "배분(물,L)", "배분(식량,kg)", "배분(의약품)"]
                _trimmed = [{k: row[k] for k in _keep if k in row} for row in _rows]
                st.dataframe(_trimmed, use_container_width=True, height=360)

            # 파이프라인 연동 세션 저장 유지
            st.session_state["supply_demand"] = result["supply_demand"]

    else:
        st.write("")
        render_module_guide("M6")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    run()