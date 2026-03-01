# 微信小程序开发实战指南

> 本文档为 client-expert 技能参考手册，涵盖微信小程序从工程搭建到发布上线的完整知识体系。

---

## 1. 技术栈总览

| 技术 | 说明 | 对应 Web 技术 |
|------|------|---------------|
| WXML | 模板语言，支持数据绑定、条件渲染、列表渲染 | HTML |
| WXSS | 样式语言，支持 rpx 响应式单位 | CSS |
| JavaScript | 逻辑层，运行在 JSCore（非浏览器环境，无 DOM/BOM） | JavaScript |
| JSON | 页面/组件/全局配置 | — |
| WXS | 视图层脚本，可在模板中直接调用，性能优于 JS 逻辑层调用 | — |

### 基础库版本策略

```json
// app.json — 建议设置最低基础库版本
{
  "setting": {
    "miniprogramLibVersion": "3.3.0"
  }
}
```

- 生产项目建议最低基础库 >= 3.0.0（覆盖 99%+ 用户）
- 使用 `wx.canIUse('API名')` 做运行时兼容判断
- 在微信公众平台「设置 > 基本设置」中配置最低基础库版本

---

## 2. 项目工程配置

### 2.1 app.json 全局配置

```json
{
  "pages": [
    "pages/index/index",
    "pages/user/user"
  ],
  "subpackages": [
    {
      "root": "pkgOrder",
      "pages": ["list/list", "detail/detail"]
    }
  ],
  "window": {
    "navigationBarTitleText": "我的应用",
    "navigationBarBackgroundColor": "#ffffff",
    "navigationBarTextStyle": "black",
    "backgroundColor": "#f5f5f5",
    "backgroundTextStyle": "dark",
    "enablePullDownRefresh": false
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#1890ff",
    "backgroundColor": "#ffffff",
    "list": [
      { "pagePath": "pages/index/index", "text": "首页", "iconPath": "assets/tab/home.png", "selectedIconPath": "assets/tab/home-active.png" },
      { "pagePath": "pages/user/user", "text": "我的", "iconPath": "assets/tab/user.png", "selectedIconPath": "assets/tab/user-active.png" }
    ]
  },
  "permission": {
    "scope.userLocation": { "desc": "用于获取您的位置信息以提供附近服务" }
  },
  "requiredPrivateInfos": ["getLocation", "chooseAddress"]
}
```
### 2.2 project.config.json

```json
{
  "miniprogramRoot": "miniprogram/",
  "setting": {
    "urlCheck": true,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "preloadBackgroundData": false,
    "minified": true,
    "autoAudits": false,
    "uglifyFileName": true
  },
  "compileType": "miniprogram",
  "appid": "wx1234567890abcdef"
}
```

### 2.3 sitemap.json

```json
{
  "rules": [
    { "action": "allow", "page": "pages/index/index" },
    { "action": "disallow", "page": "*" }
  ]
}
```

> 仅 `allow` 的页面会被微信搜索引擎收录，合理配置有助于小程序 SEO。

---

## 3. 框架选型

| 维度 | 原生开发 | Taro (v3+) | uni-app | mpx |
|------|---------|------------|---------|-----|
| 语法 | WXML + JS | React/Vue | Vue | 增强型小程序语法 |
| 多端支持 | 仅微信 | 微信/支付宝/H5/RN | 微信/支付宝/H5/App | 微信/支付宝/百度/头条 |
| 学习成本 | 低 | 中（需掌握 React/Vue） | 中 | 低 |
| 包体积 | 最小 | 中等（运行时开销） | 中等 | 较小 |
| 生态 | 微信官方 | 京东维护，社区活跃 | DCloud 维护 | 滴滴维护 |
| 适用场景 | 简单项目/极致性能 | 多端需求 + React 团队 | 多端需求 + Vue 团队 | 微信为主 + 渐进增强 |

### 选型建议

- 仅微信端 + 团队熟悉小程序 → 原生开发
- 需要同时发布 H5 + 多端小程序 + React 技术栈 → Taro
- 需要同时发布 H5 + 多端小程序 + Vue 技术栈 → uni-app
- 微信为主 + 少量跨端 + 追求性能 → mpx

---

