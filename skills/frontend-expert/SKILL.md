---
name: frontend-expert
description: "前端技术专家，以资深工程师视角进行开发任务。从需求理解、模型设计、组件复用、可维护性、视觉还原、架构分层等维度全面考量。精通Vue、React现代前端工程化，熟练运用主流组件库，确保代码质量和用户体验。适用于前端项目的架构设计、组件开发、性能优化和代码审查。"
license: MIT
compatibility: "适用于现代前端项目。支持Vue 3、React 18+、TypeScript 5+。兼容主流UI库如Ant Design、Element Plus、Tailwind CSS等。"
metadata:
  category: development
  phase: implementation
  version: "1.0.0"
  author: frontend-expert
allowed-tools: bash read_file write_file grep glob
---

# Frontend Expert Skill

作为前端技术专家，以资深工程师的视角进行开发任务，从需求理解到代码实现，全面考虑复用性、可维护性、视觉还原和用户体验。

## When to Use

**适用场景：**
- 前端项目架构设计与实现
- 复杂交互组件的开发
- 响应式布局与视觉还原
- 状态管理方案设计
- 前端性能优化
- 组件库选型与封装
- 代码重构与优化
- 代码审查与质量把控

**不适用：**
- 简单的静态页面（无架构需求）
- 纯后端项目
- 原生移动端开发（非Web技术栈）

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端技术专家工作流程                            │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: 需求分析          Phase 2: 技术选型                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 需求理解与澄清  │  ──▶  │ 框架/库选型     │                  │
│  │ 交互流程梳理    │       │ 组件库评估      │                  │
│  │ 视觉规范分析    │       │ 技术栈确定      │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 3: 架构设计          Phase 4: 组件开发                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 目录结构设计    │  ──▶  │ 基础组件封装    │                  │
│  │ 状态管理设计    │       │ 业务组件实现    │                  │
│  │ 路由规划        │       │ 页面组装        │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 5: 视觉还原          Phase 6: 质量保障                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 样式系统实现    │  ──▶  │ 单元测试编写    │                  │
│  │ 响应式适配      │       │ 性能优化        │                  │
│  │ 动效实现        │       │ 代码审查        │                  │
│  └─────────────────┘       └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 需求分析 (Requirement Analysis)

### 1.1 需求理解与澄清

**必须明确的内容：**

| 维度 | 关键问题 | 输出 |
|------|----------|------|
| 功能需求 | 页面需要实现什么功能？ | 功能清单 |
| 交互需求 | 用户如何与页面交互？ | 交互流程图 |
| 视觉需求 | 设计稿规范是什么？ | 设计规范文档 |
| 数据需求 | 数据从哪来？格式是什么？ | API接口文档 |

### 1.2 交互流程梳理

**必须考虑的交互场景：**
- 正常操作流程
- 异常状态处理（加载中、空数据、错误）
- 边界情况（网络异常、权限不足）
- 用户反馈（成功提示、错误提示）

### 1.3 视觉规范分析

| 维度 | 内容 | 考量点 |
|------|------|--------|
| 设计系统 | 颜色、字体、间距 | 是否有现成设计系统 |
| 响应式 | 断点、布局变化 | 支持哪些设备 |
| 动效 | 过渡、动画 | 性能影响 |
| 无障碍 | ARIA、键盘导航 | 可访问性要求 |

---

## Phase 2: 技术选型 (Technology Selection)

> ⚠️ **执行前必须读取 `references/component-library-guide.md` 获取组件库选型指南**

### 2.1 框架选型

**Vue vs React 选择依据：**

| 维度 | Vue 3 | React 18+ |
|------|-------|-----------|
| 团队熟悉度 | 国内团队更熟悉 | 国际化团队更熟悉 |
| 生态系统 | Element Plus、Ant Design Vue | Ant Design、MUI |
| 学习曲线 | 相对平缓 | 需要理解更多概念 |
| 类型支持 | 原生支持 | 需要额外配置 |
| 状态管理 | Pinia | Redux/Zustand |

### 2.2 组件库评估

**评估维度：**

| 维度 | 评估要点 |
|------|----------|
| 功能完整性 | 是否覆盖所需组件 |
| 定制能力 | 主题定制、样式覆盖 |
| 文档质量 | API文档、示例代码 |
| 社区活跃度 | Issue响应、更新频率 |
| 包体积 | Tree-shaking支持 |
| TypeScript | 类型定义完整性 |

### 2.3 技术栈确定

**推荐技术栈组合：**

**Vue 3 技术栈：**
```
Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus/Ant Design Vue
```

**React 技术栈：**
```
React 18 + TypeScript + Vite + Zustand/Redux Toolkit + React Router + Ant Design/MUI
```

---

## Phase 3: 架构设计 (Architecture Design)

> ⚠️ **执行前必须读取 `references/architecture-patterns.md` 获取架构模式指南**

### 3.1 目录结构设计

