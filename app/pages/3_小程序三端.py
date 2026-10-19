# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import style

st.markdown(style.css(), unsafe_allow_html=True)
st.markdown(style.page_header(
    "「银发守护」小程序 · 三端原型",
    "老人端 / 家属端 / 管理者端界面原型（静态高保真示意，数据为模拟）",
    "03 · 用户交互层"), unsafe_allow_html=True)


def phone(inner):
    return ('<div class="phone">'
            '<div class="status"><span class="sig">●●● ○ 5G</span><span>9:41</span></div>'
            f'<div class="screen">{inner}</div>'
            '<div class="homei"></div></div>')


t1, t2, t3 = st.tabs(["老人端", "家属端", "管理者端"])

with t1:
    elder = phone(
        '<div style="text-align:center;font-size:15px;font-weight:600;color:#2C2C2A">下午好，王奶奶</div>'
        '<div class="sg-mini" style="text-align:center;margin-bottom:8px">院士楼 · 东花园</div>'
        '<div class="sg-card" style="background:#E1F5EE;border-color:#9FE1CB;margin-bottom:8px">'
        '<div class="sg-h" style="color:#085041">当前状态：安全</div>'
        '<div class="sg-p">周边人流正常，无需担心</div></div>'
        '<div class="bigbtn red">一键求助 SOS</div>'
        '<div style="display:flex;gap:8px;margin-top:6px">'
        '<div class="sg-card" style="flex:1;text-align:center;margin:0"><div class="sg-h">语音交互</div><div class="sg-mini">说话即可</div></div>'
        '<div class="sg-card" style="flex:1;text-align:center;margin:0"><div class="sg-h">服务导航</div><div class="sg-mini">就近休息点</div></div>'
        '</div>'
        '<div class="sg-card" style="margin-top:8px"><div class="sg-h">今日提醒</div>'
        '<div class="sg-p">下午4点校医院义诊，步行约300米</div></div>'
    )
    st.components.v1.html(elder, height=560)

with t2:
    family = phone(
        '<div class="sg-card"><div class="sg-h">张爷爷 · 78岁</div>'
        '<div style="margin:6px 0"><span class="badge b-ok">状态：安全</span>'
        '<span class="badge b-gray">西家属区 · 中心广场</span></div>'
        '<div class="rowline"><span>今日步数</span><b>3,240</b></div>'
        '<div class="rowline"><span>今日事件</span><b>1 次（已处置）</b></div></div>'
        '<div class="sg-card" style="border-left:4px solid #A32D2D">'
        '<div class="sg-h" style="color:#A32D2D">异常告警推送</div>'
        '<div class="sg-p">14:32 检测到【长时间静止】，已自动核验并通知您</div>'
        '<div class="bigbtn red" style="margin-top:8px">查看实时定位</div></div>'
        '<div class="sg-card"><div class="sg-h">健康周报</div>'
        '<div class="sg-p">本周活动规律，建议增加午间休息</div></div>'
    )
    st.components.v1.html(family, height=560)

with t3:
    admin = phone(
        '<div style="display:flex;gap:8px">'
        '<div class="sg-kpi" style="flex:1;margin:0"><div class="v">18</div><div class="l">今日事件</div></div>'
        '<div class="sg-kpi" style="flex:1;margin:0"><div class="v">96%</div><div class="l">设备在线</div></div></div>'
        '<div class="sg-card" style="margin-top:8px"><div class="sg-h">待处置事件</div>'
        '<div class="rowline"><span>跌倒 · 院士楼东花园</span><span class="badge b-err">新</span></div>'
        '<div class="rowline"><span>独自徘徊 · 老干部活动中心</span><span class="badge b-warn">处理中</span></div>'
        '<div class="rowline"><span>异常聚集 · 南湖步道</span><span class="badge b-warn">处理中</span></div></div>'
        '<div class="sg-card"><div class="sg-h">设备管理</div>'
        '<div class="rowline"><span>感知终端</span><b>6 在线 / 0 离线</b></div>'
        '<div class="rowline"><span>边缘算力负载</span><b>正常</b></div></div>'
        '<div class="bigbtn">进入数据看板</div>'
    )
    st.components.v1.html(admin, height=560)

st.markdown(style.section("三端协同逻辑", "同一事件在三端的流转"), unsafe_allow_html=True)
st.markdown(
    '<div class="sg-flow">'
    '<div class="step"><div class="n">老</div><div class="t">老人端</div>'
    '<div class="d">大字体、大按钮、语音优先；异常时自动弹窗确认并提供一键 SOS 兜底。</div></div>'
    '<div class="step"><div class="n">属</div><div class="t">家属端</div>'
    '<div class="d">实时查看老人状态与定位，接收告警推送与处置进展，按周收到健康周报。</div></div>'
    '<div class="step"><div class="n">管</div><div class="t">管理者端</div>'
    '<div class="d">全网事件处置队列、设备运维监控、适老化指数看板与调度派单。</div></div>'
    '</div>',
    unsafe_allow_html=True)
st.markdown(style.footer(), unsafe_allow_html=True)
