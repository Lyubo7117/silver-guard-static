# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import style

st.markdown(style.css(), unsafe_allow_html=True)
st.markdown(style.page_header(
    "技术验证路线",
    "关键技术「设计目标 vs 当前状态」对照 · 无硬件替代方案 · 公开数据集 · 12 个月路线",
    "05 · 验证计划"), unsafe_allow_html=True)

st.markdown(style.note(
    '当前无 Jetson 等边缘硬件、亦无自采数据集。下表如实区分<b>设计目标值</b>与<b>当前状态</b>，'
    '验证均以「公开数据集 + PC 端」先行，实测值到位后回填。'), unsafe_allow_html=True)

st.markdown(style.section("关键技术对照表", "设计目标 vs 当前状态"), unsafe_allow_html=True)
spec = pd.DataFrame([
    ["多模态行为检测", "mAP ≥ 90%", "模型选型完成，待训练", "UR-Fall/Le2i + YOLOv8-pose", "待实测"],
    ["边缘推理延迟", "< 200 ms", "无 Jetson，改用 PC 代理验证", "TensorRT INT8 vs FP32 对比", "待实测"],
    ["CLIP 多模态融合", "复杂场景鲁棒", "零样本可行性待验证", "CLIP 图文匹配 zero-shot", "待实测"],
    ["12 类异常识别", "12 类", "依赖自采数据集", "公开子集 + 规则扩展", "待实测"],
    ["LLM 服务建议", "个性化生成", "待领域微调", "ChatGLM-6B + 小知识库 Demo", "待实测"],
    ["隐私脱敏", "本地处理", "方案设计完成", "OpenCV 人脸模糊 Demo", "待实测"],
], columns=["关键技术", "设计目标", "当前状态", "验证方式", "实测值"])
style.sg_table(spec, use_container_width=True, hide_index=True)

st.markdown(style.section("无硬件替代方案", "PC 端代理验证路径"), unsafe_allow_html=True)
st.markdown(
    '<div class="sg-card"><div class="sg-h">算法与延迟的 PC 端代理验证</div>'
    '<div class="sg-p">1) 检测/融合：PC(CPU/GPU) + PyTorch/ONNX 跑通算法逻辑；'
    '2) 延迟：PC + TensorRT 做 INT8/FP32 对比，给出量化收益曲线（注明为 PC 端代理，非 Jetson 实测）；'
    '3) 单节点模拟：笔记本 + USB 摄像头模拟「感知—边缘」一体节点，现场演示闭环。</div></div>'
    '<div class="sg-card"><div class="sg-h">后续补实测的路径</div>'
    '<div class="sg-p">申请学院 GPU / 租用云 GPU；或采购 Jetson Orin Nano（约 ¥1500）补齐边缘端真实延迟数据，'
    '替换当前 PC 代理值。</div></div>',
    unsafe_allow_html=True)

st.markdown(style.section("公开跌倒数据集", "现阶段验证用"), unsafe_allow_html=True)
ds = pd.DataFrame([
    ["UR-Fall", "视频 + 加速度计", "30 序列 / 2 相机", "跌倒识别基准测试"],
    ["Le2i", "多视角视频", "约 190 段", "多视角鲁棒性"],
    ["FDD", "视频帧序列", "约 5000+ 帧", "姿态/检测训练"],
    ["CAUCAFall", "带标注视频", "约 70 段", "静止/阈值核验"],
    ["Multiple Cameras Fall", "多相机视频", "约 24 序列", "遮挡场景"],
], columns=["数据集", "模态", "规模", "用途"])
style.sg_table(ds, use_container_width=True, hide_index=True)

st.markdown(style.section("12 个月技术路线"), unsafe_allow_html=True)
road = pd.DataFrame([
    ["阶段一", "第1-2月", "需求分析 + 多模态数据集构建", "进行中"],
    ["阶段二", "第3-5月", "核心算法研发（检测/融合/边缘优化/LLM）", "未开始"],
    ["阶段三", "第6-7月", "系统集成与测试（端-边-云）", "未开始"],
    ["阶段四", "第8-10月", "试点部署与优化（2个高校校区）", "未开始"],
    ["阶段五", "第11-12月", "成果总结与推广（论文/专利/演示）", "未开始"],
], columns=["阶段", "时间", "关键产出", "进度"])
style.sg_table(road, use_container_width=True, hide_index=True)

st.markdown(style.section("下一步行动清单", "勾选可跟踪完成度"), unsafe_allow_html=True)
todo = [
    "下载 UR-Fall / Le2i 数据集",
    "跑通 YOLOv8-pose 跌倒 Demo（PC）",
    "CLIP 零样本行为识别验证",
    "TensorRT / ONNX 延迟对比（PC）",
    "小程序三端高保真原型细化",
]
if "todo" not in st.session_state:
    st.session_state.todo = {t: False for t in todo}
for t in todo:
    st.session_state.todo[t] = st.checkbox(t, value=st.session_state.todo[t], key="cb_" + t)
done = sum(1 for v in st.session_state.todo.values() if v)
st.progress(done / len(todo), text=f"完成度 {done}/{len(todo)}")
st.markdown(style.footer(), unsafe_allow_html=True)
