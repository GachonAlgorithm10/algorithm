"""
재난 대응 통합 의사결정 시스템
Streamlit 메인 애플리케이션 — 7개 모듈 통합
담당: 임성엽 / GachonAlgorithm10

모듈 흐름 (재난 대응 타임라인):
  [1단계] M2 위험구역 확산 예측
  [2단계] M1 대피소 수용량 배분 / M3 부상자 이송 / M4 구조자원 배치
  [3단계] M6 구호물자 수요 산정
  [4단계] M5 비상 통신망 복구 / M7 복구 예산 최적 배분
"""
import streamlit as st

from core.data_loader import init_session_state
init_session_state()

from modules import m1_shelter, m2_spread, m3_triage, m4_resource
from modules import m5_network, m6_supply, m7_budget

st.set_page_config(
    page_title="재난 대응 통합 의사결정 시스템",
    page_icon="🚨",
    layout="wide",
)

st.sidebar.title("🚨 재난 대응 시스템")
st.sidebar.caption("GachonAlgorithm10 | 가천대 알고리즘 기말")
st.sidebar.divider()

menu = st.sidebar.radio(
    "모듈 선택",
    [
        "🔥 위험구역 확산 예측",
        "🏠 대피소 수용량 배분",
        "🚑 부상자 이송 우선순위",
        "🚒 구조자원 배치",
        "📦 구호물자 수요 산정",
        "📡 비상 통신망 복구",
        "💰 복구 예산 최적 배분",
    ],
    label_visibility="collapsed",
)
st.sidebar.divider()

with st.sidebar.expander("🔗 모듈 연동 현황"):
    for key in ["risk_map","shelter_assign","transport_order",
                "resource_assign","supply_demand","network_plan","budget_plan"]:
        val = st.session_state.get(key)
        st.write(f"{key}:", "✅" if val else "미실행")

st.title("🚨 재난 대응 통합 의사결정 시스템")
st.caption("가천대학교 알고리즘 기말 프로젝트 | Team GachonAlgorithm10")
st.divider()

if   menu == "🔥 위험구역 확산 예측":   m2_spread.run()
elif menu == "🏠 대피소 수용량 배분":   m1_shelter.run()
elif menu == "🚑 부상자 이송 우선순위": m3_triage.run()
elif menu == "🚒 구조자원 배치":        m4_resource.run()
elif menu == "📦 구호물자 수요 산정":   m6_supply.run()
elif menu == "📡 비상 통신망 복구":     m5_network.run()
elif menu == "💰 복구 예산 최적 배분":  m7_budget.run()
