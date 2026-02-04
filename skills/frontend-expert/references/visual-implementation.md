# 前端视觉实现指南

## 设计稿还原流程

### 1. 设计稿分析

**分析清单：**

| 分析项 | 内容 | 输出 |
|--------|------|------|
| 布局结构 | 页面整体布局、栅格系统 | 布局方案 |
| 设计规范 | 颜色、字体、间距、圆角 | CSS变量 |
| 组件识别 | 可复用组件、变体 | 组件清单 |
| 响应式 | 断点、适配策略 | 响应式方案 |
| 交互细节 | 悬停、点击、过渡效果 | 交互规范 |

### 2. 设计Token提取

```css
/* styles/tokens.css */
:root {
  /* ===== 颜色系统 ===== */
  /* 品牌色 */
  --color-primary-50: #e6f7ff;
  --color-primary-100: #bae7ff;
  --color-primary-200: #91d5ff;
  --color-primary-300: #69c0ff;
  --color-primary-400: #40a9ff;
  --color-primary-500: #1890ff;
  --color-primary-600: #096dd9;
  --color-primary-700: #0050b3;
  --color-primary-800: #003a8c;
  --color-primary-900: #002766;

  /* 功能色 */
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-error: #ff4d4f;
  --color-info: #1890ff;

  /* 中性色 */
  --color-gray-50: #fafafa;
  --color-gray-100: #f5f5f5;
  --color-gray-200: #e8e8e8;
  --color-gray-300: #d9d9d9;
  --color-gray-400: #bfbfbf;
  --color-gray-500: #8c8c8c;
  --color-gray-600: #595959;
  --color-gray-700: #434343;
  --color-gray-800: #262626;
  --color-gray-900: #1f1f1f;

  /* 文字颜色 */
  --text-primary: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-tertiary: rgba(0, 0, 0, 0.45);
  --text-disabled: rgba(0, 0, 0, 0.25);
  --text-inverse: #ffffff;

  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #fafafa;
  --bg-tertiary: #f5f5f5;

  /* 边框色 */
  --border-primary: #d9d9d9;
  --border-secondary: #e8e8e8;

  /* ===== 间距系统 ===== */
  --spacing-0: 0;
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  --spacing-16: 64px;

  /* ===== 字体系统 ===== */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
  --font-family-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;

  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* ===== 圆角 ===== */
  --radius-none: 0;
  --radius-sm: 2px;
  --radius-base: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;

  /* ===== 阴影 ===== */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);

  /* ===== 过渡 ===== */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;

  /* ===== 层级 ===== */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}
```

---

## 布局系统

### 1. Flexbox 布局

```scss
// mixins/flex.scss
@mixin flex($direction: row, $justify: flex-start, $align: stretch, $wrap: nowrap) {
  display: flex;
  flex-direction: $direction;
  justify-content: $justify;
  align-items: $align;
  flex-wrap: $wrap;
}

@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

// 使用
.header {
  @include flex-between;
  padding: var(--spacing-4);
}

.card-list {
  @include flex(row, flex-start, stretch, wrap);
  gap: var(--spacing-4);
}
```

### 2. Grid 布局

```scss
// mixins/grid.scss
@mixin grid($columns: 12, $gap: var(--spacing-4)) {
  display: grid;
  grid-template-columns: repeat($columns, 1fr);
  gap: $gap;
}

@mixin grid-auto($min-width: 250px, $gap: var(--spacing-4)) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax($min-width, 1fr));
  gap: $gap;
}

// 使用
.dashboard-grid {
  @include grid(12, var(--spacing-6));

  .widget-large {
    grid-column: span 8;
  }

  .widget-small {
    grid-column: span 4;
  }
}

.card-grid {
  @include grid-auto(300px);
}
```

### 3. 响应式布局

