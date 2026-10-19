#!/usr/bin/env python3
"""Build a fully self-hosted static (stlite) version of the silver_guard_demo Streamlit app.

Everything the browser needs is hosted locally (Gitee Pages):
  - @stlite/mountable 0.75.0 bundle (streamlit 1.40.1 runtime in WASM)
  - pyodide v0.26.2 full distribution + the pyodide-lock package closure we need
  - a pre-seeded site-packages archive for the pure-Python wheels that are NOT
    in the pyodide lock (blinker, tenacity, toml, watchdog, pydeck, tornado,
    plotly, markdown-it-py, mdurl) so micropip never touches pypi.org
  - the streamlit wheel with the `fastparquet` requirement stripped (no wasm wheel)

Run:  python build_static.py
"""
import json
import os
import re
import shutil
import urllib.request
import zipfile
import concurrent.futures

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(ROOT, "..", "silver_guard_demo"))
VENDOR = os.path.join(ROOT, "vendor")
PYODIDE_DIR = os.path.join(VENDOR, "pyodide")
PYPYI_DIR = os.path.join(VENDOR, "pypi")
WHEELHOUSE = os.path.join(ROOT, "wheelhouse")
APP_DIR = os.path.join(ROOT, "app")

PYODIDE_VERSION = "0.26.2"
JSDELIVR_PYODIDE = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full"
SITE_PACKAGES = "/lib/python3.12/site-packages"

# Packages resolved from the (self-hosted) pyodide lock file -> loadPackage.
# "micropip" is required by the stlite worker itself.
PREBUILT_NAMES = [
    "micropip", "numpy", "pandas", "altair", "pillow", "requests", "rich", "click",
    "cachetools", "protobuf", "packaging", "typing-extensions", "jinja2",
    "pygments", "markupsafe", "six",
]

# Pure-Python wheels pre-seeded into site-packages (NOT available in the pyodide lock).
# watchdog/tornado are intentionally absent: stlite's streamlit build strips those
# imports via codemods, and neither has a py3-none-any wheel anyway.
PYPI_WHEELS = [
    ("blinker", "1.9.0"),
    ("tenacity", "9.2.1"),        # streamlit pins <10
    ("toml", "0.10.2"),
    ("pydeck", "0.9.3"),
    ("plotly", "7.1.0"),
    ("narwhals", "2.27.1"),       # plotly >= 7 dependency
    ("markdown-it-py", "4.2.0"),
    ("mdurl", "0.1.2"),
]

APP_FILES = ["Home.py", "style.py", "sim_data.py"]
PAGE_FILES = [
    "pages/1_实时监测看板.py",
    "pages/2_事件与处置.py",
    "pages/3_小程序三端.py",
    "pages/4_管理者看板.py",
    "pages/5_技术验证路线.py",
    "pages/6_指标预估依据.py",
]


def log(msg):
    print(f"[build] {msg}", flush=True)


def fetch(url, dest=None, retries=4):
    for attempt in range(retries):
        try:
            if dest:
                urllib.request.urlretrieve(url, dest)
                return dest
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:
            if attempt == retries - 1:
                raise
            log(f"retry {attempt + 1} for {url} ({e})")
    return None


# ---------------------------------------------------------------- 1. app files
def transform(text: str) -> str:
    """Downgrade streamlit >=1.49 APIs to the 1.40.1 runtime bundled with stlite."""
    text = text.replace('width="stretch"', "use_container_width=True")
    text = re.sub(r"\bst\.iframe\(", "st.components.v1.html(", text)
    # st.dataframe goes through the Parquet (fastparquet) path in stlite's streamlit
    # build, which cannot be installed in Pyodide -> render design-system HTML tables.
    text = re.sub(r"\bst\.dataframe\(", "style.sg_table(", text)
    return text


# Design-system table CSS + sg_table() helper appended to the static build's style.py.
TABLE_CSS = """
<style>
.sg-table-wrap{overflow-x:auto;margin:0 0 14px}
.sg-table{width:100%;border-collapse:collapse;background:#FFFFFF;border:1px solid var(--sg-line);
  border-radius:12px;font-size:12.5px;box-shadow:var(--sg-shadow)}
.sg-table th{background:linear-gradient(180deg,#F4F8F6,#EDF5F1);color:var(--sg-primary-deep);
  font-weight:700;text-align:left;padding:9px 12px;border-bottom:1px solid var(--sg-line);white-space:nowrap}
.sg-table td{padding:8px 12px;border-bottom:1px solid #F0EEE7;color:#4A4944;vertical-align:middle}
.sg-table tr:last-child td{border-bottom:none}
.sg-table tbody tr:hover{background:#FAFBFA}
.sg-prog{position:relative;background:#EDEBE4;border-radius:999px;height:16px;min-width:90px;overflow:hidden}
.sg-prog-bar{position:absolute;left:0;top:0;bottom:0;
  background:linear-gradient(90deg,var(--sg-primary-mid),var(--sg-primary));border-radius:999px}
.sg-prog-t{position:relative;display:block;text-align:center;font-size:10.5px;font-weight:700;
  color:var(--sg-primary-deep);line-height:16px}
</style>
"""

