# 04 功能模块划分

## 模块清单

### 1. 显示模块 (Display Module)

**职责：** 展示当前计数值

**实现：**
- HTML: `<div id="counter">0</div>`
- CSS: 大字体、居中显示
- JS: 更新 innerHTML

### 2. 控制模块 (Control Module)

**职责：** 提供用户交互按钮

**实现：**
- 减少按钮: `<button id="decrement">-</button>`
- 增加按钮: `<button id="increment">+</button>`

### 3. 逻辑模块 (Logic Module)

**职责：** 处理计数逻辑

**实现：**
```javascript
let count = 0;

function increment() {
    count++;
    updateDisplay();
}

function decrement() {
    count--;
    updateDisplay();
}

function updateDisplay() {
    document.getElementById('counter').textContent = count;
}
```

## 模块依赖关系

```
控制模块 → 逻辑模块 → 显示模块
(用户点击)  (计算)     (更新UI)
```
