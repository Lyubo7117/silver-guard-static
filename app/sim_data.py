# -*- coding: utf-8 -*-
"""银发守护 · 概念演示原型 —— 模拟数据模块

说明：当前阶段无真实硬件与自采数据集，本模块全部生成"演示用模拟数据"，
仅用于展示系统形态与"感知-理解-服务"闭环，所有数值均不代表真实运行结果。
"""
import random
from datetime import datetime, timedelta
import pandas as pd

LOCATIONS = [
    ("院士楼·东花园", "家属区"),
    ("西家属区·中心广场", "家属区"),
    ("老干部活动中心", "活动中心"),
    ("离退休工作处·怡乐厅", "活动中心"),
    ("校医院·南湖步道", "校园步道"),
    ("东家属区·荷塘畔", "家属区"),
]

BEHAVIORS = ["正常行走", "驻足休息", "久坐乘凉", "结伴交谈", "独自徘徊", "挥手呼救", "跌倒"]

EVENT_TYPES = ["跌倒", "长时间静止", "独自徘徊", "异常聚集", "挥手呼救"]


def _rng(seed):
    return random.Random(seed if seed is not None else datetime.now().microsecond)


def gen_nodes(seed=None):
    rng = _rng(seed)
    nodes = []
    for i, (loc, typ) in enumerate(LOCATIONS):
        status = rng.choices(["在线", "注意", "告警"], weights=[68, 24, 8])[0]
        people = rng.randint(20, 35) if status == "告警" else rng.randint(0, 18)
        behavior = rng.choice(["挥手呼救", "跌倒"]) if status == "告警" else rng.choice(BEHAVIORS[:5])
        nodes.append({
            "id": "NODE-%02d" % (i + 1),
            "name": loc,
            "type": typ,
            "status": status,
            "people": people,
            "behavior": behavior,
            "latency_ms": int(rng.uniform(85, 195)),
            "masked": True,
            "sos": behavior == "挥手呼救",
        })
    return nodes


def gen_events(n=14, seed=None):
    rng = _rng(seed)
    now = datetime.now()
    events = []
    for i in range(n):
        et = rng.choices(EVENT_TYPES, weights=[30, 20, 24, 11, 15])[0]
        loc = LOCATIONS[rng.randrange(len(LOCATIONS))][0]
        ts = now - timedelta(minutes=rng.randint(1, 720))
        events.append({
            "event_id": "EVT-2026%04d" % (i + 1),
            "type": et,
            "node": loc,
            "time": ts.strftime("%H:%M"),
            "date": ts.strftime("%Y-%m-%d"),
            "confidence": round(rng.uniform(0.74, 0.98), 2),
            "status": rng.choices(["新告警", "处理中", "已完结"], weights=[28, 24, 48])[0],
            "masked": True,
        })
    events.sort(key=lambda e: (e["date"], e["time"]), reverse=True)
    return events


SUGGESTIONS = {
    "跌倒": [
        ("立即响应", "边缘端 <200ms 本地告警，同步推送紧急联系人"),
        ("医疗路径", "就近：校医院急诊科（约300m / 步行4分钟）"),
        ("家属联动", "家属端已弹出 SOS 提醒与实时定位"),
        ("现场处置", "提示疏散围观、保持跌倒者体位稳定、等待救护"),
    ],
    "挥手呼救": [
        ("立即响应", "识别到主动呼救，边缘端本地确认后上报"),
        ("人员定位", "已锁定节点位置并通知最近巡逻人员"),
        ("家属联动", "向家属端推送呼救事件与现场快照（已脱敏）"),
    ],
    "长时间静止": [
        ("状态核验", "静止超阈值，边缘端二次确认后上报云端"),
        ("服务建议", "推送就近休息点与饮水点信息"),
    ],
    "独自徘徊": [
        ("行为关注", "疑似走失风险，纳入观察名单"),
        ("服务建议", "生成回家/常用路线导航并通知家属关注"),
    ],
    "异常聚集": [
        ("态势研判", "人群密度超限，联动管理者端疏导"),
        ("服务建议", "规划分流路线，提示避拥挤区域"),
    ],
}


def suggestion_for(event_type):
    return SUGGESTIONS.get(event_type, SUGGESTIONS["长时间静止"])


def gen_trend(days=30, seed=7):
    rng = random.Random(seed)
    today = datetime.now().date()
    rows = []
    for d in range(days):
        date = today - timedelta(days=days - 1 - d)
        rows.append({
            "date": date.strftime("%m-%d"),
            "跌倒": rng.randint(0, 4),
            "其他异常": rng.randint(2, 12),
        })
    return pd.DataFrame(rows)


def gen_type_dist(seed=11):
    rng = random.Random(seed)
    return pd.DataFrame({
        "类型": EVENT_TYPES,
        "次数": [rng.randint(6, 30) for _ in EVENT_TYPES],
    })


def gen_node_bar(seed=13):
    rng = random.Random(seed)
    return pd.DataFrame({
        "节点": [n for n, _ in LOCATIONS],
        "事件数": [rng.randint(3, 26) for _ in LOCATIONS],
    })
