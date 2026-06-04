"""
============================================================
module_m3_triage / ui_triage.py
부상자 이송 모듈의 Streamlit 화면 (M3 탭)
담당: 임성엽
============================================================
단독 실행:   streamlit run module_m3_triage/ui_triage.py
app.py 통합: render_triage_tab() 를 호출
"""

# 패키지/폴더 양쪽 실행 지원
try:
    from .optimizer import run_triage, generate_sample_patients, results_to_rows
except ImportError:
    from optimizer import run_triage, generate_sample_patients, results_to_rows


def render_triage_tab():
    """app.py 의 M3 탭에서 이 함수를 호출한다."""
    import streamlit as st

    st.subheader("M3 · 부상자 이송 우선순위")
    st.caption("중증도 우선 배정(가중합+힙+세그먼트 트리) → 구급차별 SJF 운행")

    # --- 입력 컨트롤 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        n_patients = st.slider("부상자 수", 4, 40, 12)
    with col2:
        n_general = st.slider("일반 구급차", 1, 5, 2)
    with col3:
        n_critical = st.slider("중증 전담 구급차", 0, 3, 1)

    ambulances = [{"id": f"G{i+1}", "type": "general"} for i in range(n_general)]
    ambulances += [{"id": f"C{i+1}", "type": "critical"} for i in range(n_critical)]

    if not ambulances:
        st.warning("구급차를 최소 1대 이상 설정하세요.")
        return

    # --- 실행 ---
    patients = generate_sample_patients(n=n_patients)
    result = run_triage(patients, ambulances)

    # --- 결과 테이블 ---
    st.dataframe(results_to_rows(result), use_container_width=True)
    st.info("이송시간은 현재 시뮬레이션 값입니다. 통합 단계에서 "
            "거리 util(graph_data 기반)의 실제 값으로 교체됩니다.")


# 단독 실행 (streamlit run)
if __name__ == "__main__":
    render_triage_tab()