**Vue 3 项目结构：**
```
src/
├── api/                    # API请求
│   ├── index.ts           # API实例配置
│   ├── user.ts            # 用户相关API
│   └── types.ts           # API类型定义
├── assets/                 # 静态资源
│   ├── images/
│   └── styles/
│       ├── variables.scss # 变量定义
│       └── mixins.scss    # 混入
├── components/            # 通用组件
│   ├── base/              # 基础组件
│   │   ├── BaseButton/
│   │   └── BaseInput/
│   └── business/          # 业务组件
│       └── UserCard/
├── composables/           # 组合式函数
│   ├── useRequest.ts
│   └── useTable.ts
├── layouts/               # 布局组件
│   ├── DefaultLayout.vue
│   └── BlankLayout.vue
├── pages/                 # 页面组件
│   ├── home/
│   └── user/
├── router/                # 路由配置
│   ├── index.ts
│   └── routes.ts
├── stores/                # 状态管理
│   ├── index.ts
│   └── user.ts
├── types/                 # 类型定义
│   ├── global.d.ts
│   └── api.d.ts
├── utils/                 # 工具函数
│   ├── format.ts
│   └── validate.ts
├── App.vue
└── main.ts
```

**React 项目结构：**
```
src/
├── api/                    # API请求
├── assets/                 # 静态资源
├── components/            # 通用组件
│   ├── base/              # 基础组件
│   └── business/          # 业务组件
├── hooks/                 # 自定义Hooks
│   ├── useRequest.ts
│   └── useTable.ts
├── layouts/               # 布局组件
├── pages/                 # 页面组件
├── router/                # 路由配置
├── stores/                # 状态管理
├── types/                 # 类型定义
├── utils/                 # 工具函数
├── App.tsx
└── main.tsx
```

### 3.2 状态管理设计

> ⚠️ **执行前必须读取 `references/state-management.md` 获取状态管理指南**

**状态分类：**

| 状态类型 | 存储位置 | 示例 |
|----------|----------|------|
| 服务端状态 | React Query/SWR | API数据 |
| 全局UI状态 | Pinia/Zustand | 主题、语言 |
| 局部UI状态 | 组件内部 | 表单、弹窗 |
| URL状态 | 路由参数 | 分页、筛选 |

### 3.3 路由规划

**路由设计原则：**
- 语义化路径命名
- 合理的嵌套层级
- 路由懒加载
- 权限控制集成

---

## Phase 4: 组件开发 (Component Development)

> ⚠️ **执行前必须读取 `references/design-principles.md` 获取组件设计原则**

### 4.1 组件设计原则

**单一职责：**
- 每个组件只做一件事
- 复杂组件拆分为多个子组件
- 逻辑与视图分离

**可复用性：**
- Props设计合理，支持定制
- 提供插槽/children扩展
- 避免硬编码

**可维护性：**
- 清晰的命名规范
- 完整的类型定义
- 必要的注释说明

### 4.2 组件分层

```
┌─────────────────────────────────────────────────────────────┐
│                      页面组件 (Pages)                         │
│  职责: 页面布局、数据获取、业务逻辑编排                          │
├─────────────────────────────────────────────────────────────┤
│                    业务组件 (Business)                        │
│  职责: 特定业务场景、组合基础组件、业务逻辑封装                   │
├─────────────────────────────────────────────────────────────┤
│                    基础组件 (Base)                            │
│  职责: 通用UI组件、无业务逻辑、高度可复用                        │
├─────────────────────────────────────────────────────────────┤
│                    UI库组件 (UI Library)                      │
│  职责: 第三方组件库、原子级组件                                 │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Vue 3 组件示例

```vue
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { PropType } from 'vue'

// Props定义
interface Props {
  modelValue: string
  placeholder?: string
  disabled?: boolean
  maxLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入',
  disabled: false,
  maxLength: 100
})

// Emits定义
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [value: string]
  'blur': [event: FocusEvent]
}>()

// 内部状态
const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)

// 计算属性
const charCount = computed(() => props.modelValue.length)
const isOverLimit = computed(() => charCount.value > props.maxLength)

// 方法
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
  emit('change', props.modelValue)
}

// 暴露方法
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur()
})
</script>

<template>
  <div class="base-input" :class="{ 'is-disabled': disabled, 'is-focused': isFocused }">
    <input
      ref="inputRef"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxLength"
      @input="handleInput"
      @focus="isFocused = true"
      @blur="handleBlur"
    />
    <span v-if="maxLength" class="char-count" :class="{ 'is-over': isOverLimit }">
      {{ charCount }}/{{ maxLength }}
    </span>
  </div>
</template>
```

### 4.4 React 组件示例

```tsx
import { forwardRef, useImperativeHandle, useRef, useState, useCallback } from 'react'

interface BaseInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  maxLength?: number
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
}

export interface BaseInputRef {
  focus: () => void
  blur: () => void
}