## 4. 页面与组件体系

### 4.1 Page 生命周期

```javascript
Page({
  data: { list: [], loading: false },

  // 页面创建时触发（仅一次）
  onLoad(options) {
    // options 包含路由参数，如 ?id=123 → options.id === '123'
    this.loadData(options.id)
  },

  // 页面首次渲染完成
  onReady() {},

  // 页面显示（每次从后台切回前台都会触发）
  onShow() {},

  // 页面隐藏
  onHide() {},

  // 页面卸载
  onUnload() {},

  // 下拉刷新（需在 json 中开启 enablePullDownRefresh）
  onPullDownRefresh() {
    this.loadData().finally(() => wx.stopPullDownRefresh())
  },

  // 上拉触底
  onReachBottom() {
    if (!this.data.loading) this.loadNextPage()
  },

  // 页面滚动
  onPageScroll({ scrollTop }) {},

  // 转发分享
  onShareAppMessage() {
    return { title: '分享标题', path: '/pages/index/index' }
  }
})
```
### 4.2 Component 生命周期

```javascript
Component({
  options: {
    multipleSlots: true,
    pureDataPattern: /^_/   // 以 _ 开头的字段为纯数据字段，不参与渲染
  },

  properties: {
    title: { type: String, value: '' },
    count: { type: Number, value: 0, observer: '_onCountChange' }
  },

  data: { _internalFlag: false, expanded: false },

  lifetimes: {
    created() {},    // 组件实例创建（不能调用 setData）
    attached() {},   // 组件进入页面节点树（最常用的初始化时机）
    ready() {},      // 组件布局完成
    detached() {}    // 组件从页面节点树移除
  },

  pageLifetimes: {
    show() {},       // 所在页面显示
    hide() {},       // 所在页面隐藏
    resize(size) {}  // 所在页面尺寸变化
  },

  methods: {
    _onCountChange(newVal, oldVal) {
      // properties observer
    },
    handleTap() {
      this.triggerEvent('itemtap', { id: this.data._internalFlag })
    }
  }
})
```

### 4.3 Behavior 复用

```javascript
// behaviors/pagination.js
module.exports = Behavior({
  data: {
    pageNum: 1,
    pageSize: 20,
    hasMore: true,
    listData: []
  },

  methods: {
    resetPagination() {
      this.setData({ pageNum: 1, hasMore: true, listData: [] })
    },

    appendListData(newItems) {
      this.setData({
        listData: [...this.data.listData, ...newItems],
        hasMore: newItems.length >= this.data.pageSize,
        pageNum: this.data.pageNum + 1
      })
    }
  }
})

// 在 Component 中使用
const paginationBehavior = require('../../behaviors/pagination')

Component({
  behaviors: [paginationBehavior],
  methods: {
    async loadList() {
      const res = await api.getList(this.data.pageNum, this.data.pageSize)
      this.appendListData(res.data.list)
    }
  }
})
```

### 4.4 WXS 脚本

WXS 运行在视图层，适合做数据格式化，避免逻辑层与视图层通信开销。

```xml
<!-- utils.wxs -->
<wxs module="fmt">
  module.exports = {
    formatPrice: function(cents) {
      return (cents / 100).toFixed(2)
    },
    ellipsis: function(str, len) {
      if (!str) return ''
      return str.length > len ? str.substring(0, len) + '...' : str
    }
  }
</wxs>

<!-- 在 WXML 中使用 -->
<wxs src="./utils.wxs" module="fmt" />
<text>{{fmt.formatPrice(item.price)}}</text>
<text>{{fmt.ellipsis(item.title, 20)}}</text>
```

---

## 5. 状态管理

### 5.1 全局 Store 设计

```javascript
// store/index.js — 轻量级全局状态管理
const store = {
  state: {
    userInfo: null,
    token: '',
    cartCount: 0
  },

  _listeners: [],

  setState(partial) {
    const prevState = { ...this.state }
    this.state = { ...this.state, ...partial }
    this._listeners.forEach((fn) => fn(this.state, prevState))
  },

  subscribe(fn) {
    this._listeners.push(fn)
    return () => {
      this._listeners = this._listeners.filter((item) => item !== fn)
    }
  },

  getState() {
    return { ...this.state }
  }
}

module.exports = store
```
### 5.2 页面间通信

