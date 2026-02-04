# 前端组件设计原则

## 核心设计原则

### 1. 单一职责原则 (Single Responsibility)

**定义：** 每个组件只负责一个功能，只有一个改变的理由。

**反例：**
```vue
<!-- 违反SRP：一个组件做了太多事情 -->
<template>
  <div class="user-management">
    <input v-model="searchText" @input="searchUsers" />
    <table>
      <tr v-for="user in users" :key="user.id">
        <td>{{ user.name }}</td>
        <td>
          <button @click="editUser(user)">编辑</button>
          <button @click="deleteUser(user)">删除</button>
        </td>
      </tr>
    </table>
    <!-- 编辑弹窗 -->
    <Modal v-model="showModal">
      <form @submit="saveUser">
        <input v-model="editingUser.name" />
        <input v-model="editingUser.email" />
        <button type="submit">保存</button>
      </form>
    </Modal>
  </div>
</template>
```

**正例：**
```vue
<!-- 遵循SRP：拆分为多个职责单一的组件 -->

<!-- UserSearch.vue - 只负责搜索 -->
<template>
  <input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" placeholder="搜索用户" />
</template>

<!-- UserTable.vue - 只负责展示列表 -->
<template>
  <table>
    <tr v-for="user in users" :key="user.id">
      <td>{{ user.name }}</td>
      <td>
        <slot name="actions" :user="user" />
      </td>
    </tr>
  </table>
</template>

<!-- UserEditModal.vue - 只负责编辑 -->
<template>
  <Modal v-model="visible">
    <UserForm :user="user" @submit="$emit('save', $event)" />
  </Modal>
</template>

<!-- UserManagement.vue - 负责组合和协调 -->
<template>
  <div class="user-management">
    <UserSearch v-model="searchText" />
    <UserTable :users="filteredUsers">
      <template #actions="{ user }">
        <button @click="handleEdit(user)">编辑</button>
        <button @click="handleDelete(user)">删除</button>
      </template>
    </UserTable>
    <UserEditModal v-model="showModal" :user="editingUser" @save="handleSave" />
  </div>
</template>
```

---

### 2. 开闭原则 (Open/Closed)

**定义：** 组件应该对扩展开放，对修改关闭。

**反例：**
```vue
<!-- 违反OCP：添加新按钮类型需要修改组件 -->
<template>
  <button :class="buttonClass">
    <slot />
  </button>
</template>

<script setup>
const props = defineProps<{ type: 'primary' | 'success' | 'warning' }>()

const buttonClass = computed(() => {
  // 添加新类型需要修改这里
  switch (props.type) {
    case 'primary': return 'btn-primary'
    case 'success': return 'btn-success'
    case 'warning': return 'btn-warning'
    default: return 'btn-default'
  }
})
</script>
```

**正例：**
```vue
<!-- 遵循OCP：通过配置扩展 -->
<template>
  <button :class="['btn', `btn-${type}`, customClass]" :style="customStyle">
    <slot />
  </button>
</template>

<script setup>
interface Props {
  type?: string
  customClass?: string
  customStyle?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default'
})
</script>

<style>
/* 通过CSS变量扩展新类型 */
.btn-primary { --btn-bg: var(--color-primary); }
.btn-success { --btn-bg: var(--color-success); }
/* 新类型只需添加CSS，无需修改组件 */
.btn-danger { --btn-bg: var(--color-danger); }
</style>
```

---

### 3. 组合优于继承 (Composition over Inheritance)

**定义：** 使用组合和插槽来扩展组件功能，而不是继承。

