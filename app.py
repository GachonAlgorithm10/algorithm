"""
대규모 재난 대피 및 물류 최적화 시스템
Streamlit 메인 애플리케이션 — 4개 모듈 통합
담당: 임성엽
"""
import streamlit as st

# 모듈 통합 규약: 각 모듈 __init__.py 에서 run() 진입점을 노출한다.
from modules import m1_shelter, m2_spread, m3_triage, m5_network

st.set_page_config(
    page_title="재난 대피 최적화 시스템",
    page_icon="🚨",
    layout="wide"
)

st.sidebar.title("🚨 재난 대응 시스템")
menu = st.sidebar.radio("모듈 선택", [
    "🏠 대피소 수용량 배분",
    "🔥 위험 구역 확산 예측",
    "🚑 부상자 이송 우선순위",
    "📡 비상 통신망 설계",
])
st.sidebar.divider()

st.title("🚨 대규모 재난 대피 및 물류 최적화 시스템")
st.caption("가천대학교 알고리즘 기말 프로젝트 | Team GachonAlgorithm10")
st.divider()

if menu == "🏠 대피소 수용량 배분":
    m1_shelter.run()
elif menu == "🔥 위험 구역 확산 예측":
    m2_spread.run()
elif menu == "🚑 부상자 이송 우선순위":
    m3_triage.run()
elif menu == "📡 비상 통신망 설계":
    m5_network.run()
