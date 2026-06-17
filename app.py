"""
대규모 재난 대피 및 물류 최적화 시스템
Streamlit 메인 애플리케이션 — 7개 모듈 통합
담당: 임성엽
"""

import streamlit as st

# 모듈 통합 규약: 각 모듈 __init__.py 에서 run() 진입점을 노출한다.
from modules import m1_shelter, m2_spread, m3_triage, m5_network

st.set_page_config(
    page_title="재난 대응 실시간 최적화 시스템",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# UI/UX 극대화를 위한 Advanced CSS 인젝션 (프리텐다드 폰트 & 카드 UI)
st.markdown("""
    <style>
        /* 1. Material Symbols 폰트 정식 로드 */
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        /* 2. 프리텐다드 폰트 로드 */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        html, body, p, div, h1, h2, h3, h4, h5, h6, label, a {
            font-family: 'Pretendard', sans-serif !important;
        }
        
        .material-symbols-rounded {
            font-family: 'Material Symbols Rounded' !important;
            font-weight: normal;
            font-style: normal;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
        }
        
        .stApp {
            background-color: var(--secondary-background-color);
        }

        /* 사이드바 여백 조절 및 팁 박스 제거를 위한 간소화 */
        [data-testid="stSidebarUserContent"] {
            padding-top: 2rem !important;
        }
        [data-testid="stSidebar"] {
            background-color: var(--background-color);
            border-right: 1px solid var(--secondary-background-color);
        }
        div[role="radiogroup"] > label {
            padding: 0.8rem 1rem;
            background-color: var(--background-color); 
            color: var(--text-color) !important;
            border: 1px solid var(--secondary-background-color);
            border-radius: 12px;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.2s ease;
            cursor: pointer;
            width: 100%;
        }
        div[role="radiogroup"] > label:hover {
            border-color: #3B82F6;
            background-color: var(--secondary-background-color);
            transform: translateX(4px);
        }

        /* 메인 헤더 배너화 */
        .header-banner {
            background: var(--background-color);
            color: var(--text-color);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            margin-bottom: 2rem;
            border-left: 5px solid #1E3A8A;
        }
        .main-title {
            font-weight: 800;
            font-size: 2rem;
            color: var(--text-color);
            margin-bottom: 0.2rem;
            letter-spacing: -0.5px;
        }
        .sub-title {
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.95rem;
            font-weight: 500;
        }
            
        [data-testid="stMetric"] {
            background-color: var(--background-color);
            color: var(--text-color);
            border: 1px solid var(--secondary-background-color);
            padding: 1rem 1.2rem;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
            border-top: 3px solid #3B82F6;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text-color);
        }
    </style>
""", unsafe_allow_html=True)

# --- 메인 헤더 배너 렌더링 ---
# 상태 관리 및 내비게이션 함수
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "HOME"

def navigate_to(page):
    st.session_state["current_page"] = page

# 화면 렌더링 분기

if st.session_state["current_page"] == "HOME":
    # 첫 화면
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none;} 
            [data-testid="stSidebar"] {display: none;} 
            .block-container {
                padding-top: 10vh !important; 
                max-width: 1400px !important; /* 화면 너비 대폭 확대 */
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #0f172a; font-weight: 900; font-size: 3.5rem; letter-spacing: -1.5px;'>🚨 대규모 재난 대피 및 물류 최적화 시스템</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.3rem; margin-bottom: 4rem;'>가천대학교 알고리즘 기말 프로젝트 | Team 알고싶조 <br><br>담당하시는 임무에 맞는 권한으로 시스템에 접속해 주십시오.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; padding: 2.5rem 0 2rem 0;'><span class='material-symbols-rounded' style='font-size: 6rem; color: #1E3A8A;'>public</span><h2 style='margin-top: 20px; color: #1E3A8A; font-weight: 800;'>통합 관제</h2><p style='color: #64748b; font-size: 1.1rem;'>재난 확산 및 전체 현황 모니터링</p></div>", unsafe_allow_html=True)
            st.button("접속하기", key="btn_role_1", use_container_width=True, type="primary", on_click=navigate_to, args=("M2",))

    with col2:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; padding: 2.5rem 0 2rem 0;'><span class='material-symbols-rounded' style='font-size: 6rem; color: #1E3A8A;'>ambulance</span><h2 style='margin-top: 20px; color: #1E3A8A; font-weight: 800;'>대피·구호</h2><p style='color: #64748b; font-size: 1.1rem;'>대피소 배분 및 부상자 이송 스케줄링</p></div>", unsafe_allow_html=True)
            st.button("접속하기", key="btn_role_2", use_container_width=True, type="primary", on_click=navigate_to, args=("M1",))

    with col3:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; padding: 2.5rem 0 2rem 0;'><span class='material-symbols-rounded' style='font-size: 6rem; color: #1E3A8A;'>router</span><h2 style='margin-top: 20px; color: #1E3A8A; font-weight: 800;'>복구 계획</h2><p style='color: #64748b; font-size: 1.1rem;'>비상 통신망 및 인프라 복구 설계</p></div>", unsafe_allow_html=True)
            st.button("접속하기", key="btn_role_3", use_container_width=True, type="primary", on_click=navigate_to, args=("M5",))

else:
    # 대시보드 화면: 사이드바 & 우측 상단 홈 버튼 활성화
    
    # 우측 상단 Home 버튼 단독 배치
    col_empty, col_home = st.columns([8.8, 1.2]) 
    with col_home:
        st.button(":material/home: Home", use_container_width=True, on_click=navigate_to, args=("HOME",))
        
    # 메인 배너 렌더링
    st.markdown("""
    <div class="header-banner" style="margin-top: -0.5rem;">
        <div class="main-title">🚨 대규모 재난 대피 및 물류 최적화 시스템</div>
        <div class="sub-title">가천대학교 알고리즘 기말 프로젝트 | Team 알고싶조</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 3) 사이드바 렌더링
    st.sidebar.markdown("### :material/map: 미션 제어 센터")
    st.sidebar.caption("각 관리 모듈로 전환하여 최적화 알고리즘을 가동하세요.")

    st.sidebar.markdown("#### :material/location_on: 시뮬레이션 지역")
    selected_region = st.sidebar.selectbox("지역 선택", ["서울 송파구", "경기 성남시 (비활성)", "서울 강남구 (비활성)"], label_visibility="collapsed")
    if selected_region != "서울 송파구":
        st.sidebar.error("⚠️ 현재 송파구 공공데이터만 연동되어 있습니다.")
    st.sidebar.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # 라디오 버튼 메뉴 구성
    menu_dict = {
        "M2": ":material/local_fire_department: 위험구역 확산 예측",
        "M1": ":material/night_shelter: 대피소 배정",
        "M3": ":material/ambulance: 부상자 이송",
        "M4": ":material/engineering: 구조자원 배치",
        "M6": ":material/inventory_2: 구호물자 수요",
        "M5": ":material/router: 통신망 복구",
        "M7": ":material/account_balance: 복구 예산 배분"
    }
    
    current_index = list(menu_dict.keys()).index(st.session_state["current_page"])
    
    selected_menu_label = st.sidebar.radio(
        "단계 선택",
        list(menu_dict.values()),
        index=current_index
    )

    # 사이드바 라디오 버튼 클릭 시 상태 업데이트
    for key, label in menu_dict.items():
        if label == selected_menu_label:
            st.session_state["current_page"] = key
            break

    # 글로벌 KPI 렌더링
    st.markdown("#### :material/public: 실시간 통합 모니터링 현황")
    status_keys = ["risk_map", "shelter_assign", "transport_order", "resource_assign", "supply_demand", "network_plan", "budget_plan"]
    completed_count = sum(1 for k in status_keys if k in st.session_state)
    progress_pct = int((completed_count / 7) * 100)
    
    st.progress(progress_pct / 100.0, text=f":material/rocket: 전체 재난 대응 파이프라인 가동률: {progress_pct}% ({completed_count}/7 단계 완료)")
    st.write("")

    # 2. 핵심 요약 KPI
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        if "risk_map" in st.session_state:
            st.metric(":material/local_fire_department: 확산 위험도", "Level 3", delta="예측 완료", delta_color="normal")
        else:
            st.metric(":material/local_fire_department: 확산 위험도", "미실행", delta="대기중", delta_color="off")

    with kpi2:
        if "shelter_assign" in st.session_state:
            st.metric(":material/night_shelter: 누적 대피 인원", f"{len(st.session_state['shelter_assign'])}명", delta="배정 완료", delta_color="normal")
        else:
            st.metric(":material/night_shelter: 누적 대피 인원", "0명", delta="데이터 없음", delta_color="off")

    with kpi3:
        if "transport_order" in st.session_state:
            st.metric(":material/ambulance: 부상자 구조", f"{len(st.session_state['transport_order'])}건", delta="이송 스케줄링", delta_color="normal")
        else:
            st.metric(":material/ambulance: 부상자 구조", "0건", delta="환자 미확인", delta_color="off")

    with kpi4:
        if "network_plan" in st.session_state or "budget_plan" in st.session_state:
            st.metric(":material/engineering: 인프라 복구", "진행 중", delta="자원 투입", delta_color="normal")
        else:
            st.metric(":material/engineering: 인프라 복구", "단선 상태", delta="분석 대기", delta_color="off")

    # 4) 모듈 실행 분기
    if st.session_state["current_page"] == "M1":
        from modules import m1_shelter
        m1_shelter.run()
    elif st.session_state["current_page"] == "M2":
        from modules import m2_spread
        m2_spread.run()
    elif st.session_state["current_page"] == "M3":
        from modules import m3_triage
        m3_triage.run()
    elif st.session_state["current_page"] == "M4":
        from modules import m4_resource
        m4_resource.run()
    elif st.session_state["current_page"] == "M5":
        from modules import m5_network
        m5_network.run()
    elif st.session_state["current_page"] == "M6":
        from modules import m6_supply
        m6_supply.run()
    elif st.session_state["current_page"] == "M7":
        from modules import m7_budget
        m7_budget.run()