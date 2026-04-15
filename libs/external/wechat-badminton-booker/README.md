# 微信小程序羽毛球场地预约脚本

这个目录提供三种能力：

1. **电脑端可视化界面（推荐）**：`ui_app.py`（Streamlit，表单配置 + 一键启动）。
2. **电脑端命令行**：`pc_booker.py`（Playwright 浏览器自动化）。
3. **手机端（Android）**：`booker.auto.js`（Auto.js 无障碍自动化）。

> 你给的地址 `https://xcx-api.zuduijun.com/api/long-url?code=AzYr2i&app=13` 可以作为初始入口地址填入 UI；
> 但如果只是“活动详情落地页”而不是真正可点击预约的业务页，仍需在登录后跳转到实际预约页再抓选择器。

---

## 🚀 最快上手（建议按这个做）

### 第 0 步：准备环境（只做一次）

```bash
cd libs/external/wechat-badminton-booker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-pc.txt
python -m playwright install chromium
```

### 第 1 步：启动可视化界面

```bash
streamlit run ui_app.py
```

打开浏览器进入本地页面（通常是 `http://localhost:8501`）。

### 第 2 步：在界面中填 6 类信息

1. `预约入口 URL`：先填你给的 URL 即可。
2. `放号时间`：默认 `23:00:00`。
3. `提前预约天数`：填 `2`。
4. `首选` 与 `候补`（场地、时段）。
5. `提交按钮文案`（如：立即预约、确认预约、提交）。
6. `页面选择器`（日期/场地/时段）。

### 第 3 步：先点“保存配置”

点击 **💾 保存配置**，会生成：

- `libs/external/wechat-badminton-booker/config.yaml`

### 第 4 步：再点“启动预约”

点击 **🚀 启动预约**：

- 程序会先打开浏览器。
- 如果开启了“手动登录后继续”，你先登录账号再回到终端按回车。
- 然后程序会等待到 `23:00:00` 自动执行抢位。

### 第 5 步：第一次一定做“提前演练”

建议把 `放号时间` 临时改成当前时间后 1 分钟，验证以下流程都正常：

- 能打开正确页面。
- 能点中日期。
- 能点中场地和时段。
- 能点中提交按钮。

演练通过后，再改回 `23:00:00`。

---

## A. 电脑端可视化交互界面（新）

### 1) 环境准备

```bash
cd libs/external/wechat-badminton-booker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-pc.txt
python -m playwright install chromium
```

### 2) 启动 UI

```bash
streamlit run ui_app.py
```

默认会打开本地 Web 页面（通常是 `http://localhost:8501`）。

### 3) 在 UI 中完成配置

- 填 `预约入口 URL`（可先用你给的 URL）。
- 填放号时间（默认 `23:00:00`）。
- 填首选/候补场地与时段。
- 填日期/场地/时段/提交按钮对应选择器模板。
- 点击 **保存配置**，再点 **启动预约**。

### 4) UI 已实现的交互

- 表单化参数配置（不用手改 YAML）。
- 自动预览“提前 N 天”的目标日期。
- 实时展示候选组合优先级表格。
- 一键保存 `config.yaml`。
- 一键启动任务并实时滚动日志。

---

## B. 电脑端命令行（Playwright）

### 1) 配置

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`：

- `runtime.start_at`: 放号时间。
- `booking.advance_days`: 提前预约天数（默认 2）。
- `booking.target_*` 与 `fallback_*`: 首选与候补。
- `selectors.*`: 按你的页面 DOM 填写。

### 2) 运行

```bash
python pc_booker.py --config config.yaml
```

默认 `manual_login: true`，脚本会先打开浏览器，你手动登录后按回车，脚本才继续等待到 23:00 抢位。

---

## C. 怎么找选择器（最关键）

如果你不知道 `selectors` 怎么填，按下面做：

1. 在浏览器打开预约页面。
2. 按 `F12` 打开开发者工具。
3. 点左上角“箭头选取元素”。
4. 依次点页面上的：
   - 某一天日期按钮。
   - 某个场地按钮。
   - 某个时段按钮。
   - 提交按钮。
5. 复制它们的稳定特征（`data-*` 属性、按钮文本、class）。

推荐优先使用：

- `data-date`、`data-court`、`data-slot` 这类业务属性。
- 其次用文本 XPath，例如：
  - `xpath=//*[contains(normalize-space(.), '1号场')]`

不要优先用随机 class（容易失效）。

---

## D. 手机端方案（Auto.js）

适用场景：你在 23:00 前已进入小程序预约页，希望手机自动点选。

1. 在 Auto.js 新建脚本，粘贴 `booker.auto.js`。
2. 修改顶部 `CONFIG`（首选、候补、按钮文案）。
3. 23:00 前运行脚本。

---

## E. 现实限制与建议

- 若系统有验证码、短信二次验证、风控拦截，仍需人工介入。
- 抢位成功率受网络、设备、并发压力影响，无法 100% 保证。
- 请确认使用方式符合平台条款与场馆规则。
- 最稳妥的落地方式：你把页面 HTML 片段（日期/场地/时段/提交按钮）发我，我可直接帮你把选择器调到可用。