**Vue 3 组合式函数：**
```typescript
// composables/useTable.ts
import { ref, computed } from 'vue'

interface UseTableOptions<T> {
  data: Ref<T[]>
  pageSize?: number
}

export function useTable<T>({ data, pageSize = 10 }: UseTableOptions<T>) {
  const currentPage = ref(1)
  const sortField = ref<keyof T | null>(null)
  const sortOrder = ref<'asc' | 'desc'>('asc')

  const sortedData = computed(() => {
    if (!sortField.value) return data.value
    return [...data.value].sort((a, b) => {
      const aVal = a[sortField.value!]
      const bVal = b[sortField.value!]
      const order = sortOrder.value === 'asc' ? 1 : -1
      return aVal > bVal ? order : -order
    })
  })

  const paginatedData = computed(() => {
    const start = (currentPage.value - 1) * pageSize
    return sortedData.value.slice(start, start + pageSize)
  })

  const totalPages = computed(() => Math.ceil(data.value.length / pageSize))

  const setSort = (field: keyof T) => {
    if (sortField.value === field) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortField.value = field
      sortOrder.value = 'asc'
    }
  }

  return {
    currentPage,
    sortField,
    sortOrder,
    paginatedData,
    totalPages,
    setSort
  }
}
```

**React 自定义 Hook：**
```typescript
// hooks/useTable.ts
import { useState, useMemo } from 'react'

interface UseTableOptions<T> {
  data: T[]
  pageSize?: number
}

export function useTable<T>({ data, pageSize = 10 }: UseTableOptions<T>) {
  const [currentPage, setCurrentPage] = useState(1)
  const [sortField, setSortField] = useState<keyof T | null>(null)
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  const sortedData = useMemo(() => {
    if (!sortField) return data
    return [...data].sort((a, b) => {
      const aVal = a[sortField]
      const bVal = b[sortField]
      const order = sortOrder === 'asc' ? 1 : -1
      return aVal > bVal ? order : -order
    })
  }, [data, sortField, sortOrder])

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return sortedData.slice(start, start + pageSize)
  }, [sortedData, currentPage, pageSize])

  const totalPages = Math.ceil(data.length / pageSize)

  const setSort = (field: keyof T) => {
    if (sortField === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('asc')
    }
  }

  return {
    currentPage,
    setCurrentPage,
    sortField,
    sortOrder,
    paginatedData,
    totalPages,
    setSort
  }
}
```

---

### 4. 受控与非受控组件

**受控组件：** 状态由父组件控制

```vue
<!-- 受控组件：值和变化都由父组件控制 -->
<template>
  <input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />
</template>

<script setup>
defineProps<{ modelValue: string }>()
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
```

**非受控组件：** 组件内部管理状态

```vue
<!-- 非受控组件：内部管理状态，通过ref暴露 -->
<template>
  <input ref="inputRef" :defaultValue="defaultValue" />
</template>

<script setup>
const props = defineProps<{ defaultValue?: string }>()
const inputRef = ref<HTMLInputElement>()

defineExpose({
  getValue: () => inputRef.value?.value,
  setValue: (val: string) => { if (inputRef.value) inputRef.value.value = val }
})
</script>
```

**混合模式：** 支持两种使用方式

```vue
<template>
  <input :value="internalValue" @input="handleInput" />
</template>

<script setup>
interface Props {
  modelValue?: string
  defaultValue?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

// 判断是否受控
const isControlled = computed(() => props.modelValue !== undefined)

// 内部状态（非受控时使用）
const localValue = ref(props.defaultValue ?? '')

// 实际使用的值
const internalValue = computed(() =>
  isControlled.value ? props.modelValue : localValue.value
)

const handleInput = (e: Event) => {
  const value = (e.target as HTMLInputElement).value
  if (isControlled.value) {
    emit('update:modelValue', value)
  } else {
    localValue.value = value
  }
}
</script>
```

---

### 5. Props 设计原则

**明确的类型定义：**
```typescript
// 好的Props设计
interface ButtonProps {
  // 必需属性
  label: string

  // 可选属性带默认值
  type?: 'primary' | 'secondary' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean

  // 事件处理
  onClick?: (event: MouseEvent) => void

  // 插槽替代
  icon?: VNode | (() => VNode)
}

// 避免的Props设计
interface BadButtonProps {
  // 过于宽泛的类型
  type: string

  // 布尔属性命名不清
  flag: boolean

  // 对象类型没有具体定义
  options: object

  // any类型
  data: any
}
```

