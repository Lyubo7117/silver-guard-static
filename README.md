# 银发守护 · 概念演示（纯前端静态版）

高校公共空间适老化智能感知与服务系统的**浏览器内运行版**：完整 Streamlit 应用通过
[stlite](https://github.com/whitphx/stlite)（Pyodide/WASM）在浏览器里直接运行，
**不依赖任何服务器、不请求任何海外 CDN**——所有运行时资产（Pyodide、Streamlit、
pandas/numpy/plotly 等 28 个 wheel）均已自托管在本仓库的 `vendor/` 目录中。

## 这个包怎么工作

```
index.html            入口页（顶部品牌栏 + 加载提示 + 挂载点）
vendor/
  stlite.min.js       stlite 运行时（Streamlit 1.40.1 + React 前端）
  static/             前端 chunk 资源
  pypi/               streamlit / stlite_lib wheel
  pyodide/            Pyodide v0.26.2 完整发行版 + 所需包 wheel
  wheelhouse.zip      预置 site-packages（blinker/tenacity/toml/pydeck/plotly/narwhals 等）
app/                  应用源码（已按 streamlit 1.40 做 API 降级，仅作存档）
```

- 首次打开需下载约 60–70MB 资产（Gitee 国内线路通常 10–40 秒），之后走浏览器缓存。
- 页面内的「Streamlit Cloud 备用入口」链接指向原云端版本，两条路互为备份。

## 部署到 Gitee Pages（免费 / 免备案 / 国内可直开）

1. **在 Gitee 建仓库**：右上角 ➕ → 新建仓库，名称建议 `silver-guard-static`，
   **务必设为公开仓库**（Gitee Pages 免费版要求公开），不要勾选任何初始化文件。
2. **推送代码**（在本目录执行）：

   ```bash
   git init
   git add -A
   git commit -m "银发守护概念演示 · 纯前端静态版"
   git branch -M master
   git remote add origin https://gitee.com/<你的用户名>/silver-guard-static.git
   git push -u origin master
   ```

   > 如果以前配过 git 代理，先检查并清除：
   > `git config --global --get-regexp url` 看到 `insteadOf` 规则就
   > `git config --global --unset url.<xxx>.insteadOf`。
3. **开启 Pages**：仓库页面 → 服务 → Gitee Pages → 选择分支 `master`、目录 `/`（根目录）→ 开启，等 1–2 分钟部署完成。
4. **访问地址**：`https://<你的用户名>.gitee.io/silver-guard-static/`

把演示链接交给评委/老师即可，国内网络直接打开，无需加速器。

## 本地预览

```bash
# 任选一个静态服务器，在 index.html 所在目录执行：
python -m http.server 8000
# 打开 http://localhost:8000
```

## 修改应用后重新构建

源码在 `../silver_guard_demo/`（主仓库，保持 streamlit 1.65 新版 API）。
改完后：

```bash
python build_static.py        # 自动完成 API 降级 + 打 wheelhouse + 生成 index.html
git add -A && git commit -m "update" && git push
```

构建脚本会自动处理三件 streamlit 1.40 兼容问题：
`width="stretch"` → `use_container_width=True`；`st.iframe` → `st.components.v1.html`；
`st.dataframe` → 设计系统 HTML 表格（stlite 的 streamlit 构建走 fastparquet 序列化，
Pyodide 无法安装该包，故静态版用等效表格渲染）。

## 已知取舍

- 静态版运行 streamlit 1.40.1（stlite 0.75 内置），交互行为与云端 1.65 版一致，
  仅上述三处 API 做了等价降级；云端版保持最新 API 不变。
- 表格为 HTML 渲染，不支持列排序/下载 CSV（原演示亦未使用这些交互）。
- 多页面导航、实时推送模拟、SOS 告警、处置联动、Plotly 图表均正常。