SG_TABLE_HELPER = '''

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
'''


def build_app():
    if os.path.isdir(APP_DIR):
        shutil.rmtree(APP_DIR)
    os.makedirs(os.path.join(APP_DIR, "pages"), exist_ok=True)
    files = {}
    for rel in APP_FILES + PAGE_FILES:
        src_path = os.path.join(SRC, rel.replace("/", os.sep))
        with open(src_path, encoding="utf-8") as f:
            files[rel] = transform(f.read())
    # style.py gets the table CSS + sg_table helper for the static build
    files["style.py"] = (
        files["style.py"]
        + "\n\nBASE_CSS = BASE_CSS + "
        + repr(TABLE_CSS)
        + SG_TABLE_HELPER
    )
    for rel, content in files.items():
        dest = os.path.join(APP_DIR, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    log(f"app files written: {len(files)} (API downgraded for streamlit 1.40.1)")
    return files


# ---------------------------------------------------- 2. patched streamlit wheel
def patch_streamlit_wheel():
    """Strip the `fastparquet` Requires-Dist (no wasm/pure wheel exists)."""
    whl = os.path.join(PYPYI_DIR, "streamlit-1.40.1-cp312-none-any.whl")
    if not os.path.exists(whl):
        raise FileNotFoundError(whl)
    with zipfile.ZipFile(whl) as z:
        items = {n: z.read(n) for n in z.namelist()}
    meta_name = "streamlit-1.40.1.dist-info/METADATA"
    meta = items[meta_name].decode()
    new_meta = "\n".join(
        l for l in meta.splitlines() if not l.startswith("Requires-Dist: fastparquet")
    ) + "\n"
    if new_meta == meta:
        log("streamlit wheel already patched")
    else:
        items[meta_name] = new_meta.encode()
        tmp = whl + ".tmp"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            for n, data in items.items():
                z.writestr(n, data)
        os.replace(tmp, whl)
        log("streamlit wheel patched (fastparquet requirement removed)")


# ------------------------------------------- 3. pyodide lock closure + wheels
def lock_closure():
    with open(os.path.join(PYODIDE_DIR, "pyodide-lock.json"), encoding="utf-8") as f:
        pkgs = json.load(f)["packages"]
    closure, stack = set(), list(PREBUILT_NAMES)
    while stack:
        name = stack.pop()
        if name in closure or name not in pkgs:
            continue
        closure.add(name)
        stack.extend(pkgs[name].get("depends", []))
    return pkgs, closure


def download_lock_wheels():
    pkgs, closure = lock_closure()
    missing = []
    for name in sorted(closure):
        fn = pkgs[name]["file_name"]
        dest = os.path.join(PYODIDE_DIR, fn)
        if not os.path.exists(dest):
            missing.append((f"{JSDELIVR_PYODIDE}/{fn}", dest))
    log(f"pyodide lock closure: {len(closure)} packages, {len(missing)} wheels to download")

    def dl(item):
        url, dest = item
        try:
            fetch(url, dest)
            return None
        except Exception as e:
            return f"{url} ({e})"

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        fails = [r for r in ex.map(dl, missing) if r]
    if fails:
        raise RuntimeError("failed downloads:\n" + "\n".join(fails))
    total = sum(
        os.path.getsize(os.path.join(PYODIDE_DIR, pkgs[n]["file_name"])) for n in closure
    )
    log(f"pyodide wheels ready ({total / 1048576:.1f} MB for {len(closure)} packages)")


# ------------------------------------------------ 4. pre-seeded PyPI wheelhouse
def download_pypi_wheels():
    if os.path.isdir(WHEELHOUSE):
        shutil.rmtree(WHEELHOUSE)
    sp = os.path.join(WHEELHOUSE, "site-packages")
    os.makedirs(sp)

    def resolve(name, version):
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=60) as r:
            d = json.load(r)
        files = d["urls"]
        pure = [f for f in files if f["filename"].endswith("py3-none-any.whl")]
        if not pure:
            raise RuntimeError(f"{name}=={version} has no py3-none-any wheel")
        return pure[0]["url"], pure[0]["filename"]

    for name, version in PYPI_WHEELS:
        url, fn = resolve(name, version)
        dest = os.path.join(ROOT, "wheels_src", fn)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        fetch(url, dest)
        with zipfile.ZipFile(dest) as z:
            z.extractall(sp)
        log(f"pre-seeded {name}=={version}")
    if os.path.isdir(os.path.join(ROOT, "wheels_src")):
        shutil.rmtree(os.path.join(ROOT, "wheels_src"))

    # zip the site-packages tree for the stlite `archives` option
    zip_path = os.path.join(VENDOR, "wheelhouse.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _dirs, files in os.walk(sp):
            for fn in files:
                full = os.path.join(base, fn)
                rel = os.path.relpath(full, sp)
                z.write(full, rel)
    log(f"wheelhouse.zip written ({os.path.getsize(zip_path) / 1048576:.1f} MB)")


# ------------------------------------------------------------- 5. index.html
INDEX_TMPL = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>银发守护 · 高校公共空间适老化智能感知系统（概念演示）</title>
<link rel="stylesheet" href="vendor/stlite.min.css" />
<style>
  :root { --red:#A32D2D; --ink:#1F2733; --sub:#5B6472; --line:#E5E0DA; --bg:#F7F5F1; }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; height:100%; background:var(--bg); color:var(--ink);
    font-family:"PingFang SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif; }
  #topbar { display:flex; align-items:center; gap:12px; padding:10px 18px; background:#fff;
    border-bottom:1px solid var(--line); position:sticky; top:0; z-index:10; }
  #topbar .logo { font-weight:700; color:var(--red); font-size:17px; white-space:nowrap; }
  #topbar .sub { color:var(--sub); font-size:12.5px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #topbar .spacer { flex:1; }
  #topbar a.fallback { font-size:12.5px; color:var(--sub); text-decoration:none; border:1px solid var(--line);
    border-radius:999px; padding:4px 12px; white-space:nowrap; }
  #topbar a.fallback:hover { color:var(--red); border-color:var(--red); }
  #root { min-height: calc(100vh - 49px); }
  #boot { display:flex; flex-direction:column; align-items:center; justify-content:center;
    min-height:70vh; gap:14px; color:var(--sub); }
  #boot .ring { width:44px; height:44px; border-radius:50%; border:4px solid var(--line);
    border-top-color:var(--red); animation:spin 1s linear infinite; }
  #boot .t1 { font-size:15px; color:var(--ink); font-weight:600; }
  #boot .t2 { font-size:12.5px; }
  @keyframes spin { to { transform:rotate(360deg); } }
  #foot { padding:10px 18px 18px; color:#8A93A0; font-size:12px; text-align:center; }
  @media (max-width:640px){ #topbar .sub { display:none; } }
</style>
</head>
<body>
<div id="topbar">
  <div class="logo">银发守护 SilverGuard</div>
  <div class="sub">高校公共空间适老化智能感知与服务系统 · 概念演示（数据为模拟数据）</div>
  <div class="spacer"></div>
  <a class="fallback" href="__CLOUD_URL__" target="_blank" rel="noopener">Streamlit Cloud 备用入口</a>
</div>
<div id="boot">
  <div class="ring"></div>
  <div class="t1">正在加载演示运行时…</div>
  <div class="t2">首次加载约 20–60 秒（浏览器内运行完整 Streamlit，无需服务器）</div>
</div>
<div id="root"></div>
<div id="foot">纯前端演示 · 多模态大模型跌倒检测与适老化服务概念验证 · 智慧城市大赛创意设计</div>
<script src="vendor/stlite.min.js"></script>
<script>
(function () {
  var APP_FILES = __APP_FILES__;
  var files = {};
  Object.keys(APP_FILES).forEach(function (k) { files[k] = { data: APP_FILES[k] }; });
  function abs(p) { return new URL(p, document.baseURI).href; }
  stlite.mount(
    {
      entrypoint: "Home.py",
      files: files,
      requirements: __REQUIREMENTS__,
      prebuiltPackageNames: [],
      archives: [{ url: abs("vendor/wheelhouse.zip"), format: "zip",
                   options: { extract_dir: "__SITE_PACKAGES__" } }],
      pyodideUrl: abs("vendor/pyodide/pyodide.js"),
      streamlitConfig: { "browser.gatherUsageStats": false },
      disableProgressToasts: false,
    },
    document.getElementById("root")
  );
  var boot = document.getElementById("boot");
  var obs = new MutationObserver(function () {
    if (document.getElementById("root").children.length > 0) {
      boot.style.display = "none";
      obs.disconnect();
    }
  });
  obs.observe(document.getElementById("root"), { childList: true, subtree: true });
  setTimeout(function () { boot.style.display = "none"; }, 120000);
})();
</script>
</body>
</html>
"""

CLOUD_URL = "https://silver-guard-demo-hwxj57kzpmb2eda4hs2zw.streamlit.app"


def build_index(files):
    html = INDEX_TMPL
    html = html.replace("__APP_FILES__", json.dumps(files, ensure_ascii=False))
    html = html.replace("__REQUIREMENTS__", json.dumps(PREBUILT_NAMES))
    html = html.replace("__SITE_PACKAGES__", SITE_PACKAGES)
    html = html.replace("__CLOUD_URL__", CLOUD_URL)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    log("index.html written")


def main():
    files = build_app()
    patch_streamlit_wheel()
    download_lock_wheels()
    download_pypi_wheels()
    build_index(files)
    total = 0
    for base, _d, fs in os.walk(ROOT):
        if "wheelhouse" in base or "__pycache__" in base:
            continue
        for fn in fs:
            total += os.path.getsize(os.path.join(base, fn))
    log(f"DONE. static site total size: {total / 1048576:.1f} MB -> {ROOT}")


if __name__ == "__main__":
    main()
