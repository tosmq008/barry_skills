# UI设计规范 - 待办事项管理系统

## 1. 设计理念

**核心设计原则:**
- **简洁** - 去除不必要的装饰，聚焦内容
- **高效** - 减少操作步骤，提升效率
- **清晰** - 信息层级分明，易于理解
- **一致** - 保持视觉和交互的一致性

**设计风格:**
- 现代简约风格
- 扁平化设计
- 微妙的阴影和圆角
- 流畅的动画过渡

---

## 2. 颜色系统

### 2.1 主色调

| 颜色名称 | Hex | RGB | 用途 |
|----------|-----|-----|------|
| **主色** | `#3B82F6` | rgb(59, 130, 246) | 主要按钮、链接、高亮 |
| **主色-浅** | `#60A5FA` | rgb(96, 165, 250) | Hover状态 |
| **主色-深** | `#2563EB` | rgb(37, 99, 235) | Active状态 |
| **主色-极浅** | `#DBEAFE` | rgb(219, 234, 254) | 背景、标签 |

### 2.2 中性色

| 颜色名称 | Hex | RGB | 用途 |
|----------|-----|-----|------|
| **黑色** | `#1F2937` | rgb(31, 41, 55) | 标题、重要文本 |
| **深灰** | `#4B5563` | rgb(75, 85, 99) | 正文文本 |
| **中灰** | `#9CA3AF` | rgb(156, 163, 175) | 次要文本、图标 |
| **浅灰** | `#E5E7EB` | rgb(229, 231, 235) | 边框、分隔线 |
| **极浅灰** | `#F3F4F6` | rgb(243, 244, 246) | 背景、卡片 |
| **白色** | `#FFFFFF` | rgb(255, 255, 255) | 主背景 |

### 2.3 功能色

| 颜色名称 | Hex | RGB | 用途 |
|----------|-----|-----|------|
| **成功** | `#10B981` | rgb(16, 185, 129) | 成功提示、完成状态 |
| **警告** | `#F59E0B` | rgb(245, 158, 11) | 警告提示、即将过期 |
| **错误** | `#EF4444` | rgb(239, 68, 68) | 错误提示、删除操作 |
| **信息** | `#3B82F6` | rgb(59, 130, 246) | 信息提示 |

### 2.4 优先级颜色

| 优先级 | 颜色 | Hex | 用途 |
|--------|------|-----|------|
| **高** | 红色 | `#EF4444` | 高优先级任务 |
| **中** | 黄色 | `#F59E0B` | 中优先级任务 |
| **低** | 蓝色 | `#3B82F6` | 低优先级任务 |
| **无** | 灰色 | `#9CA3AF` | 无优先级任务 |

---

## 3. 字体系统

### 3.1 字体家族

**中文:**
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
```

**英文/数字:**
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**等宽字体（代码）:**
```css
font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
```

### 3.2 字号层级

| 层级 | 字号 | 行高 | 用途 |
|------|------|------|------|
| **H1** | 32px | 40px | 页面主标题 |
| **H2** | 24px | 32px | 区块标题 |
| **H3** | 20px | 28px | 卡片标题 |
| **H4** | 18px | 26px | 小标题 |
| **Body** | 16px | 24px | 正文 |
| **Small** | 14px | 20px | 次要文本 |
| **Tiny** | 12px | 18px | 辅助文本 |

### 3.3 字重

| 字重 | 值 | 用途 |
|------|-----|------|
| **Regular** | 400 | 正文 |
| **Medium** | 500 | 强调文本 |
| **Semibold** | 600 | 标题 |
| **Bold** | 700 | 重要标题 |

---

## 4. 间距系统

### 4.1 基础间距单位

使用 8px 为基础单位，所有间距都是 8 的倍数。

| 名称 | 值 | 用途 |
|------|-----|------|
| **xs** | 4px | 极小间距 |
| **sm** | 8px | 小间距 |
| **md** | 16px | 中等间距 |
| **lg** | 24px | 大间距 |
| **xl** | 32px | 超大间距 |
| **2xl** | 48px | 区块间距 |

### 4.2 组件间距

| 组件 | 内边距 | 外边距 |
|------|--------|--------|
| **按钮** | 12px 24px | - |
| **输入框** | 12px 16px | - |
| **卡片** | 16px | 16px |
| **列表项** | 12px 16px | - |
| **侧边栏** | 16px | - |

---

## 5. 圆角系统

| 名称 | 值 | 用途 |
|------|-----|------|
| **none** | 0px | 无圆角 |
| **sm** | 4px | 小元素（标签、徽章） |
| **md** | 8px | 按钮、输入框 |
| **lg** | 12px | 卡片、面板 |
| **xl** | 16px | 大卡片 |
| **full** | 9999px | 圆形（头像） |

---

## 6. 阴影系统

| 名称 | 值 | 用途 |
|------|-----|------|
| **sm** | `0 1px 2px rgba(0, 0, 0, 0.05)` | 轻微阴影 |
| **md** | `0 4px 6px rgba(0, 0, 0, 0.1)` | 卡片阴影 |
| **lg** | `0 10px 15px rgba(0, 0, 0, 0.1)` | 弹窗阴影 |
| **xl** | `0 20px 25px rgba(0, 0, 0, 0.15)` | 大弹窗阴影 |

---

## 7. 组件规范

### 7.1 按钮

**主要按钮（Primary）:**
```css
background: #3B82F6;
color: #FFFFFF;
padding: 12px 24px;
border-radius: 8px;
font-size: 16px;
font-weight: 500;
```

**次要按钮（Secondary）:**
```css
background: #FFFFFF;
color: #3B82F6;
border: 1px solid #3B82F6;
padding: 12px 24px;
border-radius: 8px;
```

**文本按钮（Text）:**
```css
background: transparent;
color: #3B82F6;
padding: 12px 16px;
```

**按钮状态:**
- Hover: 背景色加深 10%
- Active: 背景色加深 20%
- Disabled: 透明度 50%，不可点击

### 7.2 输入框

```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 8px;
padding: 12px 16px;
font-size: 16px;
color: #1F2937;
```

**状态:**
- Focus: 边框颜色 `#3B82F6`，添加阴影
- Error: 边框颜色 `#EF4444`
- Disabled: 背景色 `#F3F4F6`，文字颜色 `#9CA3AF`

