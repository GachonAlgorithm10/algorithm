"""
공통 지도 UI 컴포넌트
"""
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

def render_status_badge():
    """컴포넌트 3: M2 위험도 반영 상태 배지"""
    if "risk_map" in st.session_state and st.session_state["risk_map"]:
        st.success("✅ M2 위험도 반영됨")
    else:
        st.warning("⚠️ M2 미실행 — 기본값으로 동작 중")

def render_map(nodes_dict):
    """
    컴포넌트 1 & 2: 송파구 지도 베이스 + 마커 + 히트맵 오버레이
    """
    # 1. 송파구 중심 좌표(37.51, 127.1) 기준 지도 렌더링
    m = folium.Map(location=[37.51, 127.1], zoom_start=14)

    # 2. risk_map 히트맵 오버레이 (session_state 연동)
    risk_map = st.session_state.get("risk_map", {})
    if isinstance(risk_map, dict) and risk_map:
        heat_data = []
        for node_id, risk_score in risk_map.items():
            if node_id in nodes_dict:
                info = nodes_dict[node_id]
                heat_data.append([info["lat"], info["lng"], risk_score])
        
        if heat_data:
            HeatMap(heat_data).add_to(m)

    # 3. 노드 마커 렌더링
    for node_id, info in nodes_dict.items():
        node_type = info.get("type")
        
        # 대피소(파란색)와 병원(빨간색)만 마커 표시
        if node_type == "shelter":
            color = "blue"
            icon_shape = "home"
        elif node_type == "hospital":
            color = "red"
            icon_shape = "plus"
        else:
            continue
            
        lat = info.get("lat")
        lng = info.get("lng")
        name = info.get("name", "알 수 없음")
        capacity = info.get("capacity", 0)

        # 마커 클릭 시 팝업 내용
        popup_html = f"<b>{name}</b><br>수용인원: {capacity}명"
        
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon=icon_shape)
        ).add_to(m)

    # 반응형(use_container_width)으로 지도 렌더링
    st_folium(m, use_container_width=True, height=450, returned_objects=[])

# 각 모듈별 설명 및 알고리즘 세부 데이터
MODULE_GUIDES = {
    "M2": {
        "title": "위험 구역 확산 예측",
        "icon": "local_fire_department",
        "desc": "발화점에서 시작된 재난이 송파구 격자 위로 어떻게 번지는지 예측합니다. 시간대별 위험도를 계산해 이후 모든 대응 단계의 기준 데이터로 전달합니다.",
        "algorithms": ["BFS", "셀룰러 오토마타", "2D 격자"],
        "steps": ["발화점·기상 조건·시뮬레이션 시간 설정", "시뮬레이션 실행 버튼 클릭", "위험도 맵 생성 ➔ 전 모듈로 전달"]
    },
    "M1": {
        "title": "대피소 수용량 배분",
        "icon": "night_shelter",
        "desc": "주민을 가장 적절한 대피소로 배정하여 특정 시설의 초과 수용을 방지하고 이동 동선을 최적화합니다.",
        "algorithms": ["헝가리안 알고리즘", "이분 매칭"],
        "steps": ["대피소 및 시민 데이터 로드", "비용 행렬 계산", "헝가리안 알고리즘 연산 실행", "배정 결과 및 통계 요약 출력"]
    },
    "M3": {
        "title": "부상자 이송 우선순위",
        "icon": "ambulance",
        "desc": "재난 발생 현장의 부상자들을 분류하고, 한정된 구급차 자원을 최적으로 배분하여 이송 시간을 최소화합니다.",
        "algorithms": ["SJF 스케줄링", "가중합 스코어링"],
        "steps": ["부상자 수 및 구급차 자원 설정", "가중합 스코어링 기반 우선순위 환산", "SJF 기반 최적 이송 스케줄 산출"]
    },
    "M4": {
        "title": "구조자원 배치",
        "icon": "engineering",
        "desc": "자원봉사자와 구조 장비를 재난 현장에 최적으로 배치합니다. 위험도가 높은 곳에 자원을 우선 투입합니다.",
        "algorithms": ["헝가리안 알고리즘", "이분 매칭"],
        "steps": ["가용 구조 자원 확인", "위험도 맵 기반 위험도 최상위 현장 추출", "매칭 알고리즘 실행", "자원 배치 현황 시각화"]
    },
    "M5": {
        "title": "비상 통신망 복구",
        "icon": "router",
        "desc": "재난으로 파괴된 통신망을 최소 비용으로 복구합니다. 대피소와 병원을 거점으로 삼고, 단일 장애점을 탐지하여 안정적인 망을 구축합니다.",
        "algorithms": ["크루스칼 MST", "Tarjan SPOF"],
        "steps": ["통신 거점(대피소/병원) 노드 로드", "크루스칼 MST 구축", "Tarjan 기반 단일 장애점 탐지", "복구 경로 시각화"]
    },
    "M6": {
        "title": "구호물자 수요 산정",
        "icon": "inventory_2",
        "desc": "대피소별 배정 인원을 기반으로 물, 식량, 의약품 등의 수요를 계산하고 효율적으로 배분합니다.",
        "algorithms": ["Greedy 알고리즘"],
        "steps": ["대피소별 배정 인원 연동", "대피소별 필요 물자량 산정", "우선순위 기반 물자 배분 실행", "배분 결과 요약"]
    },
    "M7": {
        "title": "복구 예산 최적 배분",
        "icon": "account_balance",
        "desc": "한정된 복구 예산으로 피해 지역의 복구 효과를 최대화합니다. 위험도를 피해 심각도로 환산하여 예산을 최적 배분합니다.",
        "algorithms": ["0-1 Knapsack DP"],
        "steps": ["가용 예산 한도 설정", "위험도 맵 기반 복구 효과 가중치 계산", "Knapsack DP 알고리즘 실행", "최적 배분 결과 출력"]
    }
}

