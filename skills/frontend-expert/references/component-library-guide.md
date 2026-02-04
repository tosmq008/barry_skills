# 前端组件库选型指南

## 主流组件库对比

### Vue 3 组件库

| 组件库 | 特点 | 适用场景 | 包体积 |
|--------|------|----------|--------|
| Element Plus | 功能全面、文档完善、国内生态好 | 中后台系统 | ~500KB |
| Ant Design Vue | 设计规范、企业级、功能强大 | 企业级应用 | ~600KB |
| Naive UI | TypeScript友好、主题定制强 | 现代化项目 | ~400KB |
| Vuetify 3 | Material Design、响应式 | Material风格项目 | ~450KB |
| PrimeVue | 组件丰富、主题多样 | 需要多主题的项目 | ~350KB |
| Arco Design Vue | 字节出品、设计精美 | 追求设计感的项目 | ~400KB |

### React 组件库

| 组件库 | 特点 | 适用场景 | 包体积 |
|--------|------|----------|--------|
| Ant Design | 企业级、功能全面、生态完善 | 企业级应用 | ~600KB |
| MUI (Material-UI) | Material Design、定制性强 | Material风格项目 | ~500KB |
| Chakra UI | 可访问性好、样式灵活 | 现代化项目 | ~300KB |
| Mantine | 功能丰富、Hooks完善 | 全栈项目 | ~350KB |
| Radix UI | 无样式、可访问性强 | 需要高度定制的项目 | ~100KB |
| shadcn/ui | 复制粘贴、Tailwind集成 | Tailwind项目 | 按需 |

---

## Element Plus 使用指南

### 安装与配置

```bash
npm install element-plus
```

**按需导入配置（推荐）：**
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    })
  ]
})
```

### 主题定制

```scss
// styles/element-variables.scss
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #409eff,
    ),
    'success': (
      'base': #67c23a,
    ),
    'warning': (
      'base': #e6a23c,
    ),
    'danger': (
      'base': #f56c6c,
    ),
  ),
  $font-size: (
    'extra-large': 20px,
    'large': 18px,
    'medium': 16px,
    'base': 14px,
    'small': 13px,
    'extra-small': 12px,
  )
);

// vite.config.ts
css: {
  preprocessorOptions: {
    scss: {
      additionalData: `@use "@/styles/element-variables.scss" as *;`
    }
  }
}
```

### 常用组件封装

**表格组件封装：**
```vue
<!-- components/BaseTable.vue -->
<template>
  <div class="base-table">
    <el-table
      v-loading="loading"
      :data="data"
      :border="border"
      :stripe="stripe"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <el-table-column v-if="selection" type="selection" width="55" />

      <el-table-column
        v-for="col in columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
        :min-width="col.minWidth"
        :sortable="col.sortable"
        :fixed="col.fixed"
      >
        <template #default="scope">
          <slot :name="col.prop" :row="scope.row" :index="scope.$index">
            {{ scope.row[col.prop] }}
          </slot>
        </template>
      </el-table-column>

      <el-table-column v-if="$slots.actions" label="操作" :width="actionsWidth" fixed="right">
        <template #default="scope">
          <slot name="actions" :row="scope.row" :index="scope.$index" />
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="pagination"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="pageSizes"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
interface Column {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  sortable?: boolean | 'custom'
  fixed?: 'left' | 'right'
}

interface Props {
  data: Record<string, any>[]
  columns: Column[]
  loading?: boolean
  border?: boolean
  stripe?: boolean
  selection?: boolean
  pagination?: boolean
  total?: number
  pageSizes?: number[]
  actionsWidth?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  border: true,
  stripe: true,
  selection: false,
  pagination: true,
  total: 0,
  pageSizes: () => [10, 20, 50, 100],
  actionsWidth: 150
})

const emit = defineEmits<{
  'selection-change': [selection: any[]]
  'sort-change': [sort: { prop: string; order: string }]
  'page-change': [page: { current: number; size: number }]
}>()

const currentPage = ref(1)
const pageSize = ref(props.pageSizes[0])

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  emit('sort-change', { prop, order })
}

const handleSizeChange = () => {
  emit('page-change', { current: currentPage.value, size: pageSize.value })
}

const handleCurrentChange = () => {
  emit('page-change', { current: currentPage.value, size: pageSize.value })
}
</script>
```

**表单组件封装：**
```vue
<!-- components/BaseForm.vue -->
<template>
  <el-form
    ref="formRef"
    :model="model"
    :rules="rules"
    :label-width="labelWidth"
    :label-position="labelPosition"
    :inline="inline"
    @submit.prevent="handleSubmit"
  >
    <el-row :gutter="gutter">
      <el-col
        v-for="item in items"
        :key="item.prop"
        :span="item.span || defaultSpan"
      >
        <el-form-item :label="item.label" :prop="item.prop">
          <slot :name="item.prop" :model="model" :item="item">
            <!-- 输入框 -->
            <el-input
              v-if="item.type === 'input'"
              v-model="model[item.prop]"
              :placeholder="item.placeholder"
              :disabled="item.disabled"
              :clearable="item.clearable !== false"
            />

            <!-- 选择器 -->
            <el-select
              v-else-if="item.type === 'select'"
              v-model="model[item.prop]"
              :placeholder="item.placeholder"
              :disabled="item.disabled"
              :clearable="item.clearable !== false"
              :multiple="item.multiple"
            >
              <el-option
                v-for="opt in item.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>

            <!-- 日期选择 -->
            <el-date-picker
              v-else-if="item.type === 'date'"
              v-model="model[item.prop]"
              :type="item.dateType || 'date'"
              :placeholder="item.placeholder"
              :disabled="item.disabled"
            />

            <!-- 开关 -->
            <el-switch
              v-else-if="item.type === 'switch'"
              v-model="model[item.prop]"
              :disabled="item.disabled"
            />
          </slot>
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item v-if="showActions">
      <slot name="actions">
        <el-button type="primary" native-type="submit" :loading="loading">
          {{ submitText }}
        </el-button>
        <el-button @click="handleReset">{{ resetText }}</el-button>
      </slot>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import type { FormInstance, FormRules } from 'element-plus'