| 方式 | 适用场景 | 示例 |
|------|---------|------|
| URL 参数 | 简单值传递 | `navigateTo({ url: '/pages/detail?id=1' })` |
| EventChannel | 页面间双向通信 | `onLoad` 中通过 `this.getOpenerEventChannel()` |
| 全局 Store | 跨页面共享状态 | 见上方 Store 设计 |
| Storage | 持久化数据共享 | `wx.setStorageSync('key', value)` |

```javascript
// EventChannel 示例 — A 页面打开 B 页面并接收回传数据
// A 页面
wx.navigateTo({
  url: '/pages/select-address/index',
  events: {
    onAddressSelected(data) {
      // 接收 B 页面回传的数据
      console.log('选中地址:', data)
    }
  }
})

// B 页面
Page({
  confirmSelect(address) {
    const channel = this.getOpenerEventChannel()
    channel.emit('onAddressSelected', address)
    wx.navigateBack()
  }
})
```

### 5.3 EventBus

```javascript
// utils/event-bus.js
class EventBus {
  constructor() {
    this._events = {}
  }

  on(event, fn) {
    const fns = this._events[event] || []
    this._events = { ...this._events, [event]: [...fns, fn] }
    return () => this.off(event, fn)
  }

  off(event, fn) {
    const fns = (this._events[event] || []).filter((item) => item !== fn)
    this._events = { ...this._events, [event]: fns }
  }

  emit(event, ...args) {
    const fns = this._events[event] || []
    fns.forEach((fn) => fn(...args))
  }

  once(event, fn) {
    const wrapper = (...args) => {
      fn(...args)
      this.off(event, wrapper)
    }
    this.on(event, wrapper)
  }
}

module.exports = new EventBus()
```

---

## 6. 网络请求封装

### 6.1 Promise 封装 + 拦截器

```javascript
// utils/request.js
const store = require('../store/index')

const BASE_URL = 'https://api.example.com'
const TIMEOUT = 15000

// 请求拦截器
function requestInterceptor(config) {
  const token = store.getState().token
  return {
    ...config,
    header: {
      ...config.header,
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  }
}

// 响应拦截器
function responseInterceptor(response) {
  const { statusCode, data } = response

  if (statusCode === 401) {
    store.setState({ token: '', userInfo: null })
    wx.navigateTo({ url: '/pages/login/index' })
    return Promise.reject(new Error('登录已过期，请重新登录'))
  }

  if (statusCode >= 200 && statusCode < 300) {
    if (data.code === 0) return data.data
    return Promise.reject(new Error(data.message || '请求失败'))
  }

  return Promise.reject(new Error(`HTTP ${statusCode}`))
}

function request(options) {
  const config = requestInterceptor({
    url: `${BASE_URL}${options.url}`,
    method: options.method || 'GET',
    data: options.data,
    header: options.header || {},
    timeout: options.timeout || TIMEOUT
  })

  return new Promise((resolve, reject) => {
    wx.request({
      ...config,
      success: (res) => responseInterceptor(res).then(resolve).catch(reject),
      fail: (err) => reject(new Error(err.errMsg || '网络异常'))
    })
  })
}

// 便捷方法
const http = {
  get: (url, data, options = {}) => request({ ...options, url, data, method: 'GET' }),
  post: (url, data, options = {}) => request({ ...options, url, data, method: 'POST' }),
  put: (url, data, options = {}) => request({ ...options, url, data, method: 'PUT' }),
  del: (url, data, options = {}) => request({ ...options, url, data, method: 'DELETE' })
}

module.exports = http
```
### 6.2 请求队列与并发控制

```javascript
// utils/request-queue.js
class RequestQueue {
  constructor(maxConcurrent = 10) {
    this._max = maxConcurrent
    this._running = 0
    this._queue = []
  }

  add(requestFn) {
    return new Promise((resolve, reject) => {
      const task = () => {
        this._running++
        requestFn()
          .then(resolve)
          .catch(reject)
          .finally(() => {
            this._running--
            this._next()
          })
      }

      if (this._running < this._max) {
        task()
      } else {
        this._queue.push(task)
      }
    })
  }

  _next() {
    if (this._queue.length > 0 && this._running < this._max) {
      const task = this._queue.shift()
      task()
    }
  }
}

module.exports = new RequestQueue(10)
```