export const BaseInput = forwardRef<BaseInputRef, BaseInputProps>(
  ({ value, onChange, placeholder = '请输入', disabled = false, maxLength = 100, onBlur }, ref) => {
    const inputRef = useRef<HTMLInputElement>(null)
    const [isFocused, setIsFocused] = useState(false)

    // 暴露方法
    useImperativeHandle(ref, () => ({
      focus: () => inputRef.current?.focus(),
      blur: () => inputRef.current?.blur()
    }))

    const charCount = value.length
    const isOverLimit = charCount > maxLength

    const handleChange = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        onChange(e.target.value)
      },
      [onChange]
    )

    const handleBlur = useCallback(
      (e: React.FocusEvent<HTMLInputElement>) => {
        setIsFocused(false)
        onBlur?.(e)
      },
      [onBlur]
    )

    return (
      <div className={`base-input ${disabled ? 'is-disabled' : ''} ${isFocused ? 'is-focused' : ''}`}>
        <input
          ref={inputRef}
          value={value}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={maxLength}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={handleBlur}
        />
        {maxLength && (
          <span className={`char-count ${isOverLimit ? 'is-over' : ''}`}>
            {charCount}/{maxLength}
          </span>
        )}
      </div>
    )
  }
)

BaseInput.displayName = 'BaseInput'
```

---

## Phase 5: 视觉还原 (Visual Implementation)

> ⚠️ **执行前必须读取 `references/visual-implementation.md` 获取视觉还原指南**

### 5.1 样式系统设计

**CSS变量定义：**
```css
:root {
  /* 颜色系统 */
  --color-primary: #1890ff;
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-error: #ff4d4f;

  /* 文字颜色 */
  --text-primary: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-disabled: rgba(0, 0, 0, 0.25);

  /* 间距系统 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* 圆角 */
  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 8px;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* 字体 */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
}
```

### 5.2 响应式设计

**断点定义：**
```scss
// 断点变量
$breakpoints: (
  'xs': 480px,   // 手机
  'sm': 576px,   // 手机横屏
  'md': 768px,   // 平板
  'lg': 992px,   // 小桌面
  'xl': 1200px,  // 桌面
  'xxl': 1600px  // 大桌面
);

// 响应式混入
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}

// 使用示例
.container {
  padding: var(--spacing-sm);

  @include respond-to('md') {
    padding: var(--spacing-md);
  }

  @include respond-to('lg') {
    padding: var(--spacing-lg);
  }
}
```

### 5.3 动效实现

**过渡动画：**
```css
/* 基础过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动过渡 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
```

---

## Phase 6: 质量保障 (Quality Assurance)

> ⚠️ **执行前必须读取 `references/performance-optimization.md` 获取性能优化指南**

### 6.1 单元测试

**Vue 组件测试：**
```typescript
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import BaseInput from './BaseInput.vue'

describe('BaseInput', () => {
  it('renders correctly', () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: 'test' }
    })
    expect(wrapper.find('input').element.value).toBe('test')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: '' }
    })
    await wrapper.find('input').setValue('new value')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['new value'])
  })

  it('shows character count when maxLength is set', () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: 'test', maxLength: 10 }
    })
    expect(wrapper.find('.char-count').text()).toBe('4/10')
  })
})
```

### 6.2 性能优化清单

| 优化项 | 方法 | 工具 |
|--------|------|------|
| 代码分割 | 路由懒加载、动态导入 | Vite/Webpack |
| 图片优化 | 压缩、懒加载、WebP | vite-plugin-imagemin |
| 缓存策略 | Service Worker、HTTP缓存 | Workbox |
| 渲染优化 | 虚拟列表、防抖节流 | vue-virtual-scroller |
| 包体积 | Tree-shaking、按需导入 | rollup-plugin-visualizer |

### 6.3 代码审查要点

| 类别 | 检查项 |
|------|--------|
| 正确性 | 逻辑是否正确？边界条件是否处理？ |
| 性能 | 是否有不必要的重渲染？是否需要缓存？ |
| 可读性 | 命名是否清晰？组件是否过于复杂？ |
| 可维护性 | 是否遵循组件设计原则？是否易于测试？ |
| 安全性 | 是否有XSS风险？敏感数据是否保护？ |
| 无障碍 | 是否支持键盘导航？ARIA属性是否正确？ |

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 技术设计文档 | `docs/technical-design.md` | 架构和设计决策 |
| 组件文档 | `docs/components.md` | 组件API和使用示例 |
| 代码审查报告 | `docs/code-review.md` | 审查结果和建议 |
| 性能测试报告 | `docs/performance-report.md` | 性能指标和优化 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/design-principles.md` | 组件设计原则 |
| `references/architecture-patterns.md` | 前端架构模式 |
| `references/component-library-guide.md` | 组件库选型指南 |
| `references/state-management.md` | 状态管理指南 |
| `references/visual-implementation.md` | 视觉还原指南 |
| `references/performance-optimization.md` | 性能优化指南 |
| `references/api-integration.md` | 前后端API交互指南 |

---

## Related Skills

- `test-expert` - 测试专家（前端测试）
- `tech-plan-template` - 技术方案模板
- `development-workflow` - 开发工作流
- `python-expert` - Python专家（后端配合）
