# -*- coding: utf-8 -*-
"""银发守护 · 概念演示原型 —— 设计系统（共享样式与小组件）

设计基调：暖中性色 + 墨绿主色；浅色、克制、有呼吸感。
- BASE_CSS 为纯字符串（含 CSS 百分比，严禁对其使用 % 格式化）；
- helper 一律使用 f-string 返回 HTML，配合 st.markdown(..., unsafe_allow_html=True)；
- helper 的 HTML 中不得出现花括号（避免 f-string 转义问题）。
"""

BASE_CSS = """
<style>
:root{
  --sg-ink:#2C2C2A; --sg-muted:#6B6A64; --sg-faint:#9A988F; --sg-line:#E5E2DA; --sg-bg:#F7F6F2;
  --sg-primary:#0F6E56; --sg-primary-deep:#085041; --sg-primary-soft:#E1F5EE; --sg-primary-mid:#9FE1CB;
  --sg-warn:#854F0B; --sg-warn-bg:#FAEEDA; --sg-err:#A32D2D; --sg-err-bg:#FCEBEB;
  --sg-info:#0C447C; --sg-info-bg:#E6F1FB;
  --sg-shadow:0 1px 2px rgba(28,25,23,.05),0 2px 6px rgba(28,25,23,.06);
  --sg-shadow-lg:0 2px 6px rgba(28,25,23,.07),0 10px 28px rgba(28,25,23,.09);
}
/* ---------- Hero 首屏 ---------- */
.sg-hero{position:relative;border:1px solid var(--sg-line);border-radius:16px;padding:26px 30px 20px;
  background:linear-gradient(135deg,#FFFFFF 0%,#F4F8F6 55%,#E9F4EE 100%);
  box-shadow:var(--sg-shadow);margin-bottom:14px;overflow:hidden}
.sg-hero::after{content:"";position:absolute;right:-70px;top:-70px;width:230px;height:230px;border-radius:50%;
  background:radial-gradient(circle,rgba(15,110,86,.12),rgba(15,110,86,0) 70%)}
.sg-hero .eyebrow{font-size:11.5px;letter-spacing:.14em;color:var(--sg-primary);font-weight:600}
.sg-hero .t{font-size:28px;font-weight:700;color:var(--sg-ink);margin-top:8px;letter-spacing:.02em}
.sg-hero .s{font-size:14px;color:#5F5E5A;margin-top:8px;line-height:1.7;max-width:720px}
.sg-hero .tags{margin-top:16px;display:flex;flex-wrap:wrap;gap:6px}
.sg-hero .meta{margin-top:16px;padding-top:13px;border-top:1px dashed #D9D6CD;
  font-size:12px;color:var(--sg-muted);display:flex;flex-wrap:wrap;gap:20px}
/* ---------- 页头 ---------- */
.sg-pagehead{padding:2px 0 12px;border-bottom:1px solid var(--sg-line);margin-bottom:16px}
.sg-pagehead .eyebrow{font-size:11px;letter-spacing:.18em;color:var(--sg-primary);font-weight:700}
.sg-pagehead .t{font-size:21px;font-weight:700;color:var(--sg-ink);margin-top:5px}
.sg-pagehead .s{font-size:12.5px;color:var(--sg-muted);margin-top:3px}
/* ---------- 分区标题 ---------- */
.sg-section{display:flex;align-items:center;gap:9px;margin:22px 0 11px;flex-wrap:wrap}
.sg-section .bar{width:4px;height:15px;border-radius:2px;background:var(--sg-primary);flex:none}
.sg-section .t{font-size:15.5px;font-weight:700;color:var(--sg-ink)}
.sg-section .s{font-size:12px;color:var(--sg-faint)}
/* ---------- KPI / 卡片 ---------- */
.sg-kpi{border:1px solid var(--sg-line);border-radius:12px;padding:13px 15px;background:#FFFFFF;
  margin-bottom:10px;box-shadow:var(--sg-shadow);transition:transform .15s ease,box-shadow .15s ease}
.sg-kpi:hover{transform:translateY(-1px);box-shadow:var(--sg-shadow-lg)}
.sg-kpi .v{font-size:23px;font-weight:700;color:var(--sg-primary);line-height:1.15}
.sg-kpi .l{font-size:12px;color:var(--sg-muted);margin-top:3px}
.sg-kpi .sub{font-size:11px;color:var(--sg-faint);margin-top:2px}
.sg-card{border:1px solid var(--sg-line);border-radius:12px;padding:14px 16px;background:#FFFFFF;
  margin-bottom:12px;box-shadow:var(--sg-shadow)}
.sg-h{font-size:14.5px;font-weight:700;color:var(--sg-ink);margin:0 0 3px}
.sg-p{font-size:12.5px;color:#5F5E5A;margin:0 0 4px;line-height:1.75}
.sg-mini{font-size:12px;color:var(--sg-muted)}
.sg-note{font-size:12.5px;color:var(--sg-warn);background:linear-gradient(180deg,#FDF6E9,#FAEEDA);
  border:1px solid #F0DCB8;border-radius:10px;padding:10px 14px;margin:10px 0;line-height:1.75}
/* ---------- 徽标 ---------- */
.badge{display:inline-flex;align-items:center;padding:2px 10px;border-radius:999px;font-size:11.5px;
  font-weight:600;margin-right:6px;letter-spacing:.02em}
.b-ok{background:var(--sg-primary-soft);color:var(--sg-primary-deep)}
.b-warn{background:var(--sg-warn-bg);color:var(--sg-warn)}
.b-err{background:var(--sg-err-bg);color:var(--sg-err)}
.b-info{background:var(--sg-info-bg);color:var(--sg-info)}
.b-gray{background:#F1EFE8;color:#5F5E5A}
.b-primary{background:var(--sg-primary);color:#FFFFFF}
/* ---------- 流程步骤 ---------- */
.sg-flow{display:flex;gap:14px;align-items:stretch;flex-wrap:wrap}
.sg-flow .step{position:relative;flex:1 1 180px;border:1px solid var(--sg-line);border-radius:12px;
  padding:14px 16px;background:#FFFFFF;box-shadow:var(--sg-shadow)}
.sg-flow .step:not(:last-child)::after{content:"→";position:absolute;right:-13px;top:50%;
  transform:translateY(-50%);color:#B9B6AC;font-size:14px;font-weight:700}
.sg-flow .step .n{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;
  border-radius:50%;background:var(--sg-primary-soft);color:var(--sg-primary-deep);
  font-size:12px;font-weight:700;margin-bottom:7px}
.sg-flow .step .t{font-size:13.5px;font-weight:700;color:var(--sg-primary)}
.sg-flow .step .d{font-size:12px;color:#5F5E5A;margin-top:5px;line-height:1.75}
@media (max-width:760px){.sg-flow .step:not(:last-child)::after{display:none}}
/* ---------- 收入条形 ---------- */
.sg-barrow{margin-top:12px}
.sg-barrow .item{margin-bottom:10px}
.sg-barrow .lab{display:flex;justify-content:space-between;font-size:12px;color:var(--sg-ink);margin-bottom:4px}
.sg-barrow .lab b{color:var(--sg-primary);font-weight:600}
.sg-bar{height:6px;background:#F1EFE8;border-radius:3px;overflow:hidden}
.sg-bar i{display:block;height:100%;background:linear-gradient(90deg,#1D9E75,#0F6E56);border-radius:3px}
/* ---------- 页面导航卡片 ---------- */
.sg-navgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media (max-width:900px){.sg-navgrid{grid-template-columns:repeat(2,1fr)}}
.sg-navcard{border:1px solid var(--sg-line);border-radius:12px;padding:14px 16px;background:#FFFFFF;
  box-shadow:var(--sg-shadow);transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease}
.sg-navcard:hover{transform:translateY(-2px);box-shadow:var(--sg-shadow-lg);border-color:var(--sg-primary-mid)}
.sg-navcard .ico{font-size:18px}
.sg-navcard .t{font-size:13.5px;font-weight:700;color:var(--sg-ink);margin-top:7px}
.sg-navcard .d{font-size:12px;color:var(--sg-muted);margin-top:4px;line-height:1.65}
/* ---------- 行 / 大按钮 ---------- */
.rowline{display:flex;justify-content:space-between;font-size:12.5px;color:var(--sg-ink);
  padding:7px 0;border-bottom:1px solid #F0EEE7}
.rowline:last-child{border-bottom:none}
.bigbtn{display:block;text-align:center;background:var(--sg-primary);color:#fff;border-radius:14px;
  padding:15px;font-size:16px;font-weight:600;margin:10px 0;box-shadow:var(--sg-shadow)}
.bigbtn.red{background:var(--sg-err)}
/* ---------- 手机原型 ---------- */
.phone{width:284px;border:1px solid #D9D6CD;border-radius:30px;background:#F4F2EC;
  padding:10px 12px 12px;margin:0 auto;box-shadow:var(--sg-shadow-lg)}
.phone .status{display:flex;justify-content:space-between;align-items:center;font-size:10.5px;
  color:var(--sg-muted);padding:2px 8px 8px;font-weight:600}
.phone .status .sig{letter-spacing:1px}
.phone .screen{background:#FFFFFF;border:1px solid #ECE9E1;border-radius:22px;padding:14px;min-height:470px}
.phone .homei{width:96px;height:4px;border-radius:2px;background:#D9D6CD;margin:10px auto 0}
/* ---------- 主监测视图（深色 HUD） ---------- */
.sg-mon{position:relative;height:340px;border-radius:14px;overflow:hidden;border:1px solid #3A3A34;
  background:radial-gradient(120% 120% at 50% 0%,#33322E 0%,#232220 70%)}
.sg-mon .hud{position:absolute;left:0;right:0;display:flex;justify-content:space-between;align-items:center;
  gap:10px;padding:9px 14px;color:#E8E6DF;font-size:11.5px;background:rgba(0,0,0,.38);z-index:2}
.sg-mon .hud-top{top:0}
.sg-mon .hud-bottom{bottom:0}
.sg-mon .rec{display:inline-flex;align-items:center;gap:5px;color:#FF9B9B;font-weight:700;letter-spacing:.1em}
.sg-mon .rec::before{content:"";width:7px;height:7px;border-radius:50%;background:#E5484D;
  animation:sg-blink 1.2s ease-in-out infinite}
@keyframes sg-blink{0%,100%{opacity:1}50%{opacity:.2}}
.sg-mon .scan{position:absolute;left:0;right:0;height:90px;pointer-events:none;z-index:1;
  background:linear-gradient(180deg,rgba(29,158,117,0),rgba(29,158,117,.16),rgba(29,158,117,0));
  animation:sg-scan 3.4s linear infinite}
@keyframes sg-scan{from{top:-90px}to{top:100%}}
.sg-mon .box{position:absolute;border:1.5px solid var(--c);border-radius:4px;z-index:1}
.sg-mon .box .tag{position:absolute;top:-15px;left:-1.5px;background:var(--c);color:#fff;
  font-size:10px;font-weight:600;padding:1px 6px;border-radius:3px;white-space:nowrap}
.sg-mon .legend{display:flex;gap:6px;flex-wrap:wrap}
.sg-mon .chip{display:inline-flex;align-items:center;gap:5px;font-size:10.5px;color:#D8D5CC;
  background:rgba(255,255,255,.09);padding:2px 8px;border-radius:999px}
.sg-mon .chip .dot{width:7px;height:7px;border-radius:50%}
/* ---------- 用户三层角色 ---------- */
.sg-roles{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media (max-width:900px){.sg-roles{grid-template-columns:1fr}}
.sg-roles .role{border:1px solid var(--sg-line);border-radius:12px;padding:14px 16px;background:#FFFFFF;
  box-shadow:var(--sg-shadow);transition:transform .15s ease,box-shadow .15s ease}
.sg-roles .role:hover{transform:translateY(-1px);box-shadow:var(--sg-shadow-lg)}
.sg-roles .role .tag{font-size:11px;font-weight:700;letter-spacing:.08em;color:var(--sg-primary)}
.sg-roles .role .who{font-size:14.5px;font-weight:700;color:var(--sg-ink);margin-top:5px}
.sg-roles .role .d{font-size:12px;color:#5F5E5A;margin-top:6px;line-height:1.7}
.sg-roles .role .pay{margin-top:9px;padding-top:8px;border-top:1px dashed #E5E2DA;
  font-size:11.5px;color:var(--sg-primary);font-weight:600}
/* ---------- 场景三列对比 ---------- */
.sg-cmp{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media (max-width:900px){.sg-cmp{grid-template-columns:1fr}}
.sg-cmp .col{border:1px solid var(--sg-line);border-radius:12px;background:#FFFFFF;
  overflow:hidden;box-shadow:var(--sg-shadow)}
.sg-cmp .col .hd{padding:9px 14px;font-size:13px;font-weight:700;border-bottom:1px solid var(--sg-line);
  background:#FAF9F5;color:var(--sg-muted);display:flex;justify-content:space-between;align-items:center}
.sg-cmp .col .hd .mk{font-size:11px;font-weight:600;color:var(--sg-faint)}
.sg-cmp .col.hl{border-color:var(--sg-primary);box-shadow:var(--sg-shadow-lg)}
.sg-cmp .col.hl .hd{background:var(--sg-primary-soft);color:var(--sg-primary-deep);border-bottom-color:var(--sg-primary-mid)}
.sg-cmp .col.hl .hd .mk{color:var(--sg-primary)}
.sg-cmp .row{display:flex;justify-content:space-between;gap:10px;padding:8px 14px;
  font-size:12px;border-bottom:1px solid #F0EEE7;line-height:1.55}
.sg-cmp .row:last-child{border-bottom:none}
.sg-cmp .row .k{color:var(--sg-faint);flex:none}
.sg-cmp .row .v{color:var(--sg-ink);text-align:right}
.sg-cmp .col.hl .row .v{color:var(--sg-primary-deep);font-weight:600}
/* ---------- 页脚 ---------- */
.sg-foot{margin-top:26px;padding-top:14px;border-top:1px solid var(--sg-line);
  text-align:center;font-size:11.5px;color:var(--sg-faint);letter-spacing:.02em}
</style>
"""