> 微信小程序同时最多 10 个 `wx.request` 并发连接，超出会排队。封装队列可避免请求丢失。

---

## 7. 数据缓存

### 7.1 缓存工具封装

```javascript
// utils/cache.js
const DEFAULT_EXPIRE = 30 * 60 * 1000 // 默认 30 分钟

const cache = {
  set(key, data, expire = DEFAULT_EXPIRE) {
    const record = {
      data,
      expireAt: expire > 0 ? Date.now() + expire : 0
    }
    try {
      wx.setStorageSync(key, JSON.stringify(record))
    } catch (err) {
      console.error('缓存写入失败:', err)
    }
  },

  get(key) {
    try {
      const raw = wx.getStorageSync(key)
      if (!raw) return null

      const record = JSON.parse(raw)
      if (record.expireAt > 0 && Date.now() > record.expireAt) {
        wx.removeStorageSync(key)
        return null
      }
      return record.data
    } catch (err) {
      return null
    }
  },

  remove(key) {
    wx.removeStorageSync(key)
  },

  clear() {
    wx.clearStorageSync()
  }
}

module.exports = cache
```

### 7.2 缓存策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| Cache First | 优先读缓存，过期再请求 | 配置数据、字典数据 |
| Network First | 优先请求，失败读缓存 | 列表数据、详情数据 |
| Stale While Revalidate | 先返回缓存，后台更新 | 首页数据、用户信息 |

```javascript
// Stale While Revalidate 示例
async function fetchWithSWR(cacheKey, fetchFn, expire) {
  const cached = cache.get(cacheKey)

  // 后台静默更新
  const freshPromise = fetchFn().then((data) => {
    cache.set(cacheKey, data, expire)
    return data
  })

  if (cached) return { data: cached, fresh: freshPromise }
  return { data: await freshPromise, fresh: null }
}
```

---

## 8. 路由与导航

### 8.1 导航方式对比

| API | 页面栈变化 | 适用场景 |
|-----|-----------|---------|
| `wx.navigateTo` | 入栈（最多 10 层） | 普通页面跳转 |
| `wx.redirectTo` | 替换栈顶 | 登录后跳转、中间页 |
| `wx.switchTab` | 清空栈，切换 Tab | Tab 页切换 |
| `wx.reLaunch` | 清空栈，打开新页 | 重新登录、异常恢复 |
| `wx.navigateBack` | 出栈 | 返回上一页 |

### 8.2 路由守卫封装

```javascript
// utils/router.js
const store = require('../store/index')

const AUTH_PAGES = ['/pages/order/list', '/pages/user/profile']

function navigateTo(options) {
  const url = typeof options === 'string' ? options : options.url
  const path = url.split('?')[0]

  // 登录守卫
  if (AUTH_PAGES.includes(path) && !store.getState().token) {
    return wx.navigateTo({
      url: `/pages/login/index?redirect=${encodeURIComponent(url)}`
    })
  }

  return wx.navigateTo(typeof options === 'string' ? { url } : options)
}

function redirectTo(url) {
  return wx.redirectTo({ url })
}

function switchTab(url) {
  return wx.switchTab({ url })
}

function navigateBack(delta = 1) {
  return wx.navigateBack({ delta })
}

module.exports = { navigateTo, redirectTo, switchTab, navigateBack }
```
---

## 9. 常用 API 与能力

### 9.1 登录流程

```
用户端                    小程序服务端                微信服务端
  |--- wx.login() -------->|                           |
  |<-- code ---------------|                           |
  |--- code 发给服务端 ---->|--- code+appid+secret ---->|
  |                         |<-- openid+session_key ----|
  |<-- 自定义 token --------|                           |
```

```javascript
// utils/auth.js
const http = require('./request')
const store = require('../store/index')

async function login() {
  const { code } = await wx.login()
  const { token, userInfo } = await http.post('/auth/wx-login', { code })
  store.setState({ token, userInfo })
  return userInfo
}

// 获取用户手机号（需要 button 组件触发）
async function getPhoneNumber(e) {
  if (e.detail.errMsg !== 'getPhoneNumber:ok') {
    throw new Error('用户拒绝授权手机号')
  }
  const { code } = e.detail
  const { phone } = await http.post('/auth/phone', { code })
  return phone
}

module.exports = { login, getPhoneNumber }
```

