# 银发守护 · 概念演示（纯前端静态版）

高校公共空间适老化智能感知与服务系统的**浏览器内运行版**：完整 Streamlit 应用通过
[stlite](https://github.com/whitphx/stlite)（Pyodide/WASM）在浏览器里直接运行，
**不依赖任何服务器、不请求任何海外 CDN**——所有运行时资产（Pyodide、Streamlit、
pandas/numpy/plotly 等 28 个 wheel）均已自托管在本仓库的 `vendor/` 目录中。

## 这个包怎么工作

```
index.html            入口页（顶部品牌栏 + 加载提示 + 挂载点）
vercel.json           Vercel 部署配置（wasm 类型头 + 长期缓存）
vendor/
  stlite.min.js       stlite 运行时（Streamlit 1.40.1 + React 前端）
  static/             前端 chunk 资源
  pypi/               streamlit / stlite_lib wheel
  pyodide/            Pyodide v0.26.2 完整发行版 + 所需包 wheel
  wheelhouse.zip      预置 site-packages（blinker/tenacity/toml/pydeck/plotly/narwhals 等）
app/                  应用源码（已按 streamlit 1.40 做 API 降级，仅作存档）
```

- 首次打开需下载约 60–70MB 资产（通常 10–40 秒），之后走浏览器缓存。
- 页面内的「Streamlit Cloud 备用入口」链接指向原云端版本，两条路互为备份。

## 部署到 Cloudflare Pages（免费，约 5 分钟）

> Vercel 也可用（本仓库的 `vercel.json` 保留），但部分账号会遇到登录限制；
> Cloudflare Pages 无此问题，且推送后同样自动部署。二选一即可。

1. **GitHub 仓库已就绪**：`Lyubo7117/silver-guard-static`（已推送，含本页所有文件）。
2. **导入 Cloudflare Pages**：打开 https://dash.cloudflare.com → 注册/登录（免费）→
   左侧 **Workers & Pages** → **Create** → **Pages** 标签页 → **Connect to Git**：
   - 授权 GitHub，选择仓库 `silver-guard-static`
   - Project name：`silver-guard-static`
   - Framework preset：**None**
   - Build command：**留空**
   - Build output directory：**`/`**
   - 点 **Save and Deploy**，等 1–2 分钟
3. 得到 `https://silver-guard-static.pages.dev`（Custom domains 里可换名字）

以后每次 `git push`，Cloudflare **自动重新部署**。

### 备选：Vercel

https://vercel.com → Add New → Project → Import `silver-guard-static` →
Framework 选 Other，其余默认 → Deploy。得到 `*.vercel.app`。

## 本地预览

```bash
python -m http.server 8000   # 在 index.html 所在目录执行，打开 http://localhost:8000
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
- ⚠️ Cloudflare Pages 的 `*.pages.dev` 与 Vercel 的 `*.vercel.app` 域名在部分国内网络下访问不稳定。正式分发前建议
  用国内网络（如手机流量）实测；顶栏保留了「Streamlit Cloud 备用入口」链接，
  本地 `python -m http.server` 亦可作为答辩现场的兜底演示方式。
