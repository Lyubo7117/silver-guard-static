# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import style, sim_data

st.markdown(style.css(), unsafe_allow_html=True)
st.markdown(style.page_header(
    "管理者数据看板",
    "适老化指数 · 事件趋势 · 类型分布 · 响应分析",
    "04 · 云端服务层"), unsafe_allow_html=True)

# 统一 Plotly 浅色主题
LAYOUT = dict(
    font=dict(family="sans-serif", size=12, color="#5F5E5A"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(style.kpi("128", "本月异常事件", "模拟值"), unsafe_allow_html=True)
with k2:
    st.markdown(style.kpi("21", "其中跌倒事件", "最高优先级类型"), unsafe_allow_html=True)
with k3:
    st.markdown(style.kpi("1.8 min", "平均响应时长", "目标 < 3 min"), unsafe_allow_html=True)
with k4:
    st.markdown(style.kpi("94%", "处置及时率", "目标 ≥ 90%"), unsafe_allow_html=True)
with k5:
    st.markdown(style.kpi("82 / 100", "校园适老化指数", "综合评估"), unsafe_allow_html=True)

st.markdown(style.section("事件趋势", "近 30 天 · 模拟数据"), unsafe_allow_html=True)
trend = sim_data.gen_trend()
fig_trend = px.bar(
    trend, x="date", y=["跌倒", "其他异常"],
    color_discrete_map={"跌倒": "#A32D2D", "其他异常": "#EF9F27"},
    barmode="stack", height=300,
)
fig_trend.update_layout(**LAYOUT, legend_title_text="")
st.plotly_chart(fig_trend, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(style.section("事件类型分布"), unsafe_allow_html=True)
    dist = sim_data.gen_type_dist()
    fig_type = px.bar(dist, y="类型", x="次数", orientation="h", height=300,
                      color="次数", color_continuous_scale=["#9FE1CB", "#0F6E56"])
    fig_type.update_layout(**LAYOUT, coloraxis_showscale=False)
    st.plotly_chart(fig_type, use_container_width=True)
with col_b:
    st.markdown(style.section("各节点事件数"), unsafe_allow_html=True)
    nb = sim_data.gen_node_bar()
    fig_node = px.bar(nb, y="节点", x="事件数", orientation="h", height=300,
                      color="事件数", color_continuous_scale=["#B5D4F4", "#185FA5"])
    fig_node.update_layout(**LAYOUT, coloraxis_showscale=False)
    st.plotly_chart(fig_node, use_container_width=True)

col_c, col_d = st.columns(2)
with col_c:
    st.markdown(style.section("校园适老化指数"), unsafe_allow_html=True)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=82,
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#0F6E56"},
               "steps": [{"range": [0, 60], "color": "#FCEBEB"},
                         {"range": [60, 80], "color": "#FAEEDA"},
                         {"range": [80, 100], "color": "#E1F5EE"}]},
    ))
    gauge.update_layout(height=300, font=dict(color="#5F5E5A"),
                        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(gauge, use_container_width=True)
with col_d:
    st.markdown(style.section("告警响应时长分布", "模拟数据"), unsafe_allow_html=True)
    rng = np.random.default_rng(3)
    resp = rng.lognormal(mean=np.log(110), sigma=0.35, size=400).astype(int)
    fig_resp = px.histogram(resp, nbins=24, height=300,
                            color_discrete_sequence=["#1D9E75"])
    fig_resp.update_layout(**LAYOUT, xaxis_title="响应时长（ms）", yaxis_title="频次",
                           showlegend=False)
    st.plotly_chart(fig_resp, use_container_width=True)

st.markdown(style.note(
    '适老化指数综合设施覆盖率、事件密度、响应时长与处置及时率等维度，'
    '用于高校端校园适老化治理评估（当前为模拟值）。'), unsafe_allow_html=True)
st.markdown(style.footer(), unsafe_allow_html=True)
