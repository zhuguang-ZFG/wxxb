# 需求文档：统一图形界面（Unified GUI）

## 介绍

本需求文档定义了 linktunnel 项目的统一图形界面（Unified GUI）功能。该功能旨在将项目中所有独立的功能模块（串口工具、网络中继、代理管理、Grbl CNC 控制、BLE 蓝牙扫描、Linux I2C 扫描）整合到一个现代化的桌面应用程序中，提供统一的操作入口和协同工作能力。

当前 linktunnel 项目包含多个功能模块，但大部分只有命令行接口，代理功能虽有 3 种独立 UI（浏览器/tkinter/WebView），但缺乏统一的用户体验。用户需要记忆大量 CLI 命令，功能之间无法协同工作。统一图形界面将解决这些问题，为嵌入式开发者、网络工程师、CNC 操作员和硬件调试人员提供一站式工具平台。

## 术语表

- **Unified_GUI**: 统一图形界面应用程序，整合所有 linktunnel 功能模块的桌面应用
- **Module_Panel**: 功能模块面板，每个功能模块的独立操作界面
- **Navigation_System**: 导航系统，用于在不同功能模块之间切换的界面组件（侧边栏或标签页）
- **Log_Viewer**: 日志查看器，统一显示所有模块运行日志的组件
- **Config_Manager**: 配置管理器，管理应用程序和各模块配置的组件
- **Serial_Module**: 串口工具模块，包含串口桥接和调试终端功能
- **Network_Module**: 网络中继模块，包含 TCP/UDP 透明中继功能
- **Proxy_Module**: 代理管理模块，包含 Mihomo/Clash 代理配置和控制功能
- **Grbl_Module**: Grbl CNC 控制模块，包含 Grbl/Grbl_Esp32 设备控制功能
- **BLE_Module**: BLE 蓝牙扫描模块，包含蓝牙设备发现功能
- **I2C_Module**: Linux I2C 扫描模块，包含 I2C 总线扫描功能
- **Backend_Logic**: 后端逻辑，现有的功能实现代码（复用）
- **CLI_Interface**: 命令行接口，现有的命令行工具（保持向后兼容）

## 需求

### 需求 1：应用程序架构

**用户故事：** 作为开发者，我希望统一图形界面采用模块化架构，以便于维护和扩展新功能。

#### 验收标准

1. THE Unified_GUI SHALL 使用 Python 实现
2. THE Unified_GUI SHALL 支持 Windows、macOS 和 Linux 操作系统
3. THE Unified_GUI SHALL 复用现有的 Backend_Logic 代码
4. THE Unified_GUI SHALL 保持 CLI_Interface 向后兼容
5. WHERE 用户选择 tkinter 实现，THE Unified_GUI SHALL 不依赖额外的第三方库
6. WHERE 用户选择 PyQt/PySide 实现，THE Unified_GUI SHALL 提供更现代的用户界面

### 需求 2：主窗口和导航

**用户故事：** 作为用户，我希望通过直观的导航系统访问所有功能模块，以便快速切换不同工具。

#### 验收标准

1. THE Unified_GUI SHALL 提供主窗口，包含 Navigation_System 和 Module_Panel 显示区域
2. THE Navigation_System SHALL 支持侧边栏或标签页两种导航模式
3. WHEN 用户点击导航项，THE Unified_GUI SHALL 切换到对应的 Module_Panel
4. THE Navigation_System SHALL 显示以下模块：Serial_Module、Network_Module、Proxy_Module、Grbl_Module、BLE_Module、I2C_Module
5. THE Unified_GUI SHALL 在主窗口底部显示统一的状态栏
6. THE Unified_GUI SHALL 支持窗口大小调整，最小尺寸不小于 1024x768 像素

### 需求 3：串口工具模块

**用户故事：** 作为嵌入式开发者，我希望在图形界面中使用串口桥接和调试终端功能，以便监控串口通信。

#### 验收标准

