# linktunnel

串口双端桥接、**单串口调试终端**（`serial term`，能力对齐常见助手如 **[RYCOM](https://github.com/rymcu/RYCOM)** 的 CLI 子集）、TCP/UDP 透明中继（带方向日志）、**本机 Mihomo 代理**（生成配置 + 启动内核）、**浏览器控制台**（`dashboard open`：在线 Yacd 或本机 `/ui`）、**自带图形客户端**（`linktunnel client`：tkinter，直连 API）、**独立桌面面板**（`linktunnel gui`：嵌入 WebView）、**Grbl / Grbl_Esp32**、**`clash`** API、串口 / 蓝牙枚举、BLE、Linux I2C 等。

> 协议侧与 [gnea/grbl](https://github.com/gnea/grbl) 一致；[Grbl_Esp32](https://github.com/bdring/Grbl_Esp32) 在 `Serial.cpp` 中说明：G 代码行以 `\r`/`\n` 结束且需等 `ok` 再发下一行，实时命令为单字节（如 `? ! ~`）。WiFi Telnet 可用 PySerial 的 `socket://` URL（端口以固件 / WebUI 配置为准）。

## 能力边界（重要）

| 需求 | 本工具能做什么 |
|------|----------------|
| **串口「穿透」** | 用 **两个** 物理/虚拟串口 **桥接**（A↔B 双向转发），中间可打日志。 |
| **单串口调试** | **`serial term`**：标准输入 → 串口、串口 → 标准输出；接收按 **`\n` / `\r` / `\r\n`** 分行；文本模式支持 **`--encoding utf-8|ascii|gbk`**（接收解码与发送编码；非法字节替换显示）；支持 **`--raw-rx`** 原始字节直出；另有 **`--hex` / `--hex-send`**、**`--timestamp`**、**`--period` + `--message`**、**`--save`**、**`--quiet`**；退出时默认 **RX/TX 字节统计**（与 RYCOM 等「助手」同类能力；本仓库为命令行实现）。 |
| **已被占用的串口** | 同一串口在常见系统上 **不能** 被两个进程同时打开；要「旁听」需 **硬件分路** 或 **另一路采集**，不能单靠本程序再开一次端口。 |
| **蓝牙经典 / RFCOMM** | 系统映射成 **串口设备**（如 macOS 的 `cu.Bluetooth-*`）时，按 **串口** 使用 `serial bridge` / `serial list`。 |
| **BLE** | 仅提供 **`ble scan`** 发现设备；BLE GATT 不是串口，不做 RFCOMM 嗅探。 |
| **网口** | **`net tcp` / `net udp`**：监听本地端口，转发到上游，并打印经过的数据。 |
| **I2C** | 仅在 **Linux** 上 **`i2c scan`** 扫描总线地址；I2C 无通用「双进程共享总线嗅探」软件方案，多主/监听需硬件与分析仪。 |
| **本机跑代理** | **`proxy`**：需单独安装 **[Mihomo](https://github.com/MetaCubeX/mihomo)**（`MIHOMO_BIN` 或 PATH；`linktunnel proxy doctor` 会按 **Windows / macOS / Linux** 提示应下载的包名）。配置目录：**Windows** `%LOCALAPPDATA%\linktunnel`，**macOS/Linux** 隐藏目录 `~/.linktunnel`。`proxy init --sub-url` 拉订阅；`proxy init --import-yaml` 导入 `proxies:`；`proxy run` 后台启动。 |
| **浏览器里看节点** | **`dashboard open`**：默认打开在线 [Yacd Meta](https://yacd.metacubex.one)；**`--panel local`** 打开本机 `http://127.0.0.1:9090/ui`（需 **`proxy init --embed-ui`** 且 **`proxy run`**）。**`dashboard info`** 说明与 Verge 的关系。 |
| **自带客户端（不嵌网页）** | **`linktunnel client`** 或 **`linktunnel-client`**：用 **tkinter** 直连 External Controller（交互参考 **Clash Verge Rev** 常用能力）：**rule/global/direct**、**监听端口摘要**（mixed/http/socks）、策略组与节点、**筛选**、**复制 API**、**延迟测试**、**关闭全部连接**、**切换模式时可断开连接**；**「其他工具」标签页**可一键运行常用 **`linktunnel` CLI**（如 `serial list`、`proxy doctor`、`dashboard info`）并查看输出。手动刷新时 **并行拉取** 多路 API，自动刷新为轻量轮询（不拉 `/version`）。仅需系统 Tk；无 tkinter 时需安装 **python3-tk** / **python-tk** 等。 |
| **独立桌面窗口（非系统浏览器）** | **`linktunnel gui`** 或 **`linktunnel-gui`**：同一套面板 URL，在 **独立窗口** 内嵌 WebView（需 **`pip install 'linktunnel[desktop]'`**）。Windows 需 **WebView2**；macOS 用系统 WebKit；Linux 需 **GTK + WebKitGTK**（各发行版包名不同）。 |
| **Clash Verge / 已有内核** | **`clash`** 遥控已在跑的 Mihomo；完整 GUI 请另装 **Clash Verge Rev**（见 `dashboard info`）。 |

## 安装

```bash
cd /path/to/wxxb
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# 可选：BLE 扫描
pip install 'linktunnel[ble]'

# 可选：Linux I2C
pip install 'linktunnel[i2c]'

# 可选：独立桌面面板（pywebview）
pip install 'linktunnel[desktop]'

# 开发 / 自测（含 ruff + pytest，与 CI 一致）
pip install -e '.[dev]'
ruff check src tests && ruff format --check src tests && pytest -q
```

## 用法示例

```bash
# 列出串口（含蓝牙串口设备）
linktunnel serial list
linktunnel serial list --bluetooth-only

# 桥接 USB-TTL 与 蓝牙串口；--quiet 不往终端打 payload，可配合 --log 只写文件；--bytesize 5–8
linktunnel serial bridge --a /dev/ttyUSB0 --b /dev/cu.Bluetooth-Incoming-Port --baud 115200 --hex
linktunnel serial bridge --a COM3 --b COM4 --quiet --log bridge.log

# 单串口终端（参考 RYCOM 类助手：收发、HEX、时间戳、周期发、保存、统计）
linktunnel serial term -p /dev/ttyUSB0 --baud 115200
linktunnel serial term -p COM3 --encoding gbk
linktunnel serial term -p COM3 --hex -t --save ./rx.bin
linktunnel serial term -p /dev/ttyUSB0 --hex-send --eol none
linktunnel serial term -p COM5 -m 'AT' --period 2 --no-stdin
linktunnel serial term -p /dev/ttyUSB0 --send-file ./payload.bin --no-stdin

# TCP 穿透：支持 IPv6 写法 `[::1]:9000`；启动时会打印 [tcp] listening …
linktunnel net tcp --listen 127.0.0.1:9000 --target example.com:80
linktunnel net tcp --listen [::]:8080 --target '[2001:db8::1]:443'

# UDP 中继（多客户端时「回包」发往最近一个客户端）；启动时打印 [udp] relay …
linktunnel net udp --listen 0.0.0.0:5000 --target 192.168.1.10:5000 --log ./udp.log

# BLE 扫描（需 pip install 'linktunnel[ble]'）
linktunnel ble scan --timeout 5

# Linux I2C 扫描（需权限访问 /dev/i2c-N）
linktunnel i2c scan --bus 1

# --- Grbl / Grbl_Esp32（USB 串口 -p 或 WiFi Telnet -u）---
linktunnel grbl report --port /dev/ttyUSB0
linktunnel grbl status --port COM5 --raw
linktunnel grbl settings --url socket://192.168.4.1:23
linktunnel grbl stream ./job.nc --port /dev/ttyUSB0 -v
# 仅校验 G 代码解析（不占串口）
linktunnel grbl stream ./job.nc --dry-run --dry-preview 0
linktunnel grbl monitor --port /dev/ttyUSB0 --decode-status
# 监视时向 stdin 输入行即可下发；解码后的状态摘要打到 stderr
linktunnel grbl reset --port /dev/ttyUSB0

# --- Clash Verge Rev / Mihomo 外部控制（默认 http://127.0.0.1:9090）---
export CLASH_API=http://127.0.0.1:9090
export CLASH_SECRET=你的密钥   # 若未设置 secret 可省略
linktunnel clash version
linktunnel clash configs
linktunnel clash proxies
linktunnel clash mode
linktunnel clash mode global
linktunnel clash select GLOBAL 节点名称
linktunnel clash connections

# --- 本机 Mihomo 代理（跨系统：先 doctor，再按提示下载内核）---
linktunnel proxy doctor
# 订阅 URL（由内核拉取并解析节点）
linktunnel proxy init --sub-url 'https://example.com/subscription'
# 或从 Clash YAML 导入 proxies 列表
linktunnel proxy init --import-yaml ./proxies_fragment.yaml
linktunnel proxy run
# 浏览器：系统代理指向本机 mixed-port（默认 7890，见生成的 config.yaml）
linktunnel proxy status
linktunnel proxy stop

# --- 浏览器控制台（系统默认浏览器）---
linktunnel dashboard info
linktunnel dashboard open
linktunnel dashboard open --from-profile
# 本机 Mihomo 内置页（需 init 时加 --embed-ui 且内核已运行）
linktunnel proxy init --sub-url 'https://example.com/sub' --embed-ui
linktunnel proxy run
linktunnel dashboard open --panel local --from-profile

# --- 自带图形客户端（tkinter，直连 Mihomo API；无需 linktunnel[desktop]）---
linktunnel client
linktunnel client --from-profile
linktunnel-client --api http://127.0.0.1:9090

# --- 独立桌面面板（嵌入 WebView；需 pip install 'linktunnel[desktop]'）---
linktunnel gui
linktunnel gui --from-profile
linktunnel gui --panel local --from-profile
# 等价入口（参数与 linktunnel gui 相同）
linktunnel-gui --from-profile
```

## 许可证

见仓库内 `LICENSE`。