```xml
<!-- 手机号授权按钮 -->
<button open-type="getPhoneNumber" bindgetphonenumber="onGetPhone">
  手机号快捷登录
</button>
```

### 9.2 微信支付

```javascript
async function pay(orderId) {
  // 1. 后端创建预支付订单，返回支付参数
  const payParams = await http.post('/pay/create', { orderId })

  // 2. 调起微信支付
  return new Promise((resolve, reject) => {
    wx.requestPayment({
      timeStamp: payParams.timeStamp,
      nonceStr: payParams.nonceStr,
      package: payParams.package,       // 格式: prepay_id=xxx
      signType: payParams.signType,     // RSA 或 MD5
      paySign: payParams.paySign,
      success: () => resolve(true),
      fail: (err) => {
        if (err.errMsg.includes('cancel')) {
          resolve(false) // 用户取消
        } else {
          reject(new Error('支付失败: ' + err.errMsg))
        }
      }
    })
  })
}
```

### 9.3 分享

```javascript
Page({
  // 分享给好友
  onShareAppMessage() {
    return {
      title: '推荐给你一个好物',
      path: `/pages/detail/index?id=${this.data.goodsId}`,
      imageUrl: this.data.shareImage  // 5:4 比例，最小 300x240
    }
  },

  // 分享到朋友圈（基础库 2.11.3+）
  onShareTimeline() {
    return {
      title: '推荐给你一个好物',
      query: `id=${this.data.goodsId}`,
      imageUrl: this.data.shareImage  // 正方形图片
    }
  }
})
```

### 9.4 扫码

```javascript
async function scanCode() {
  try {
    const { result, scanType } = await wx.scanCode({ onlyFromCamera: false })
    return { result, scanType }
  } catch (err) {
    if (err.errMsg.includes('cancel')) return null
    throw new Error('扫码失败')
  }
}
```

### 9.5 地图

```xml
<map
  id="myMap"
  longitude="{{longitude}}"
  latitude="{{latitude}}"
  markers="{{markers}}"
  scale="16"
  show-location
  style="width: 100%; height: 400rpx;"
  bindmarkertap="onMarkerTap"
/>
```

### 9.6 常用能力速查

| 能力 | API | 注意事项 |
|------|-----|---------|
| 相机 | `wx.chooseMedia` | 替代已废弃的 `wx.chooseImage` |
| 文件选择 | `wx.chooseMessageFile` | 从聊天记录选文件 |
| 蓝牙 | `wx.openBluetoothAdapter` | 需先初始化适配器 |
| NFC | `wx.getNFCAdapter` | 仅 Android 支持 |
| 剪贴板 | `wx.setClipboardData` | 会弹出系统提示 |
| 震动 | `wx.vibrateShort` | 轻触反馈 |
| 生物认证 | `wx.startSoterAuthentication` | 指纹/面容 |

---

## 10. 自定义组件开发

### 10.1 组件通信

```
父组件 ──properties──> 子组件
父组件 <──triggerEvent── 子组件
父组件 ──selectComponent──> 子组件（直接调用方法）
```
```javascript
// 子组件 — components/counter/counter.js
Component({
  properties: {
    value: { type: Number, value: 0 }
  },

  methods: {
    increment() {
      this.triggerEvent('change', { value: this.data.value + 1 })
    },
    decrement() {
      if (this.data.value > 0) {
        this.triggerEvent('change', { value: this.data.value - 1 })
      }
    },
    // 供父组件通过 selectComponent 调用
    reset() {
      this.triggerEvent('change', { value: 0 })
    }
  }
})
```

```xml
<!-- 父组件使用 -->
<counter
  id="myCounter"
  value="{{count}}"
  bind:change="onCountChange"
/>
```

```javascript
// 父组件
Page({
  data: { count: 1 },
  onCountChange(e) {
    this.setData({ count: e.detail.value })
  },
  resetCounter() {
    this.selectComponent('#myCounter').reset()
  }
})
```

