"""
============================================================
module_m3_triage / ui_triage.py
부상자 이송 모듈의 Streamlit 화면 (M3 탭)
담당: 임성엽
============================================================
단독 실행:   streamlit run module_m3_triage/ui_triage.py
app.py 통합: render_triage_tab() 를 호출
"""
import random
import plotly.graph_objects as go
from core.viz_util import style_fig, show

# 패키지/폴더 양쪽 실행 지원
try:
    from .optimizer import run_triage, generate_sample_patients, results_to_rows, Patient
except ImportError:
    from optimizer import run_triage, generate_sample_patients, results_to_rows, Patient


def _real_to_patient(raw: dict, idx: int) -> "Patient":
    """실데이터 dict → Patient 객체 변환 어댑터.
    실데이터 키: id, location_node, severity, wait_minutes
    Patient 키:  pid, severity, wait_time, transport_time
    transport_time 은 거리 util 통합 전까지 임시 랜덤값 사용.
    """
    pid_str = str(raw.get("id", idx))
    try:
        pid = int("".join(filter(str.isdigit, pid_str)) or idx)
    except (ValueError, TypeError):
        pid = idx
    return Patient(
        pid=pid,
        severity=int(raw.get("severity", 3)),
        wait_time=int(raw.get("wait_minutes", 0)),
        transport_time=random.randint(5, 40),
    )


def render_triage_tab():
    """app.py 의 M3 탭에서 이 함수를 호출한다."""
    import streamlit as st

    from core.map_util import render_module_guide

    # --- 사이드바 입력 컨트롤 ---
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    use_real = True

    n_general = st.sidebar.slider("일반 구급차", 1, 5, 2)
    n_critical = st.sidebar.slider("중증 전담 구급차", 0, 3, 1)
    run_btn = st.sidebar.button("▶ 시뮬레이션 실행", key="triage_run_btn", type="primary", use_container_width=True)

    ambulances = [{"id": f"G{i+1}", "type": "general"} for i in range(n_general)]
    ambulances += [{"id": f"C{i+1}", "type": "critical"} for i in range(n_critical)]

    if not ambulances:
        st.warning("⚠️ 구급차를 최소 1대 이상 설정하세요.")
        return

    if run_btn:
        # --- 데이터 로드 ---
        if use_real:
            try:
                from core.data_loader import DataLoader
                raw_list = DataLoader().patients
                random.seed(42)
                patients = [_real_to_patient(r, idx) for idx, r in enumerate(raw_list)]
            except Exception as e:
                st.warning(f"⚠️ 실데이터 로드 실패 — 더미 데이터로 대체합니다. ({e})")
                patients = generate_sample_patients(n=12)
        else:
            patients = generate_sample_patients(n=n_patients)

        result = run_triage(patients, ambulances)
        st.session_state["transport_order"] = result

        st.divider()
        st.subheader("📊 결과")

        ranked = sorted(result, key=lambda p: p.score, reverse=True)
        if ranked:
            t = ranked[0]
            st.error(
                f"🚑 최우선 이송 대상: 환자 #{t.pid} · 중증도 {t.severity} · 대기 {t.wait_time}분 "
                f"→ {t.assigned} 구급차 배정"
            )

        total = len(result)
        assigned_n = sum(1 for p in result if p.assigned)
        avg_wait = round(sum(p.wait_time for p in result) / total, 1) if total else 0
        avg_score = round(sum(p.score for p in result) / total, 3) if total else 0
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("총 부상자", f"{total} 명")
        k2.metric("배정 완료", f"{assigned_n} 명")
        k3.metric("평균 대기", f"{avg_wait} 분")
        k4.metric("평균 우선순위", avg_score)

        st.markdown("#### 이송 우선순위 큐 (상위 15)")
        topN = ranked[:15][::-1]  # 가로 막대 상단이 1순위가 되도록 역순
        fig = go.Figure([go.Bar(
            x=[p.score for p in topN],
            y=[f"#{p.pid}" for p in topN],
            orientation="h",
            marker=dict(color=[p.severity for p in topN], colorscale="Reds",
                        cmin=1, cmax=5, colorbar=dict(title="중증도")),
            customdata=[[p.severity, p.wait_time, p.assigned or "-"] for p in topN],
            hovertemplate=("환자 %{y}<br>우선순위 %{x:.3f}<br>중증도 %{customdata[0]}"
                           "<br>대기 %{customdata[1]}분<br>배정 %{customdata[2]}<extra></extra>"),
        )])
        fig.update_layout(xaxis_title="우선순위 점수", yaxis_title="환자")
        show(style_fig(fig, height=420))

        st.caption("💡 이송시간은 현재 시뮬레이션 값이며, 통합 단계에서 거리 util(graph_data 기반) 실제 값으로 교체됩니다.")
        with st.expander("📋 상세 이송 우선순위 (전체)"):
            st.dataframe(results_to_rows(result), use_container_width=True, height=360)
    else:
        st.write("")
        render_module_guide("M3")


# 단독 실행 (streamlit run)
if __name__ == "__main__":
    render_triage_tab()