def css():
    return BASE_CSS


def page_header(title, sub="", tag=""):
    """统一页头：眉标 + 标题 + 副标题。"""
    eyebrow = f'<div class="eyebrow">{tag}</div>' if tag else ""
    return (f'<div class="sg-pagehead">{eyebrow}'
            f'<div class="t">{title}</div>'
            f'<div class="s">{sub}</div></div>')


def section(title, sub=""):
    """统一分区标题：墨绿竖线 + 标题 + 可选副标题。"""
    s = f'<span class="s">{sub}</span>' if sub else ""
    return (f'<div class="sg-section"><span class="bar"></span>'
            f'<span class="t">{title}</span>{s}</div>')


def kpi(value, label, sub=""):
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="sg-kpi"><div class="v">{value}</div><div class="l">{label}</div>{s}</div>'


def status_badge(s):
    m = {"在线": "b-ok", "注意": "b-warn", "告警": "b-err",
         "新告警": "b-err", "处理中": "b-warn", "已完结": "b-ok", "安全": "b-ok"}
    return f'<span class="badge {m.get(s, "b-gray")}">{s}</span>'


def note(text):
    return f'<div class="sg-note">{text}</div>'


def footer(text="银发守护 · 晚晴智守 ｜ 概念演示原型 · 页面数据均为模拟"):
    return f'<div class="sg-foot">{text}</div>'