### 10.2 Slot 插槽

```xml
<!-- components/card/card.wxml -->
<view class="card">
  <view class="card-header">
    <slot name="header"></slot>
  </view>
  <view class="card-body">
    <slot></slot>
  </view>
  <view class="card-footer">
    <slot name="footer"></slot>
  </view>
</view>
```

```javascript
// components/card/card.js
Component({
  options: { multipleSlots: true }
})
```

```xml
<!-- 使用 -->
<card>
  <view slot="header">标题</view>
  <view>正文内容</view>
  <view slot="footer">
    <button size="mini" type="primary">确定</button>
  </view>
</card>
```

### 10.3 外部样式类

```javascript
// components/tag/tag.js
Component({
  externalClasses: ['custom-class', 'text-class']
})
```

```xml
<!-- components/tag/tag.wxml -->
<view class="tag custom-class">
  <text class="tag-text text-class">{{text}}</text>
</view>
```

```xml
<!-- 使用时传入自定义样式 -->
<tag text="热门" custom-class="my-tag" text-class="my-tag-text" />
```

```css
/* 页面样式 */
.my-tag { background: #ff4d4f; border-radius: 8rpx; }
.my-tag-text { color: #fff; font-size: 24rpx; }
```

---

## 11. 性能优化

### 11.1 setData 优化

`setData` 是小程序性能的核心瓶颈，数据从逻辑层序列化后传输到视图层。

```javascript
// 反模式：频繁全量更新
this.setData({ list: this.data.list }) // 整个列表重新序列化

// 优化1：路径更新（只更新变化的部分）
this.setData({ [`list[${index}].checked`]: true })

// 优化2：合并多次 setData
// 反模式
this.setData({ a: 1 })
this.setData({ b: 2 })
this.setData({ c: 3 })
// 正确
this.setData({ a: 1, b: 2, c: 3 })

// 优化3：纯数据字段（不渲染的数据不走 setData 通道）
Component({
  options: { pureDataPattern: /^_/ },
  data: {
    _rawList: [],      // 纯数据，不传输到视图层
    displayList: []    // 渲染数据
  }
})
```

### 11.2 分包加载

```json
// app.json
{
  "pages": ["pages/index/index", "pages/user/user"],
  "subpackages": [
    {
      "root": "pkgOrder",
      "name": "order",
      "pages": ["list/list", "detail/detail"],
      "independent": false
    },
    {
      "root": "pkgActivity",
      "name": "activity",
      "pages": ["index/index"],
      "independent": true
    }
  ],
  "preloadRule": {
    "pages/index/index": {
      "network": "all",
      "packages": ["order"]
    }
  }
}
```

| 类型 | 说明 | 限制 |
|------|------|------|
| 主包 | 包含 tabBar 页面和公共资源 | <= 2MB |
| 普通分包 | 按需加载 | 单个 <= 2MB |
| 独立分包 | 可独立运行，不依赖主包 | 单个 <= 2MB |
| 总体积 | 所有包合计 | <= 20MB |
### 11.3 图片优化

```javascript
// 1. 使用 CDN + WebP 格式
const imageUrl = `${CDN_BASE}/image.jpg?x-oss-process=image/format,webp/resize,w_400`

// 2. 懒加载
// <image lazy-load src="{{item.cover}}" mode="aspectFill" />

// 3. 图片尺寸适配 — 根据屏幕宽度请求合适尺寸
function getOptimizedUrl(url, width) {
  const ratio = wx.getWindowInfo().pixelRatio
  const realWidth = Math.ceil(width * ratio)
  return `${url}?x-oss-process=image/resize,w_${realWidth}/format,webp`
}
```

### 11.4 长列表虚拟化

使用官方 `recycle-view` 组件或自行实现：

```json
// page.json
{
  "usingComponents": {
    "recycle-view": "miniprogram-recycle-view/recycle-view",
    "recycle-item": "miniprogram-recycle-view/recycle-item"
  }
}
```

```xml
<recycle-view
  batch="{{batchSetRecycleData}}"
  id="recycleId"
  height="{{windowHeight}}"
>
  <recycle-item wx:for="{{recycleList}}" wx:key="id">
    <view class="item">{{item.title}}</view>
  </recycle-item>
</recycle-view>
```