```scss
// mixins/responsive.scss
$breakpoints: (
  'xs': 0,
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px,
  'xxl': 1400px
);

@mixin media-up($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}

@mixin media-down($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (max-width: map-get($breakpoints, $breakpoint) - 1px) {
      @content;
    }
  }
}

@mixin media-between($lower, $upper) {
  @media (min-width: map-get($breakpoints, $lower)) and (max-width: map-get($breakpoints, $upper) - 1px) {
    @content;
  }
}

// 使用
.container {
  width: 100%;
  padding: var(--spacing-4);

  @include media-up('sm') {
    max-width: 540px;
    margin: 0 auto;
  }

  @include media-up('md') {
    max-width: 720px;
  }

  @include media-up('lg') {
    max-width: 960px;
  }

  @include media-up('xl') {
    max-width: 1140px;
  }
}
```

---

## 组件样式规范

### 1. BEM 命名规范

```scss
// Block: 独立的组件
// Element: 组件的组成部分
// Modifier: 组件或元素的变体

// 示例：卡片组件
.card {
  // Block 样式
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);

  // Element: 头部
  &__header {
    padding: var(--spacing-4);
    border-bottom: 1px solid var(--border-secondary);
  }

  // Element: 标题
  &__title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  // Element: 内容
  &__body {
    padding: var(--spacing-4);
  }

  // Element: 底部
  &__footer {
    padding: var(--spacing-4);
    border-top: 1px solid var(--border-secondary);
  }

  // Modifier: 尺寸变体
  &--small {
    .card__header,
    .card__body,
    .card__footer {
      padding: var(--spacing-3);
    }
  }

  &--large {
    .card__header,
    .card__body,
    .card__footer {
      padding: var(--spacing-6);
    }
  }

  // Modifier: 状态变体
  &--hoverable {
    cursor: pointer;
    transition: box-shadow var(--transition-base);

    &:hover {
      box-shadow: var(--shadow-md);
    }
  }

  &--selected {
    border: 2px solid var(--color-primary-500);
  }
}
```

### 2. CSS Modules (Vue)

```vue
<template>
  <div :class="$style.card">
    <div :class="$style.header">
      <h3 :class="$style.title">{{ title }}</h3>
    </div>
    <div :class="$style.body">
      <slot />
    </div>
  </div>
</template>

<style module>
.card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
}

.header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-secondary);
}

.title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.body {
  padding: var(--spacing-4);
}
</style>
```

### 3. Scoped CSS (Vue)

```vue
<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
    </div>
    <div class="card-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
}

.card-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-secondary);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.card-body {
  padding: var(--spacing-4);
}

/* 深度选择器：影响子组件 */
:deep(.child-component) {
  color: var(--text-secondary);
}
</style>
```

---

## 动效实现

### 1. CSS 过渡

```css
/* 基础过渡 */
.btn {
  background: var(--color-primary-500);
  transition: background var(--transition-base), transform var(--transition-fast);
}

.btn:hover {
  background: var(--color-primary-600);
}

.btn:active {
  transform: scale(0.98);
}

/* 多属性过渡 */
.card {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity var(--transition-slow),
    transform var(--transition-slow),
    box-shadow var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-lg);
}

.card.is-hidden {
  opacity: 0;
  transform: translateY(20px);
}
```

### 2. Vue Transition

```vue
<template>
  <!-- 单元素过渡 -->
  <Transition name="fade">
    <div v-if="show" class="modal">...</div>
  </Transition>

  <!-- 列表过渡 -->
  <TransitionGroup name="list" tag="ul">
    <li v-for="item in items" :key="item.id">
      {{ item.text }}
    </li>
  </TransitionGroup>
</template>

<style>
/* 淡入淡出 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-slow);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动 */
.slide-enter-active,
.slide-leave-active {
  transition: transform var(--transition-slow), opacity var(--transition-slow);
}

.slide-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 列表动画 */
.list-enter-active,
.list-leave-active {
  transition: all var(--transition-slow);
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* 列表移动动画 */
.list-move {
  transition: transform var(--transition-slow);
}
</style>
```

### 3. CSS 动画

```css
/* 加载动画 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--color-gray-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.skeleton {
  background: var(--color-gray-200);
  animation: pulse 1.5s ease-in-out infinite;
}

/* 弹跳动画 */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.bounce {
  animation: bounce 0.5s ease-in-out;
}

/* 抖动动画 */
@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

.shake {
  animation: shake 0.5s ease-in-out;
}
```

