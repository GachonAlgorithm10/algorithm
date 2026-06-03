"""
대규모 재난 대피 및 물류 최적화 시스템
Streamlit 메인 애플리케이션 — 4개 모듈 통합
담당: 임성엽
"""
import streamlit as st
from modules.m1_shelter import shelter
from modules.m2_spread import spread
from modules.m3_triage import triage
from modules.m5_network import network

st.set_page_config(
    page_title="재난 대피 최적화 시스템",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 대규모 재난 대피 및 물류 최적화 시스템")
st.caption("가천대학교 알고리즘 기말 프로젝트 | Team GachonAlgorithm10")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 M1 대피소 배분",
    "🔥 M2 위험 구역 확산",
    "🚑 M3 부상자 이송",
    "📡 M5 비상 통신망",
])

with tab1:
    shelter.run()

with tab2:
    spread.run()

with tab3:
    triage.run()

with tab4:
    network.run()