def render_module_guide(module_key):
    import streamlit as st
    guide = MODULE_GUIDES.get(module_key)
    if not guide:
        return
        
    tags_html = "".join([f'<span class="algo-tag">{algo}</span>' for algo in guide["algorithms"]])
    steps_html = "".join([f'<li><span class="step-num">{idx}</span> {step}</li>' for idx, step in enumerate(guide["steps"], 1)])
    
    st.markdown(f"""
    <style>
        .guide-container {{ display: flex; gap: 1.2rem; margin-bottom: 1rem; margin-top: 1rem; }}
        .guide-card {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 1.5rem; flex: 1;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            display: flex;
            flex-direction: column;
        }}
        .guide-title {{
            font-size: 1.15rem; 
            font-weight: 700; color: #0f172a;
            margin-bottom: 1rem; display: flex; align-items: center;
        }}
        .red-bar {{ color: #ef4444; font-weight: 900; margin-right: 10px; font-size: 1.2rem; }}
        .guide-text {{ 
            color: #475569; 
            font-size: 1.05rem; 
            line-height: 1.7; margin-bottom: 1.5rem; 
        }}
        .tag-wrapper {{ display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: auto;}}
        .algo-tag {{
            background-color: #f8fafc; color: #475569; padding: 0.4rem 0.9rem;
            border: 1px solid #cbd5e1;
            border-radius: 20px; 
            font-size: 0.9rem; 
            font-weight: 600;
        }}
        .step-list {{ list-style: none; padding: 0; margin: 0; }}
        .step-list li {{ 
            margin-bottom: 1rem; display: flex; align-items: center; 
            font-size: 1.05rem; 
            color: #475569; 
        }}
        .step-num {{
            background-color: #f1f5f9; color: #64748b; 
            width: 26px; height: 26px; 
            border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
            font-size: 0.9rem; 
            font-weight: 700; margin-right: 12px; flex-shrink: 0;
        }}
        .info-banner {{
            background-color: #eff6ff; color: #1e3a8a; padding: 1rem 1.5rem;
            border-radius: 8px; 
            font-size: 1.05rem; 
            font-weight: 500;
            display: flex; align-items: center; margin-top: 1rem;
        }}
    </style>

    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; margin-top: 1rem;">
        <div style="background-color: #fef2f2; width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);">
            <span class="material-symbols-rounded" style="color: #ef4444; font-size: 28px;">{guide['icon']}</span>
        </div>
        <h2 style="margin: 0; padding: 0; font-weight: 800; color: var(--text-color); font-size: 1.9rem; letter-spacing: -0.5px;">{guide['title']}</h2>
    </div>

    <div class="guide-container">
        <div class="guide-card">
            <div class="guide-title"><span class="red-bar">|</span> 이 단계가 하는 일</div>
            <div class="guide-text">{guide['desc']}</div>
            <div class="tag-wrapper">{tags_html}</div>
        </div>
        <div class="guide-card">
            <div class="guide-title"><span class="red-bar">|</span> 실행 순서</div>
            <ul class="step-list">{steps_html}</ul>
        </div>
    </div>
    <div class="info-banner">
        ← 왼쪽 사이드바에서 설정을 조정한 뒤 실행 버튼을 눌러주세요
    </div>
    """, unsafe_allow_html=True)