interface FormItem {
  prop: string
  label: string
  type: 'input' | 'select' | 'date' | 'switch' | 'custom'
  span?: number
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  multiple?: boolean
  dateType?: 'date' | 'datetime' | 'daterange'
  options?: { label: string; value: any }[]
}

interface Props {
  model: Record<string, any>
  items: FormItem[]
  rules?: FormRules
  labelWidth?: string
  labelPosition?: 'left' | 'right' | 'top'
  inline?: boolean
  gutter?: number
  defaultSpan?: number
  showActions?: boolean
  submitText?: string
  resetText?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: '100px',
  labelPosition: 'right',
  inline: false,
  gutter: 20,
  defaultSpan: 24,
  showActions: true,
  submitText: '提交',
  resetText: '重置',
  loading: false
})

const emit = defineEmits<{
  submit: [model: Record<string, any>]
  reset: []
}>()

const formRef = ref<FormInstance>()

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (valid) {
    emit('submit', props.model)
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  emit('reset')
}

defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate()
})
</script>
```

---

## Ant Design 使用指南

### 安装与配置

```bash
npm install antd @ant-design/icons-vue
```

**按需导入配置：**
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [
        AntDesignVueResolver({
          importStyle: false // 使用CSS-in-JS
        })
      ]
    })
  ]
})
```

### 主题定制

```typescript
// main.ts
import { ConfigProvider } from 'ant-design-vue'

app.use(ConfigProvider, {
  theme: {
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 4,
      fontSize: 14
    },
    components: {
      Button: {
        colorPrimary: '#1890ff'
      }
    }
  }
})
```

---

## Tailwind CSS 集成

### 安装配置

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8'
        }
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem'
      }
    }
  },
  plugins: []
}
```

### 与组件库共存

```scss
// styles/index.scss
@tailwind base;
@tailwind components;
@tailwind utilities;

// 避免与组件库冲突
@layer base {
  button, [type='button'], [type='submit'] {
    @apply bg-transparent;
  }
}

// 自定义组件类
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-primary-500 text-white rounded-md
           hover:bg-primary-600 focus:outline-none focus:ring-2
           focus:ring-primary-500 focus:ring-offset-2
           disabled:opacity-50 disabled:cursor-not-allowed;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }

  .input {
    @apply w-full px-3 py-2 border border-gray-300 rounded-md
           focus:outline-none focus:ring-2 focus:ring-primary-500
           focus:border-transparent;
  }
}
```

---

## 组件库选型决策树

```
开始选型
    │
    ├── 是否需要 Material Design 风格？
    │   ├── 是 → Vue: Vuetify 3 / React: MUI
    │   └── 否 ↓
    │
    ├── 是否是企业级中后台项目？
    │   ├── 是 → Vue: Element Plus / Ant Design Vue
    │   │        React: Ant Design
    │   └── 否 ↓
    │
    ├── 是否需要高度定制化？
    │   ├── 是 → Vue: Naive UI / React: Radix UI + Tailwind
    │   └── 否 ↓
    │
    ├── 是否使用 Tailwind CSS？
    │   ├── 是 → React: shadcn/ui / Vue: 自建组件
    │   └── 否 ↓
    │
    └── 默认推荐
        Vue: Element Plus（国内）/ Naive UI（现代化）
        React: Ant Design（企业级）/ Chakra UI（现代化）
```

---

## 组件库最佳实践

### 1. 二次封装原则

```typescript
// 封装目的：
// 1. 统一API，降低迁移成本
// 2. 添加业务默认值
// 3. 集成业务逻辑

// components/AppButton.vue
<template>
  <el-button
    :type="type"
    :size="size"
    :loading="loading"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </el-button>
</template>

<script setup lang="ts">
// 统一默认值
withDefaults(defineProps<{
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'large' | 'default' | 'small'
  loading?: boolean
  disabled?: boolean
}>(), {
  type: 'default',
  size: 'default',
  loading: false,
  disabled: false
})
</script>
```

### 2. 图标使用规范

```typescript
// 统一图标导入
// icons/index.ts
export {
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'

// 或使用 unplugin-icons
// vite.config.ts
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'

plugins: [
  Icons({ autoInstall: true }),
  Components({
    resolvers: [
      IconsResolver({ prefix: 'icon' })
    ]
  })
]

// 使用
<icon-mdi-account />
<icon-carbon-search />
```

### 3. 表单验证规范

```typescript
// utils/validators.ts
import type { FormItemRule } from 'element-plus'

export const required = (message = '此项为必填项'): FormItemRule => ({
  required: true,
  message,
  trigger: 'blur'
})

export const email: FormItemRule = {
  type: 'email',
  message: '请输入有效的邮箱地址',
  trigger: 'blur'
}

export const phone: FormItemRule = {
  pattern: /^1[3-9]\d{9}$/,
  message: '请输入有效的手机号码',
  trigger: 'blur'
}

export const minLength = (min: number): FormItemRule => ({
  min,
  message: `最少输入${min}个字符`,
  trigger: 'blur'
})

export const maxLength = (max: number): FormItemRule => ({
  max,
  message: `最多输入${max}个字符`,
  trigger: 'blur'
})

// 使用
const rules = {
  username: [required(), minLength(3), maxLength(20)],
  email: [required(), email],
  phone: [required(), phone]
}
```
