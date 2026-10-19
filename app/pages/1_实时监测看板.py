# -*- coding: utf-8 -*-
import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import style, sim_data

st.markdown(style.css(), unsafe_allow_html=True)
st.markdown(style.page_header(
    "实时监测看板",
    "多节点运行状态 · 模拟主监测视图 · SOS 本地快速告警",
    "01 · 感知层实况"), unsafe_allow_html=True)

if "seed" not in st.session_state:
    st.session_state.seed = 0

ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 2])
with ctrl1:
    if st.button("立即刷新", use_container_width=True):
        st.session_state.seed += 1
        st.rerun()
with ctrl2:
    st.checkbox("模拟实时推送（每 3 秒）", key="live")
with ctrl3:
    st.markdown('<div class="sg-mini" style="padding-top:8px">刷新或开启推送后，各节点状态与画面将按新随机种子重新生成（均为模拟数据）。</div>',
                unsafe_allow_html=True)
if st.session_state.get("live"):
    time.sleep(3)
    st.session_state.seed += 1
    st.rerun()

nodes = sim_data.gen_nodes(st.session_state.seed)
online = sum(1 for n in nodes if n["status"] == "在线")
alarm = sum(1 for n in nodes if n["status"] == "告警")
people = sum(n["people"] for n in nodes)
avg_lat = round(sum(n["latency_ms"] for n in nodes) / len(nodes))

st.markdown(style.section("全网概览"), unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(style.kpi(f"{online}/{len(nodes)}", "在线节点"), unsafe_allow_html=True)
with k2:
    st.markdown(style.kpi(str(alarm), "告警节点", "需关注节点数"), unsafe_allow_html=True)
with k3:
    st.markdown(style.kpi(str(people), "当前监测人数", "全网实时汇总"), unsafe_allow_html=True)
with k4:
    st.markdown(style.kpi(f"{avg_lat} ms", "平均推理延迟", "模拟值 · 目标 <200ms"), unsafe_allow_html=True)

for n in [x for x in nodes if x["sos"]]:
    st.markdown(style.note(
        f'<b>SOS 本地快速告警</b>：{n["name"]} 检测到【挥手呼救】，'
        f'边缘端 &lt;200ms 本地触发，未经云端，体现隐私优先与低延迟设计。'),
        unsafe_allow_html=True)

st.markdown(style.section("节点状态", "边缘智能层各节点运行实况"), unsafe_allow_html=True)
cols = st.columns(3)
for i, n in enumerate(nodes):
    with cols[i % 3]:
        st.markdown(
            f'<div class="sg-card">'
            f'<div class="sg-h">{n["name"]} {style.status_badge(n["status"])}</div>'
            f'<div class="sg-p">{n["id"]} · {n["type"]}场景</div>'
            f'<div class="rowline"><span>当前人数</span><b>{n["people"]}</b></div>'
            f'<div class="rowline"><span>最近行为</span><b>{n["behavior"]}</b></div>'
            f'<div class="rowline"><span>推理延迟</span><b>{n["latency_ms"]} ms</b></div>'
            f'<div class="rowline"><span>隐私保护</span><b>已本地脱敏</b></div>'
            f'</div>',
            unsafe_allow_html=True)

st.markdown(style.section("主监测视图", "检测框 + 骨架示意 + 扫描线（模拟画面，人脸已本地脱敏）"), unsafe_allow_html=True)
labels = [f'{n["name"]}（{n["id"]}）' for n in nodes]
sel = st.selectbox("选择节点", labels)
node = nodes[labels.index(sel)]
n_obj = max(2, node["people"] % 5)
view = (
    '<div class="sg-mon">'
    '<div class="hud hud-top"><span class="rec">● REC</span>'
    f'<span>{node["name"]} · 模拟画面（人脸已本地脱敏）</span></div>'
    '<div class="scan"></div>'
    '<div class="box" style="--c:#97C459;left:12%;top:34%;width:19%;height:46%">'
    '<span class="tag">person 0.94</span></div>'
    f'<div class="box" style="--c:#EF9F27;left:52%;top:44%;width:17%;height:38%">'
    f'<span class="tag">{node["behavior"]} 0.88</span></div>'
    '<div class="box" style="--c:#85B7EB;left:78%;top:54%;width:11%;height:30%">'
    '<span class="tag">person 0.91</span></div>'
    '<div class="hud hud-bottom">'
    f'<span class="chip"><span class="dot" style="background:#97C459"></span>正常</span>'
    f'<span class="chip"><span class="dot" style="background:#EF9F27"></span>{node["behavior"]}</span>'
    f'<span class="chip"><span class="dot" style="background:#85B7EB"></span>正常</span>'
    f'<span>检测目标 {n_obj} · 主导行为 {node["behavior"]} · 延迟 {node["latency_ms"]} ms</span>'
    '</div></div>'
)
st.components.v1.html(view, height=360)
st.markdown(style.footer(), unsafe_allow_html=True)
