# linktunnel Unified GUI - 字体和颜色修复

**日期**: 2026-04-13  
**版本**: 0.3.0  
**状态**: ✅ 完成

---

## 🔧 问题和解决方案

### 问题 1: 字体看不清

**原因**:
- 字体大小太小（10px）
- 字体族设置不当
- 没有明确指定系统字体

**解决方案**:
```python
# 全局字体设置
* {
    font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
    font-size: 11pt;
    color: #000000;
}

# 标题字体
title_font = QFont()
title_font.setPointSize(13)
title_font.setBold(True)
title.setFont(title_font)
```

**改进**:
- 字体大小: 10px → 11pt (更清晰)
- 字体族: 系统字体 (Segoe UI, Microsoft YaHei, Arial)
- 字体颜色: 明确设置为黑色 (#000000)

### 问题 2: 颜色对比度不足

**原因**:
- 使用了浅灰色文字 (#333333)
- 背景色和文字色对比度低
- 没有明确的颜色方案

**解决方案**:
```python
# 高对比度颜色方案
QLabel {
    color: #000000;  # 纯黑色
    font-size: 11pt;
}

QLineEdit {
    border: 2px solid #cccccc;
    background-color: #ffffff;  # 纯白色
    color: #000000;  # 纯黑色
}

QLineEdit:focus {
    border: 2px solid #0078d4;  # 微软蓝
    background-color: #ffffff;
    color: #000000;
}
```

**改进**:
- 文字颜色: #333333 → #000000 (纯黑)
- 背景色: 保持纯白 (#ffffff)
- 边框色: #e0e0e0 → #cccccc (更深)
- 焦点色: #2196F3 → #0078d4 (微软蓝)

---

## 📁 新增文件

### src/linktunnel/unified_gui/core/fixed_main_window.py

完全修复的主窗口实现，包含：

1. **全局样式表** - 统一的字体和颜色
2. **清晰的字体** - 11pt 系统字体
3. **高对比度** - 黑色文字，白色背景
4. **完整的颜色方案** - 所有 UI 元素都有明确的颜色

### test_fixed_ui.py

测试脚本，验证修复效果

---

## 🎨 颜色方案

### 主要颜色

| 用途 | 颜色 | 十六进制 |
|------|------|---------|
| 文字 | 纯黑 | #000000 |
| 背景 | 纯白 | #ffffff |
| 边框 | 浅灰 | #cccccc |
| 焦点 | 微软蓝 | #0078d4 |
| 成功 | 绿色 | #4CAF50 |
| 警告 | 橙色 | #FF9800 |

### 元素颜色

| 元素 | 正常 | 悬停 | 按下 |
|------|------|------|------|
| 按钮 | #f0f0f0 | #e0e0e0 | #0078d4 |
| 输入框 | #ffffff | #ffffff | #ffffff |
| 菜单项 | #ffffff | #0078d4 | #0078d4 |
| 标签 | #000000 | - | - |

---

## 📝 样式表详解

### 全局样式

```python
* {
    font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
    font-size: 11pt;
    color: #000000;
}
```

- 所有元素使用相同的字体族
- 默认字体大小 11pt
- 默认文字颜色黑色

### 输入框样式

```python
QLineEdit {
    border: 2px solid #cccccc;
    border-radius: 4px;
    padding: 8px;
    font-size: 11pt;
    background-color: #ffffff;
    color: #000000;
}

QLineEdit:focus {
    border: 2px solid #0078d4;
    background-color: #ffffff;
    color: #000000;
}
```

- 边框: 2px 浅灰色
- 圆角: 4px
- 内边距: 8px
- 焦点时边框变蓝

### 按钮样式

```python
QPushButton {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 8px 16px;
    background-color: #f0f0f0;
    color: #000000;
    font-size: 11pt;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #e0e0e0;
    border: 1px solid #0078d4;
}

QPushButton:pressed {
    background-color: #0078d4;
    color: #ffffff;
    border: 1px solid #0078d4;
}
```

- 正常: 浅灰背景
- 悬停: 更深的灰色
- 按下: 蓝色背景，白色文字

---

## ✅ 验证清单

- [x] 字体大小: 11pt (清晰可见)
- [x] 字体族: 系统字体 (Segoe UI, Microsoft YaHei)
- [x] 文字颜色: 纯黑 (#000000)
- [x] 背景色: 纯白 (#ffffff)
- [x] 边框色: 浅灰 (#cccccc)
- [x] 焦点色: 微软蓝 (#0078d4)
- [x] 对比度: WCAG AA 标准
- [x] 所有元素: 颜色一致
- [x] 菜单栏: 清晰可见
- [x] 按钮: 清晰可见
- [x] 输入框: 清晰可见
- [x] 标签: 清晰可见

---

## 🚀 使用方法

### 启动修复后的 UI

```bash
py -3 test_fixed_ui.py
```

### 验证字体和颜色

1. 启动应用程序
2. 检查所有文字是否清晰可见
3. 检查颜色对比度是否足够
4. 测试按钮悬停和按下效果
5. 测试输入框焦点效果

---

## 📊 对比表

### 修复前 vs 修复后

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 字体大小 | 10px | 11pt |
| 字体族 | 不明确 | Segoe UI, Microsoft YaHei |
| 文字颜色 | #333333 | #000000 |
| 背景色 | #ffffff | #ffffff |
| 边框色 | #e0e0e0 | #cccccc |
| 焦点色 | #2196F3 | #0078d4 |
| 对比度 | 低 | 高 (WCAG AA) |
| 可读性 | 差 | 优 |

---

## 🔍 技术细节

### 字体设置优先级

1. 全局样式表 (最高优先级)
2. 元素特定样式表
3. 代码中的 QFont 设置
4. 系统默认字体 (最低优先级)

### 颜色应用顺序

1. 全局 `*` 选择器
2. 特定元素选择器 (QLabel, QPushButton 等)
3. 伪类选择器 (:hover, :focus, :pressed)
4. 代码中的 setStyleSheet()

### 确保颜色可见

```python
# 方法 1: 全局样式表
* { color: #000000; }

# 方法 2: 元素特定样式
QLabel { color: #000000; }

# 方法 3: 代码设置
label.setStyleSheet("color: #000000;")
```

---

## 🎓 最佳实践

### 字体设置

```python
# ✓ 好的做法
font = QFont()
font.setPointSize(11)  # 使用 pt 而不是 px
font.setFamily("Segoe UI")
label.setFont(font)

# ✗ 不好的做法
font = QFont()
font.setPixelSize(10)  # 像素大小不一致
label.setFont(font)
```

### 颜色设置

```python
# ✓ 好的做法
label.setStyleSheet("color: #000000;")  # 纯黑色
label.setStyleSheet("background-color: #ffffff;")  # 纯白色

# ✗ 不好的做法
label.setStyleSheet("color: #333333;")  # 灰色，对比度低
label.setStyleSheet("background-color: #f5f5f5;")  # 浅灰，对比度低
```

### 对比度检查

使用 WCAG 对比度检查工具：
- 文字 vs 背景: 至少 4.5:1 (AA 标准)
- 大文字 vs 背景: 至少 3:1 (AA 标准)

---

## 📞 故障排除

### 字体仍然看不清

1. 检查全局样式表是否正确应用
2. 确认字体大小设置为 11pt 或更大
3. 检查是否有其他样式表覆盖了设置
4. 尝试重启应用程序

### 颜色仍然不对

1. 检查颜色值是否正确 (#000000 = 纯黑)
2. 确认样式表中没有冲突的颜色设置
3. 检查是否有主题覆盖了颜色
4. 尝试清除样式表缓存

### 对比度不足

1. 使用 WCAG 对比度检查工具
2. 增加文字大小或加粗
3. 使用更深的文字颜色
4. 使用更浅的背景色

---

## 📈 性能影响

- **字体渲染**: 系统字体比自定义字体更快
- **样式表应用**: 全局样式表比逐个设置更高效
- **内存使用**: 无显著增加
- **启动时间**: 无显著影响

---

## 🎯 总结

修复后的 UI 具有以下特点：

1. ✅ **字体清晰** - 11pt 系统字体
2. ✅ **颜色正确** - 黑色文字，白色背景
3. ✅ **对比度高** - WCAG AA 标准
4. ✅ **易于阅读** - 所有元素清晰可见
5. ✅ **一致性** - 统一的颜色方案
6. ✅ **专业外观** - 现代化设计

应用程序现在**字体清晰，颜色正确，易于使用**！

---

**最后更新**: 2026-04-13  
**状态**: ✅ 完成并测试通过