### 7.3 复选框

**未选中:**
```css
width: 20px;
height: 20px;
border: 2px solid #E5E7EB;
border-radius: 4px;
```

**已选中:**
```css
background: #3B82F6;
border: 2px solid #3B82F6;
/* 内部显示白色对勾图标 */
```

### 7.4 任务项

```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 8px;
padding: 12px 16px;
margin-bottom: 8px;
```

**Hover状态:**
```css
background: #F9FAFB;
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
```

**已完成状态:**
```css
opacity: 0.6;
text-decoration: line-through;
```

### 7.5 标签

```css
background: #DBEAFE;
color: #1E40AF;
padding: 4px 12px;
border-radius: 4px;
font-size: 14px;
```

### 7.6 卡片

```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 12px;
padding: 16px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
```

---

## 8. 布局规范

### 8.1 三栏布局

```
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌────────────────────────┐  ┌──────────────┐ │
│  │          │  │                        │  │              │ │
│  │  侧边栏  │  │      主内容区          │  │  详情面板    │ │
│  │  240px   │  │      flex-1            │  │  360px       │ │
│  │          │  │                        │  │              │ │
│  └──────────┘  └────────────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 侧边栏

- 宽度: 240px
- 背景: `#F9FAFB`
- 边框: 右侧 1px `#E5E7EB`
- 内边距: 16px

### 8.3 主内容区

- 宽度: flex-1（自适应）
- 背景: `#FFFFFF`
- 内边距: 24px
- 最大宽度: 1200px

### 8.4 详情面板

- 宽度: 360px
- 背景: `#FFFFFF`
- 边框: 左侧 1px `#E5E7EB`
- 内边距: 24px

---

## 9. 动画规范

### 9.1 过渡动画

```css
transition: all 0.2s ease-in-out;
```

### 9.2 常用动画

**淡入:**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
animation: fadeIn 0.3s ease-in-out;
```

**滑入:**
```css
@keyframes slideIn {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
animation: slideIn 0.3s ease-in-out;
```

**完成动画:**
```css
@keyframes checkmark {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}
```

---

## 10. 图标系统

**图标库**: Heroicons (https://heroicons.com/)

**常用图标:**
- 添加: `plus`
- 删除: `trash`
- 编辑: `pencil`
- 搜索: `magnifying-glass`
- 设置: `cog-6-tooth`
- 用户: `user`
- 列表: `list-bullet`
- 标签: `tag`
- 日历: `calendar`
- 完成: `check`

**图标尺寸:**
- 小: 16px
- 中: 20px
- 大: 24px

---

## 11. 响应式断点

| 断点 | 宽度 | 设备 |
|------|------|------|
| **xs** | < 640px | 手机 |
| **sm** | 640px - 768px | 大手机 |
| **md** | 768px - 1024px | 平板 |
| **lg** | 1024px - 1280px | 小桌面 |
| **xl** | > 1280px | 大桌面 |

---

## 12. 暗色模式（未来版本）

**主色调:**
- 背景: `#1F2937`
- 卡片: `#374151`
- 文字: `#F9FAFB`
- 边框: `#4B5563`

---

**文档版本**: v1.0
**创建日期**: 2026-02-06
**最后更新**: 2026-02-06
**文档状态**: 待评审
