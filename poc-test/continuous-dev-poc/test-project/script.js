// 计数器应用逻辑

let count = 0;

// 获取 DOM 元素
const counterDisplay = document.getElementById('counter');
const incrementBtn = document.getElementById('increment');
const decrementBtn = document.getElementById('decrement');

// 更新显示
function updateDisplay() {
    counterDisplay.textContent = count;
}

// 增加计数
function increment() {
    count++;
    updateDisplay();
}

// 减少计数
function decrement() {
    count--;
    updateDisplay();
}

// 绑定事件
incrementBtn.addEventListener('click', increment);
decrementBtn.addEventListener('click', decrement);