BASE_CSS = BASE_CSS + '\n<style>\n.sg-table-wrap{overflow-x:auto;margin:0 0 14px}\n.sg-table{width:100%;border-collapse:collapse;background:#FFFFFF;border:1px solid var(--sg-line);\n  border-radius:12px;font-size:12.5px;box-shadow:var(--sg-shadow)}\n.sg-table th{background:linear-gradient(180deg,#F4F8F6,#EDF5F1);color:var(--sg-primary-deep);\n  font-weight:700;text-align:left;padding:9px 12px;border-bottom:1px solid var(--sg-line);white-space:nowrap}\n.sg-table td{padding:8px 12px;border-bottom:1px solid #F0EEE7;color:#4A4944;vertical-align:middle}\n.sg-table tr:last-child td{border-bottom:none}\n.sg-table tbody tr:hover{background:#FAFBFA}\n.sg-prog{position:relative;background:#EDEBE4;border-radius:999px;height:16px;min-width:90px;overflow:hidden}\n.sg-prog-bar{position:absolute;left:0;top:0;bottom:0;\n  background:linear-gradient(90deg,var(--sg-primary-mid),var(--sg-primary));border-radius:999px}\n.sg-prog-t{position:relative;display:block;text-align:center;font-size:10.5px;font-weight:700;\n  color:var(--sg-primary-deep);line-height:16px}\n</style>\n'

