# 담당: 임성엽 / GachonAlgorithm10
"""core/viz_util.py — Plotly 공통 스타일 헬퍼 (전 모듈 테마 자동 연동)"""
from __future__ import annotations
import streamlit as st


def plotly_template() -> str:
    """현재 Streamlit 테마(light/dark)에 맞는 Plotly 템플릿 반환."""
    try:
        return "plotly_dark" if st.context.theme.type == "dark" else "plotly_white"
    except Exception:
        base = st.get_option("theme.base") or "light"
        return "plotly_dark" if base == "dark" else "plotly_white"


def style_fig(fig, height: int | None = None):
    """투명 배경 + 테마 템플릿 + Pretendard 폰트 적용."""
    fig.update_layout(
        template=plotly_template(),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    if height:
        fig.update_layout(height=height)
    return fig


def show(fig, **kwargs):
    """st.plotly_chart 표준 호출. theme=None 으로 위 수동 템플릿을 그대로 사용."""
    st.plotly_chart(fig, use_container_width=True, theme=None, **kwargs)
