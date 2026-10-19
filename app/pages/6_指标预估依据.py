# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import style

st.markdown(style.css(), unsafe_allow_html=True)
st.markdown(style.page_header(
    "指标预估依据",
    "说明书核心设计指标的「预估推导链条 + 公开基准来源」",
    "06 · 预估依据"), unsafe_allow_html=True)

st.markdown(style.note(
    '本页所有数值均为<b>预估值 / 公开基准</b>，不是本系统实测结果，'
    '用途是证明「目标设定在合理范围内」。获得实测数据后将逐项替换为实测值并标注。'
    '完整推导见配套文档 docs/技术指标预估依据.md。'), unsafe_allow_html=True)

# ---------------- 指标总览 ----------------
st.markdown(style.section("指标总览"), unsafe_allow_html=True)
overview = pd.DataFrame([
    ["多模态行为检测 mAP", "≥ 90%", "取同类公开数据集文献报告区间的下沿，设定偏保守", "强"],
    ["边缘端推理延迟", "< 200 ms", "单模型 CPU+ONNX 官方基准已 131.8ms，边缘量化后余量 25–50%", "强"],
    ["12 类异常识别", "12 类", "封闭类别集 + CLIP 零样本模板 + 规则兜底，工程可覆盖", "中"],
    ["服务推荐准确率", "92%", "封闭意图域 RAG 系统常见 85–95%，取区间中值", "中"],
], columns=["技术指标", "设计目标值", "预估结论", "依据强度"])
style.sg_table(overview, use_container_width=True, hide_index=True)

# ---------------- 指标 1 ----------------
st.markdown(style.section("① 多模态行为检测 mAP ≥ 90%"), unsafe_allow_html=True)
st.markdown(
    '<div class="sg-card"><div class="sg-p">'
    '<b>1.</b> 跌倒检测在主流公开数据集上已有充分验证：Le2i / UR-Fall 上多数方法报告 '
    '<b>90%–99%</b> 的准确率（如 Le2i 数据集提出论文 Charfi et al., JEI 2013 及其后续工作），'
    '90% 位于该区间<b>下沿</b>。<br>'
    '<b>2.</b> 本场景任务难度低于开放场景：固定机位、画面稳定、待识别类别少'
    '（跌倒 vs 正常为主）、背景相对固定，域内泛化压力小。<br>'
    '<b>3.</b> 技术路线（RT-DETR + CLIP 多模态融合 + 自采数据微调）相比纯 RGB 单模态基线'
    '具备冗余信息增益，指标有上探空间。<br>'
    '<b>结论：</b>取文献区间下沿，属稳健可达目标，而非激进指标。'
    '</div></div>',
    unsafe_allow_html=True)

# ---------------- 指标 2 ----------------
st.markdown(style.section("② 边缘端推理延迟 < 200 ms"), unsafe_allow_html=True)
chain = pd.DataFrame([
    ["① 单模型推理", "Ultralytics 官方基准：YOLOv8n-pose，640 输入，batch=1，CPU+ONNX", "≈ 132 ms"],
    ["② 边缘端加速", "Jetson Nano + TensorRT INT8 较同设备 CPU 快 2–4 倍（社区普遍基准）", "≈ 40–80 ms"],
    ["③ 系统级合计", "感知（检测+姿态）→ 规则/分类头 → 本地脱敏 → 事件上报，全链路叠加", "≈ 100–150 ms"],
    ["④ 对照目标", "设计目标 < 200 ms", "余量约 25–50%"],
], columns=["环节", "预估依据", "预估耗时"])
style.sg_table(chain, use_container_width=True, hide_index=True)
st.markdown(
    '<div class="sg-card"><div class="sg-p">来源：Ultralytics 官方模型基准表（YOLOv8n-pose：3.3M 参数 / 9.2 GFLOPs / '
    'CPU ONNX 131.8ms）；Jetson 加速倍数为社区公开基准的通用经验区间。'
    '<b>结论：</b>即使不做量化优化，单模型 CPU ONNX 延迟已低于 200ms；'
    '上边缘端 + TensorRT INT8 后余量充足。Jetson 实测值待补。</div></div>',
    unsafe_allow_html=True)

# ---------------- 指标 3 ----------------
st.markdown(style.section("③ 12 类异常行为识别"), unsafe_allow_html=True)
st.markdown(
    '<div class="sg-card"><div class="sg-p">'
    '<b>1.</b> 类别集封闭且枚举明确（跌倒、久坐不起、徘徊、挥手求助、聚集、奔跑等，'
    '以说明书枚举为准），非开放域识别。<br>'
    '<b>2.</b> CLIP 零样本图文匹配：每类配置 3–5 个文本模板即可覆盖同义表述，'
    '封闭类别集下逐类 F1 预估 ≥85%。<br>'
    '<b>3.</b> 高置信场景（如明显跌倒）叠加规则 / 时序确认兜底，保证关键事件不漏报。<br>'
    '<b>4.</b> 多模态融合（RGB + 姿态 + 时序）相对单模态基线有增益空间。<br>'
    '<b>结论：</b>12 类为工程可枚举的封闭集，「零样本 + 规则兜底 + 后续微调」可稳定覆盖，'
    '需以自采数据持续校准。'
    '</div></div>',
    unsafe_allow_html=True)

# ---------------- 指标 4 ----------------
st.markdown(style.section("④ 服务推荐准确率 92%"), unsafe_allow_html=True)
st.markdown(
    '<div class="sg-card"><div class="sg-p">'
    '<b>1.</b> 服务推荐运行在<b>封闭意图域</b>内：就医建议 / 联系家属 / 社区服务 / 防跌倒干预等'
    '有限意图集合，远低于开放域问答难度。<br>'
    '<b>2.</b> 技术栈：适老化知识图谱约束 + RAG 检索增强生成 + ChatGLM 领域微调，'
    '图谱约束可显著压缩幻觉空间。<br>'
    '<b>3.</b> 封闭域智能问答 / 推荐系统的意图命中率在同类落地系统中普遍报告 85%–95%，'
    '取 92% 作为区间中值。<br>'
    '<b>结论：</b>92% 为封闭域系统常规区间中值，有工程先例支撑；上线后以人工抽检逐步校准。'
    '</div></div>',
    unsafe_allow_html=True)

# ---------------- 方法与边界 ----------------
st.markdown(style.section("预估方法与边界"), unsafe_allow_html=True)
st.markdown(
    '<div class="sg-card"><div class="sg-h">预估方法</div>'
    '<div class="sg-p">厂商官方基准（可复现）→ 社区经验区间（加速倍数）→ 文献报告区间'
    '（同类任务表现）→ 取「下沿或中值」作为目标，保证目标不激进。</div></div>'
    '<div class="sg-card"><div class="sg-h">边界说明（随材料一并出示）</div>'
    '<div class="sg-p">1) 本页数值为预估值，最终以自采数据集 + Jetson Nano 实测为准；'
    '2) 预估证明「目标设定合理」，不能替代实测背书；'
    '3) 边缘延迟暂无本系统实测，当前仅完成 PC 代理验证（算法 Demo 可复现）。</div></div>',
    unsafe_allow_html=True)
st.markdown(style.footer(), unsafe_allow_html=True)