1. THE Serial_Module SHALL 提供串口列表刷新功能
2. THE Serial_Module SHALL 提供串口桥接配置界面，包含端口 A、端口 B、波特率、数据位、停止位、校验位参数
3. WHEN 用户启动串口桥接，THE Serial_Module SHALL 调用现有的 bridge.py Backend_Logic
4. THE Serial_Module SHALL 提供串口调试终端界面，包含接收区域和发送区域
5. THE Serial_Module SHALL 支持文本模式和十六进制模式切换
6. THE Serial_Module SHALL 支持编码选择（UTF-8、ASCII、GBK）
7. THE Serial_Module SHALL 支持时间戳显示、周期发送、保存接收数据功能
8. THE Serial_Module SHALL 显示 RX/TX 字节统计信息

### 需求 4：网络中继模块

**用户故事：** 作为网络工程师，我希望在图形界面中配置和监控 TCP/UDP 中继，以便调试网络通信。

#### 验收标准

1. THE Network_Module SHALL 提供 TCP 中继配置界面，包含监听地址、目标地址参数
2. THE Network_Module SHALL 提供 UDP 中继配置界面，包含监听地址、目标地址参数
3. THE Network_Module SHALL 支持 IPv4 和 IPv6 地址格式
4. WHEN 用户启动网络中继，THE Network_Module SHALL 调用现有的 tcp_udp.py Backend_Logic
5. THE Network_Module SHALL 实时显示经过的数据流量
6. THE Network_Module SHALL 支持十六进制日志显示
7. THE Network_Module SHALL 显示连接状态和统计信息

### 需求 5：代理管理模块

**用户故事：** 作为网络工程师，我希望在统一界面中管理 Mihomo 代理节点，以便集中控制代理服务。

#### 验收标准

1. THE Proxy_Module SHALL 整合现有的 client_app.py 功能
2. THE Proxy_Module SHALL 提供代理配置初始化界面，支持订阅 URL 和 YAML 导入
3. THE Proxy_Module SHALL 提供代理服务启动、停止、状态查询功能
4. THE Proxy_Module SHALL 显示代理模式（rule/global/direct）切换控件
5. THE Proxy_Module SHALL 显示策略组和节点列表
6. THE Proxy_Module SHALL 支持节点筛选和延迟测试
7. THE Proxy_Module SHALL 支持切换节点和关闭连接操作
8. THE Proxy_Module SHALL 提供浏览器控制台打开功能（Yacd 或本地 UI）

### 需求 6：Grbl CNC 控制模块

**用户故事：** 作为 CNC 操作员，我希望在图形界面中控制 Grbl 设备，以便实时监控和操作 CNC 机器。

#### 验收标准

1. THE Grbl_Module SHALL 提供设备连接配置界面，支持串口和 WiFi Telnet 连接
2. THE Grbl_Module SHALL 提供实时状态监控界面，显示机器位置、状态和缓冲区信息
3. THE Grbl_Module SHALL 提供 G 代码文件流式传输功能
4. THE Grbl_Module SHALL 提供设置查询和修改界面
5. THE Grbl_Module SHALL 提供复位、暂停、恢复控制按钮
6. WHEN 用户加载 G 代码文件，THE Grbl_Module SHALL 显示预览和进度信息
7. THE Grbl_Module SHALL 支持手动命令输入和发送

### 需求 7：BLE 蓝牙扫描模块

**用户故事：** 作为硬件调试人员，我希望在图形界面中扫描 BLE 设备，以便发现和识别蓝牙设备。

#### 验收标准

1. THE BLE_Module SHALL 提供扫描超时时间配置
2. WHEN 用户启动扫描，THE BLE_Module SHALL 调用现有的 ble_scan.py Backend_Logic
3. THE BLE_Module SHALL 以表格形式显示扫描结果，包含设备名称、地址、RSSI 信号强度
4. THE BLE_Module SHALL 支持扫描结果导出功能
5. WHERE 系统未安装 BLE 依赖，THE BLE_Module SHALL 显示安装提示信息

### 需求 8：Linux I2C 扫描模块

**用户故事：** 作为硬件调试人员，我希望在图形界面中扫描 I2C 总线，以便识别连接的 I2C 设备。

#### 验收标准

