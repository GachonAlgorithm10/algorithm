# 담당: 임성엽 / GachonAlgorithm10
"""
M7 UI — 복구 예산 최적 배분 탭
"""
import streamlit as st
import plotly.graph_objects as go
from core.viz_util import style_fig, show

from core.map_util import render_module_guide

from core.data_loader import get_loader

try:
    from .budget import compute, generate_sample_zones, results_to_rows
except ImportError:
    from budget import compute, generate_sample_zones, results_to_rows


def _real_to_zone(raw: dict) -> dict:
    """실데이터 dict → compute()가 기대하는 키로 변환 어댑터.
    실데이터 키: id, node_id, damage_area_m2, repair_cost_million, repair_effect_score
    compute 기대 키: zone_id, node_id, damage_area_m2, repair_cost_million, base_effect
    """
    return {
        "zone_id": raw.get("id", raw.get("zone_id", "")),
        "node_id": raw.get("node_id", ""),
        "damage_area_m2": raw.get("damage_area_m2", 0),
        "repair_cost_million": raw.get("repair_cost_million", 100),
        "base_effect": raw.get("repair_effect_score", raw.get("base_effect", 10)),
    }


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

    use_real = True

    run_btn = st.sidebar.button("▶ 예산 배분 최적화 실행", key="budget_run_btn", type="primary", use_container_width=True)

    if run_btn:

        risk_map = st.session_state.get("risk_map", {})

        # M2 위험도 데이터 연동 상태 알림 배지
        if isinstance(risk_map, dict) and risk_map:
            st.success("✅ M2 위험도 데이터 연동됨 (위험도가 복구 효과 가중치에 반영됩니다)")
        else:
            st.info("💡 M2 위험구역 확산 예측을 먼저 실행하면 실제 위험도가 복구 효과에 반영됩니다.")

        with st.spinner("0-1 Knapsack DP 알고리즘 기반 예산 최적 배분 연산 중..."):
            if use_real:
                try:
                    from core.data_loader import DataLoader
                    zones = [_real_to_zone(z) for z in DataLoader().damage_zones]
                except Exception as e:
                    st.warning(f"⚠️ 실데이터 로드 실패 — 더미 데이터로 대체합니다. ({e})")
                    zones = generate_sample_zones(n=15, seed=42)
            else:
                zones = generate_sample_zones(n=15, seed=42)

            result = compute(
                data={
                    "damage_zones": zones,
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
            st.success(
                f"💰 복구 예산 {budget_million:,}백만 원으로 {n_selected}개 구역 복구 선정 "
                f"— 총 복구효과 {result['total_effect']:,} (예산 {result['budget_used']:,} 사용)"
            )

            # 복구 우선순위 결정 리스트 (선정 구역, 효과 큰 순)
            selected = [z for z in result["selected_zones"] if z["selected"]]
            selected.sort(key=lambda z: z["effect"], reverse=True)
            st.markdown("#### 복구 착수 우선순위")
            _nl = get_loader()
            decision_rows = [
                {"순위": i, "구역": z["zone_id"],
                 "거점": _nl.name_of(z.get("node_id", "")),
                 "복구비용(백만)": z["cost"], "복구효과": z["effect"]}
                for i, z in enumerate(selected, 1)
            ]
            st.dataframe(decision_rows, use_container_width=True, height=320)

            # 보조 시각물: 전체 구역 효과 (선택 강조)
            st.markdown("#### 구역별 복구 효과 (선택 강조)")
            sz = sorted(result["selected_zones"], key=lambda z: z["effect"], reverse=True)
            colors = ["#2F9E44" if z["selected"] else "#495057" for z in sz]
            fig = go.Figure([go.Bar(x=[z["zone_id"] for z in sz],
                                    y=[z["effect"] for z in sz], marker_color=colors)])
            fig.update_layout(xaxis_title="복구 구역", yaxis_title="실효과", xaxis_tickangle=-45)
            show(style_fig(fig, height=360))
            st.caption("💡 초록 = 예산 배분 선택(Knapsack DP), 회색 = 예산 제약으로 제외된 구역")

            with st.expander("📋 지역별 상세 배분 결과 (전체)"):
                st.dataframe(results_to_rows(result), use_container_width=True, height=360)

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