# ---------- static build: dataframe fallback (stlite parquet limitation) ----------
def sg_table(df, column_config=None, **kwargs):
    """Render a DataFrame as a design-system HTML table (static build only)."""
    import streamlit as st

    cols = list(df.columns)
    headers = []
    for c in cols:
        label = c
        if column_config and c in column_config:
            label = getattr(column_config[c], "label", None) or c
        headers.append(str(label))
    head = "".join("<th>%s</th>" % h for h in headers)
    body = ""
    for _, row in df.iterrows():
        tds = []
        for c in cols:
            v = row[c]
            pc = column_config.get(c) if column_config else None
            if pc is not None:
                try:
                    pct = max(0.0, min(1.0, float(v)))
                except Exception:
                    pct = 0.0
                fmt = getattr(pc, "format", None)
                text = (fmt % pct) if isinstance(fmt, str) else str(v)
                tds.append(
                    '<td><div class="sg-prog"><div class="sg-prog-bar" style="width:%d%%"></div>'
                    '<span class="sg-prog-t">%s</span></div></td>' % (round(pct * 100), text)
                )
            else:
                tds.append("<td>%s</td>" % v)
        body += "<tr>" + "".join(tds) + "</tr>"
    st.markdown(
        '<div class="sg-table-wrap"><table class="sg-table"><thead><tr>'
        + head + "</tr></thead><tbody>" + body + "</tbody></table></div>",
        unsafe_allow_html=True,
    )