1. THE I2C_Module SHALL 提供 I2C 总线编号选择
2. WHEN 用户启动扫描，THE I2C_Module SHALL 调用现有的 i2c_linux.py Backend_Logic
3. THE I2C_Module SHALL 以网格形式显示扫描结果，标识已响应的地址
4. THE I2C_Module SHALL 支持扫描结果导出功能
5. WHERE 系统不是 Linux 或缺少 I2C 依赖，THE I2C_Module SHALL 显示不可用提示

### 需求 9：统一日志查看器

**用户故事：** 作为用户，我希望在统一的日志查看器中查看所有模块的运行日志，以便排查问题和监控系统状态。

#### 验收标准

1. THE Unified_GUI SHALL 提供 Log_Viewer 组件
2. THE Log_Viewer SHALL 显示所有模块的日志输出
3. THE Log_Viewer SHALL 支持日志级别过滤（DEBUG、INFO、WARNING、ERROR）
4. THE Log_Viewer SHALL 支持日志内容搜索
5. THE Log_Viewer SHALL 支持日志清空和导出功能
6. THE Log_Viewer SHALL 支持自动滚动到最新日志
7. THE Log_Viewer SHALL 为不同日志级别使用不同颜色显示

### 需求 10：配置管理

**用户故事：** 作为用户，我希望应用程序能够保存和恢复我的配置，以便下次使用时无需重新设置。

#### 验收标准

1. THE Config_Manager SHALL 保存用户的模块配置到本地文件
2. WHEN 应用程序启动，THE Config_Manager SHALL 加载上次保存的配置
3. THE Config_Manager SHALL 支持配置导入和导出功能
4. THE Config_Manager SHALL 支持恢复默认配置功能
5. WHERE 配置文件损坏，THE Config_Manager SHALL 使用默认配置并提示用户

### 需求 11：跨模块协同

**用户故事：** 作为用户，我希望不同功能模块之间能够协同工作，以便实现复杂的调试场景。

#### 验收标准

1. THE Unified_GUI SHALL 允许多个模块同时运行
2. WHEN 串口被某个模块占用，THE Unified_GUI SHALL 在其他模块中标识该串口为不可用
3. THE Unified_GUI SHALL 提供全局快捷键支持，用于快速切换模块和停止所有操作
4. THE Unified_GUI SHALL 在状态栏显示当前运行的模块数量

### 需求 12：错误处理和用户反馈

**用户故事：** 作为用户，我希望应用程序能够清晰地提示错误信息，以便我能够快速定位和解决问题。

#### 验收标准

1. WHEN 模块操作失败，THE Unified_GUI SHALL 显示错误对话框，包含错误描述和建议操作
2. WHEN 缺少依赖库，THE Unified_GUI SHALL 显示安装提示和命令
3. WHEN 配置参数无效，THE Unified_GUI SHALL 在输入框旁显示验证错误提示
4. THE Unified_GUI SHALL 在长时间操作时显示进度指示器
5. THE Unified_GUI SHALL 在操作成功时显示简短的成功提示

### 需求 13：性能和资源管理

**用户故事：** 作为用户，我希望应用程序运行流畅且资源占用合理，以便在资源受限的环境中使用。

#### 验收标准

1. THE Unified_GUI SHALL 在空闲状态下 CPU 占用率低于 5%
2. THE Unified_GUI SHALL 在空闲状态下内存占用低于 200MB
3. WHEN 日志超过 10000 行，THE Log_Viewer SHALL 自动清理旧日志
4. THE Unified_GUI SHALL 在后台线程中执行耗时操作，避免界面冻结
5. WHEN 用户关闭应用程序，THE Unified_GUI SHALL 正确停止所有运行中的模块

### 需求 14：帮助和文档

**用户故事：** 作为新用户，我希望应用程序提供帮助文档，以便快速学习如何使用各个功能。

#### 验收标准

1. THE Unified_GUI SHALL 提供帮助菜单，包含用户手册链接
2. THE Unified_GUI SHALL 为每个模块提供工具提示（tooltip）说明
3. THE Unified_GUI SHALL 提供关于对话框，显示版本信息和许可证
4. THE Unified_GUI SHALL 提供快捷键列表查看功能

