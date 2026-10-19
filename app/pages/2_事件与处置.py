# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import style, sim_data

st.markdown(style.css(), unsafe_allow_html=True)
st.markdown(style.page_header(
    "异常事件与处置",
    "异常事件列表 · 感知—理解—服务时间线 · 云端服务建议",
    "02 · 事件闭环"), unsafe_allow_html=True)

if "events" not in st.session_state:
    st.session_state.events = sim_data.gen_events()
events = st.session_state.events

st.markdown(style.section("事件列表", "全网异常事件实时汇总"), unsafe_allow_html=True)
df = pd.DataFrame(events)[["event_id", "type", "node", "date", "time", "confidence", "status"]]
style.sg_table(
    df, use_container_width=True, hide_index=True,
    column_config={"confidence": st.column_config.ProgressColumn("置信度", format="%.2f", min_value=0, max_value=1)},
)

ids = [e["event_id"] for e in events]
sel = st.selectbox("选择事件查看详情", ids)
ev = next(e for e in events if e["event_id"] == sel)

st.markdown(style.section("事件详情"), unsafe_allow_html=True)
st.markdown(
    f'<div class="sg-card"><div class="sg-h" style="font-size:16px">{ev["event_id"]} {style.status_badge(ev["status"])}</div>'
    f'<div style="margin-top:8px">'
    f'<span class="badge b-info">{ev["type"]}</span>'
    f'<span class="badge b-gray">{ev["node"]}</span>'
    f'<span class="badge b-gray">{ev["date"]} {ev["time"]}</span>'
    f'<span class="badge b-warn">置信度 {ev["confidence"]}</span>'
    f'</div></div>',
    unsafe_allow_html=True)

st.markdown(style.section("处置时间线", "感知 — 理解 — 服务"), unsafe_allow_html=True)
tl = [
    ("T0 边缘检出", "<200ms 本地推理识别异常，触发本地告警"),
    ("T1 本地脱敏", "人脸模糊化，仅上传行为特征向量"),
    ("T2 云端理解", "LLM 结合知识图谱进行语义理解与推理（约1.5s，模拟）"),
    ("T3 生成建议", "输出结构化个性化服务建议"),
    ("T4 触达联动", "通知家属 / 派单离退休工作处 / 联动校医院"),
    ("T5 处置完结", "记录归档，纳入适老化指数统计"),
]
for i, (t, d) in enumerate(tl):
    st.markdown(
        f'<div class="sg-card" style="padding:10px 16px;margin-bottom:8px">'
        f'<div class="rowline"><span><span class="badge b-primary">{i+1}</span> <b>{t}</b></span>'
        f'<span class="sg-mini">{d}</span></div></div>',
        unsafe_allow_html=True)

st.markdown(style.section("云端服务建议", "模拟 LLM 输出 · 结构化个性化建议"), unsafe_allow_html=True)
sug = sim_data.suggestion_for(ev["type"])
cols = st.columns(2)
for i, (k, v) in enumerate(sug):
    with cols[i % 2]:
        st.markdown(f'<div class="sg-card"><div class="sg-h">{k}</div><div class="sg-p">{v}</div></div>',
                    unsafe_allow_html=True)

st.markdown(style.note(
    '该事件已本地人脸脱敏，云端仅保存行为特征向量；数据采用 AES-256 加密存储，'
    '体现「隐私优先」的架构设计原则。'), unsafe_allow_html=True)

st.markdown(style.section("处置操作", "模拟管理者端处置动作"), unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)


def set_status(s):
    for e in st.session_state.events:
        if e["event_id"] == sel:
            e["status"] = s
    st.rerun()


with b1:
    if st.button("通知家属", use_container_width=True):
        st.toast("已通知家属（模拟）")
with b2:
    if st.button("派单离退休处", use_container_width=True):
        st.toast("已派单至离退休工作处（模拟）")
with b3:
    if st.button("标记已完结", use_container_width=True):
        set_status("已完结")
st.markdown(style.footer(), unsafe_allow_html=True)