### 11.5 预加载策略

```javascript
// 在当前页面预加载下一页数据
Page({
  onReady() {
    // 预加载详情页可能需要的数据
    this._preloadData = null
  },

  onItemTap(e) {
    const id = e.currentTarget.dataset.id
    // 先发起请求，再跳转
    this._preloadData = http.get(`/goods/${id}`)
    wx.navigateTo({ url: `/pages/detail/index?id=${id}` })
  },

  // 供详情页获取预加载数据
  getPreloadData() {
    return this._preloadData
  }
})

// 详情页
Page({
  async onLoad(options) {
    const pages = getCurrentPages()
    const prevPage = pages[pages.length - 2]

    try {
      // 优先使用预加载数据
      const preloaded = prevPage && prevPage.getPreloadData
        ? prevPage.getPreloadData()
        : null
      const data = preloaded ? await preloaded : await http.get(`/goods/${options.id}`)
      this.setData({ detail: data })
    } catch (err) {
      // 预加载失败则正常请求
      const data = await http.get(`/goods/${options.id}`)
      this.setData({ detail: data })
    }
  }
})
```

### 11.6 性能检查清单

| 检查项 | 目标 | 工具 |
|--------|------|------|
| setData 数据量 | 单次 < 256KB | 开发者工具 Audits |
| setData 频率 | 避免 16ms 内多次调用 | Performance 面板 |
| 首屏渲染 | < 1.5s | 体验评分 |
| 包体积 | 主包 < 2MB | 代码依赖分析 |
| 图片大小 | 单张 < 200KB | 网络面板 |
| WXML 节点数 | 页面 < 1000 个 | WXML 面板 |
| 内存占用 | < 256MB | Memory 面板 |

---

## 12. 安全实践

### 12.1 数据传输安全

```javascript
// 1. 所有接口必须使用 HTTPS
// 2. 敏感数据加密传输
const crypto = require('./utils/crypto')

async function submitSensitiveData(data) {
  const encrypted = crypto.aesEncrypt(JSON.stringify(data), AES_KEY)
  return http.post('/api/sensitive', { payload: encrypted })
}
```

### 12.2 接口安全

```javascript
// 服务端校验清单：
// 1. 验证 session_key 有效性
// 2. 校验请求签名（timestamp + nonce + token 签名）
// 3. 接口限流（单用户 QPS 限制）
// 4. 参数校验与 SQL 注入防护
// 5. openid 不可信任前端传递，必须服务端通过 code 换取

// 请求签名示例
function signRequest(params, timestamp, nonce, secret) {
  const sortedKeys = Object.keys(params).sort()
  const str = sortedKeys.map((k) => `${k}=${params[k]}`).join('&')
  const signStr = `${str}&timestamp=${timestamp}&nonce=${nonce}&secret=${secret}`
  return md5(signStr)
}
```

### 12.3 内容安全审核

```javascript
// 文本内容安全检测
async function checkTextSafety(content) {
  try {
    const res = await http.post('/security/msg-check', { content })
    return res.safe
  } catch (err) {
    // 安全接口异常时，建议拦截提交
    return false
  }
}

// 图片内容安全检测
async function checkImageSafety(filePath) {
  const res = await http.upload('/security/img-check', { filePath })
  return res.safe
}

// 使用场景：用户发布内容前必须过审
async function submitPost(content, images) {
  const textSafe = await checkTextSafety(content)
  if (!textSafe) throw new Error('内容包含违规信息，请修改后重试')

  for (const img of images) {
    const imgSafe = await checkImageSafety(img)
    if (!imgSafe) throw new Error('图片包含违规内容，请更换后重试')
  }

  return http.post('/post/create', { content, images })
}
```

---

## 13. 审核与发布

### 13.1 版本管理流程

```
开发版 ──上传──> 体验版 ──提交审核──> 审核版 ──发布──> 正式版
  │                │                    │              │
  │  开发调试用     │  内部测试用         │  微信审核中   │  全量用户
  │  不限数量      │  仅一个             │  仅一个       │  仅一个
```

### 13.2 审核常见驳回原因与规避