---

## 主题系统

### 1. 暗色主题

```css
/* 亮色主题（默认） */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #fafafa;
  --text-primary: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --border-primary: #d9d9d9;
}

/* 暗色主题 */
[data-theme='dark'] {
  --bg-primary: #141414;
  --bg-secondary: #1f1f1f;
  --text-primary: rgba(255, 255, 255, 0.85);
  --text-secondary: rgba(255, 255, 255, 0.65);
  --border-primary: #434343;
}

/* 系统主题跟随 */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme='light']) {
    --bg-primary: #141414;
    --bg-secondary: #1f1f1f;
    --text-primary: rgba(255, 255, 255, 0.85);
    --text-secondary: rgba(255, 255, 255, 0.65);
    --border-primary: #434343;
  }
}
```

### 2. 主题切换

```typescript
// composables/useTheme.ts
import { ref, watch, onMounted } from 'vue'

type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const theme = ref<Theme>('system')

  const applyTheme = (newTheme: Theme) => {
    const root = document.documentElement

    if (newTheme === 'system') {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', newTheme)
    }

    localStorage.setItem('theme', newTheme)
  }

  const toggleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'system']
    const currentIndex = themes.indexOf(theme.value)
    theme.value = themes[(currentIndex + 1) % themes.length]
  }

  watch(theme, applyTheme)

  onMounted(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null
    if (savedTheme) {
      theme.value = savedTheme
      applyTheme(savedTheme)
    }
  })

  return {
    theme,
    toggleTheme,
    setTheme: (newTheme: Theme) => {
      theme.value = newTheme
    }
  }
}
```

---

## 无障碍设计

### 1. 焦点样式

```css
/* 自定义焦点样式 */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* 移除默认焦点样式（仅在有自定义样式时） */
:focus:not(:focus-visible) {
  outline: none;
}

/* 按钮焦点样式 */
.btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.2);
}

/* 输入框焦点样式 */
.input:focus-visible {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
```

### 2. 屏幕阅读器

```css
/* 仅对屏幕阅读器可见 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 聚焦时可见 */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### 3. ARIA 属性

```vue
<template>
  <!-- 按钮 -->
  <button
    type="button"
    :aria-pressed="isPressed"
    :aria-disabled="disabled"
    @click="handleClick"
  >
    {{ label }}
  </button>

  <!-- 模态框 -->
  <div
    role="dialog"
    aria-modal="true"
    :aria-labelledby="titleId"
    :aria-describedby="descId"
  >
    <h2 :id="titleId">{{ title }}</h2>
    <p :id="descId">{{ description }}</p>
  </div>

  <!-- 标签页 -->
  <div role="tablist" aria-label="选项卡">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      role="tab"
      :aria-selected="activeTab === tab.id"
      :aria-controls="`panel-${tab.id}`"
      @click="activeTab = tab.id"
    >
      {{ tab.label }}
    </button>
  </div>

  <div
    v-for="tab in tabs"
    :key="tab.id"
    :id="`panel-${tab.id}`"
    role="tabpanel"
    :aria-labelledby="`tab-${tab.id}`"
    :hidden="activeTab !== tab.id"
  >
    {{ tab.content }}
  </div>
</template>
```

---

## 视觉还原检查清单

| 检查项 | 说明 | 优先级 |
|--------|------|--------|
| 颜色准确 | 与设计稿颜色一致 | 高 |
| 间距准确 | 内外边距与设计稿一致 | 高 |
| 字体样式 | 字号、字重、行高一致 | 高 |
| 圆角阴影 | 圆角和阴影效果一致 | 中 |
| 响应式 | 各断点布局正确 | 高 |
| 交互状态 | hover/active/focus 状态 | 中 |
| 动效流畅 | 过渡动画自然 | 中 |
| 无障碍 | 焦点可见、ARIA正确 | 中 |
| 暗色主题 | 暗色模式显示正确 | 低 |