**Props 命名规范：**

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 布尔值 | is/has/can/should 前缀 | `isDisabled`, `hasError`, `canEdit` |
| 事件 | on 前缀 | `onClick`, `onChange`, `onSubmit` |
| 渲染函数 | render 前缀 | `renderItem`, `renderHeader` |
| 数量 | count/num 后缀 | `itemCount`, `maxNum` |

---

### 6. 插槽设计原则

**Vue 插槽设计：**
```vue
<template>
  <div class="card">
    <!-- 默认插槽 -->
    <div class="card-body">
      <slot />
    </div>

    <!-- 具名插槽 -->
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>

    <!-- 作用域插槽 -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" :data="cardData" :actions="cardActions" />
    </div>
  </div>
</template>

<!-- 使用 -->
<Card>
  <template #header>
    <h3>标题</h3>
  </template>

  <p>内容</p>

  <template #footer="{ data, actions }">
    <button @click="actions.save">保存 {{ data.name }}</button>
  </template>
</Card>
```

**React children 和 render props：**
```tsx
interface CardProps {
  children: React.ReactNode
  header?: React.ReactNode
  footer?: (props: { data: CardData; actions: CardActions }) => React.ReactNode
}

const Card: React.FC<CardProps> = ({ children, header, footer }) => {
  const cardData = { name: 'test' }
  const cardActions = { save: () => {} }

  return (
    <div className="card">
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
      {footer && (
        <div className="card-footer">
          {footer({ data: cardData, actions: cardActions })}
        </div>
      )}
    </div>
  )
}

// 使用
<Card
  header={<h3>标题</h3>}
  footer={({ data, actions }) => (
    <button onClick={actions.save}>保存 {data.name}</button>
  )}
>
  <p>内容</p>
</Card>
```

---

## 组件命名规范

### 文件命名

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 组件文件 | PascalCase | `UserProfile.vue`, `UserProfile.tsx` |
| 组合式函数 | camelCase + use前缀 | `useUserData.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 类型定义 | camelCase + .d.ts | `user.d.ts` |
| 样式文件 | kebab-case | `user-profile.scss` |

### 组件命名

```typescript
// Vue 组件
// 文件: UserProfileCard.vue
export default defineComponent({
  name: 'UserProfileCard' // 与文件名一致
})

// React 组件
// 文件: UserProfileCard.tsx
export const UserProfileCard: React.FC<Props> = () => {}
UserProfileCard.displayName = 'UserProfileCard'
```

### 事件命名

```typescript
// Vue 事件命名：kebab-case
defineEmits<{
  'update:modelValue': [value: string]
  'item-click': [item: Item]
  'load-more': []
}>()

// React 事件命名：camelCase + on前缀
interface Props {
  onUpdateValue: (value: string) => void
  onItemClick: (item: Item) => void
  onLoadMore: () => void
}
```

---

## 组件文档规范

每个组件应包含以下文档：

```typescript
/**
 * @component UserCard
 * @description 用户信息卡片组件，展示用户头像、名称和基本信息
 *
 * @example
 * ```vue
 * <UserCard
 *   :user="userData"
 *   :showAvatar="true"
 *   @click="handleClick"
 * />
 * ```
 *
 * @props
 * - user: User - 用户数据对象（必需）
 * - showAvatar: boolean - 是否显示头像（默认: true）
 * - size: 'small' | 'medium' | 'large' - 卡片尺寸（默认: 'medium'）
 *
 * @emits
 * - click: (user: User) => void - 点击卡片时触发
 *
 * @slots
 * - default: 自定义内容区域
 * - actions: 操作按钮区域
 */
```