| 驳回原因 | 规避方法 |
|---------|---------|
| 功能不完整 | 确保所有页面可正常访问，无空白页 |
| 诱导分享 | 不强制分享后才能使用功能 |
| 虚拟支付 | iOS 端不可使用微信支付购买虚拟商品 |
| 类目不符 | 选择正确的服务类目，提供相关资质 |
| 内容违规 | 接入内容安全审核 API |
| 个人信息收集 | 明确隐私协议，按需获取权限 |
| 登录强制 | 提供游客模式，非必要不强制登录 |

### 13.3 灰度发布

```
正式版 v1.0.0（当前全量）
    │
    ├── 灰度 v1.1.0（5% 用户）
    │     ├── 观察 24h，无异常
    │     ├── 扩大到 20%
    │     ├── 观察 24h，无异常
    │     └── 全量发布
    │
    └── 如有异常 → 回退到 v1.0.0
```

> 在微信公众平台「版本管理」中可设置灰度比例，建议重大更新先灰度 5%-10%。

---

## 14. 小程序与公众号/App 联动

### 14.1 公众号关联

| 场景 | 实现方式 |
|------|---------|
| 公众号文章嵌入小程序 | 文章中插入小程序卡片 |
| 公众号菜单跳转小程序 | 自定义菜单配置小程序路径 |
| 公众号模板消息跳转 | 模板消息中配置 miniprogram 字段 |
| 小程序关注公众号 | `<official-account>` 组件（需关联） |

```xml
<!-- 小程序内引导关注公众号 -->
<official-account></official-account>
```

### 14.2 App 打开小程序

```javascript
// iOS/Android — 微信 OpenSDK
// 通过 App 拉起小程序
WXLaunchMiniProgram.Req req = new WXLaunchMiniProgram.Req();
req.userName = "gh_xxxxxxxxxxxx";  // 小程序原始 ID
req.path = "/pages/detail/index?id=123";
req.miniprogramType = WXLaunchMiniProgram.Req.MINIPTOGRAM_TYPE_RELEASE;
api.sendReq(req);
```

### 14.3 小程序跳转 App

```xml
<!-- 仅从 App 分享到微信打开的小程序场景下可用 -->
<button open-type="launchApp" app-parameter="id=123" binderror="onLaunchAppError">
  打开 App
</button>
```

### 14.4 小程序互跳

```javascript
// 跳转到其他小程序
wx.navigateToMiniProgram({
  appId: 'wx1234567890',
  path: '/pages/index/index?from=myapp',
  envVersion: 'release',
  success() {},
  fail(err) {
    console.error('跳转失败:', err)
  }
})

// 返回来源小程序
wx.navigateBackMiniProgram({
  extraData: { result: 'success' }
})
```

### 14.5 统一用户体系

```
                    ┌─────────────┐
                    │  微信开放平台  │
                    │  (UnionID)   │
                    └──────┬──────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  小程序A  │ │  公众号   │ │   App    │
        │ (OpenID) │ │ (OpenID) │ │ (OpenID) │
        └──────────┘ └──────────┘ └──────────┘
```

- 同一微信开放平台下绑定的小程序、公众号、App 共享 UnionID
- 通过 UnionID 实现跨端用户身份打通
- 服务端以 UnionID 作为用户唯一标识，各端 OpenID 作为渠道标识

---

## 附录：项目目录结构推荐

```
miniprogram/
├── app.js
├── app.json
├── app.wxss
├── assets/                  # 静态资源（图标、Tab 图片）
│   └── tab/
├── behaviors/               # 公共 Behavior
│   └── pagination.js
├── components/              # 全局公共组件
│   ├── card/
│   ├── counter/
│   └── empty-state/
├── pages/                   # 主包页面
│   ├── index/
│   │   ├── index.js
│   │   ├── index.json
│   │   ├── index.wxml
│   │   └── index.wxss
│   └── user/
├── pkgOrder/                # 分包 — 订单模块
│   └── pages/
│       ├── list/
│       └── detail/
├── store/                   # 全局状态管理
│   └── index.js
├── utils/                   # 工具函数
│   ├── request.js
│   ├── cache.js
│   ├── router.js
│   ├── auth.js
│   └── event-bus.js
├── project.config.json
└── sitemap.json
```
