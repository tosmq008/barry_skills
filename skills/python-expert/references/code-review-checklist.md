# Python 代码审查清单

## 审查流程

```
┌─────────────────────────────────────────────────────────────┐
│                      代码审查流程                             │
├─────────────────────────────────────────────────────────────┤
│  Step 1: 功能正确性     Step 2: 代码质量                      │
│  ┌─────────────────┐   ┌─────────────────┐                  │
│  │ 逻辑是否正确    │ → │ 可读性检查      │                  │
│  │ 边界条件处理    │   │ 命名规范        │                  │
│  │ 异常处理        │   │ 代码结构        │                  │
│  └─────────────────┘   └─────────────────┘                  │
│           │                     │                           │
│           ▼                     ▼                           │
│  Step 3: 安全性         Step 4: 性能                         │
│  ┌─────────────────┐   ┌─────────────────┐                  │
│  │ 输入验证        │ → │ 算法复杂度      │                  │
│  │ 敏感数据处理    │   │ 资源使用        │                  │
│  │ 权限检查        │   │ 并发安全        │                  │
│  └─────────────────┘   └─────────────────┘                  │
│           │                     │                           │
│           ▼                     ▼                           │
│  Step 5: 可维护性       Step 6: 测试覆盖                      │
│  ┌─────────────────┐   ┌─────────────────┐                  │
│  │ SOLID原则       │ → │ 单元测试        │                  │
│  │ 设计模式        │   │ 边界测试        │                  │
│  │ 文档完整性      │   │ 异常测试        │                  │
│  └─────────────────┘   └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 功能正确性

### 1.1 逻辑正确性

| 检查项 | 说明 | 示例 |
|--------|------|------|
| 算法正确 | 实现是否符合需求 | 排序算法是否正确排序 |
| 条件判断 | if/else 逻辑是否正确 | 边界值判断 |
| 循环逻辑 | 循环条件和终止条件 | 是否有死循环风险 |
| 返回值 | 返回值是否符合预期 | 是否返回正确类型 |

```python
# 检查点：条件判断是否完整
# 差：遗漏了等于的情况
def compare(a, b):
    if a > b:
        return 1
    elif a < b:
        return -1
    # 缺少 a == b 的情况

# 好：覆盖所有情况
def compare(a, b):
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0
```

### 1.2 边界条件

| 检查项 | 说明 |
|--------|------|
| 空值处理 | None、空字符串、空列表 |
| 边界值 | 最大值、最小值、零 |
| 类型检查 | 输入类型是否正确 |
| 长度限制 | 字符串长度、列表大小 |

```python
# 检查点：空值和边界处理
def get_average(numbers: list[float]) -> float:
    # 检查空列表
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")

    # 检查类型
    if not all(isinstance(n, (int, float)) for n in numbers):
        raise TypeError("All elements must be numbers")

    return sum(numbers) / len(numbers)
```

### 1.3 异常处理

| 检查项 | 说明 |
|--------|------|
| 异常捕获 | 是否捕获了可能的异常 |
| 异常类型 | 是否捕获了正确的异常类型 |
| 异常信息 | 异常信息是否有意义 |
| 资源清理 | 异常时是否正确清理资源 |

```python
# 检查点：异常处理是否完善
# 差：捕获所有异常，隐藏问题
try:
    result = process_data(data)
except:
    pass

# 好：捕获特定异常，记录日志
try:
    result = process_data(data)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    raise
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise ServiceError("Failed to process data") from e
```

---

## 2. 代码质量

### 2.1 可读性

| 检查项 | 标准 |
|--------|------|
| 函数长度 | 单个函数不超过 50 行 |
| 嵌套深度 | 不超过 3 层嵌套 |
| 行长度 | 不超过 120 字符 |
| 复杂度 | 圈复杂度不超过 10 |

```python
# 检查点：减少嵌套深度
# 差：深层嵌套
def process(data):
    if data:
        if data.is_valid:
            if data.has_permission:
                if data.is_active:
                    return do_something(data)
    return None

# 好：提前返回
def process(data):
    if not data:
        return None
    if not data.is_valid:
        return None
    if not data.has_permission:
        return None
    if not data.is_active:
        return None
    return do_something(data)
```

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | snake_case | `user_name`, `total_count` |
| 函数 | snake_case | `get_user()`, `calculate_total()` |
| 类 | PascalCase | `UserService`, `OrderRepository` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 私有 | 前缀下划线 | `_internal_method()`, `_cache` |

```python
# 检查点：命名是否清晰表达意图
# 差：含糊的命名
def process(d):
    r = []
    for i in d:
        if i.x > 0:
            r.append(i)
    return r

# 好：清晰的命名
def filter_positive_items(items: list[Item]) -> list[Item]:
    positive_items = []
    for item in items:
        if item.value > 0:
            positive_items.append(item)
    return positive_items

# 更好：使用列表推导式
def filter_positive_items(items: list[Item]) -> list[Item]:
    return [item for item in items if item.value > 0]
```

### 2.3 代码结构

| 检查项 | 说明 |
|--------|------|
| 单一职责 | 每个函数/类只做一件事 |
| DRY原则 | 不要重复代码 |
| 模块化 | 相关功能组织在一起 |
| 导入顺序 | 标准库 → 第三方 → 本地 |

```python
# 检查点：导入顺序
# 好：按规范排序
import os
import sys
from typing import List, Optional

import requests
from sqlalchemy import Column, String

from app.models import User
from app.services import UserService
```

---

## 3. 安全性

### 3.1 输入验证

| 检查项 | 风险 | 防护 |
|--------|------|------|
| SQL注入 | 数据库被攻击 | 使用参数化查询 |
| XSS | 脚本注入 | 转义输出 |
| 命令注入 | 系统被控制 | 避免shell=True |
| 路径遍历 | 文件泄露 | 验证路径 |

```python
# 检查点：SQL注入防护
# 差：字符串拼接
def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return db.execute(query)

# 好：参数化查询
def get_user(user_id: str):
    query = "SELECT * FROM users WHERE id = :user_id"
    return db.execute(query, {"user_id": user_id})

# 检查点：命令注入防护
# 差：使用 shell=True
import subprocess
def run_command(filename: str):
    subprocess.run(f"cat {filename}", shell=True)

# 好：使用列表参数
def run_command(filename: str):
    subprocess.run(["cat", filename], shell=False)
```

### 3.2 敏感数据处理

| 检查项 | 说明 |
|--------|------|
| 密码存储 | 使用安全哈希（bcrypt/argon2） |
| 密钥管理 | 不硬编码，使用环境变量 |
| 日志脱敏 | 不记录敏感信息 |
| 传输加密 | 使用HTTPS |

```python
# 检查点：密码处理
# 差：明文存储
user.password = request.password

# 好：使用安全哈希
from passlib.hash import bcrypt

user.password_hash = bcrypt.hash(request.password)

# 检查点：日志脱敏
# 差：记录敏感信息
logger.info(f"User login: {username}, password: {password}")

# 好：脱敏处理
logger.info(f"User login: {username}")
```

### 3.3 权限检查

```python
# 检查点：权限验证
def delete_user(current_user: User, user_id: str):
    # 检查权限
    if not current_user.is_admin:
        raise PermissionError("Only admin can delete users")

    # 检查不能删除自己
    if current_user.id == user_id:
        raise ValueError("Cannot delete yourself")

    return user_repository.delete(user_id)
```

---

## 4. 性能

### 4.1 算法复杂度

| 检查项 | 说明 |
|--------|------|
| 时间复杂度 | 是否有更优算法 |
| 空间复杂度 | 内存使用是否合理 |
| 数据结构 | 是否选择了合适的数据结构 |

```python
# 检查点：算法复杂度
# 差：O(n²) 查找
def find_duplicates(items: list) -> list:
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other and item not in duplicates:
                duplicates.append(item)
    return duplicates

# 好：O(n) 使用集合
def find_duplicates(items: list) -> list:
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

### 4.2 资源使用

| 检查项 | 说明 |
|--------|------|
| 内存泄漏 | 是否正确释放资源 |
| 连接池 | 是否复用连接 |
| 缓存 | 是否合理使用缓存 |
| 批量操作 | 是否避免N+1查询 |

```python
# 检查点：资源释放
# 差：可能泄漏
def read_file(path: str) -> str:
    f = open(path)
    return f.read()  # 文件未关闭

# 好：使用上下文管理器
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()
```

### 4.3 并发安全

| 检查项 | 说明 |
|--------|------|
| 线程安全 | 共享数据是否加锁 |
| 死锁风险 | 锁的获取顺序是否一致 |
| 竞态条件 | 是否有检查-使用竞态 |

```python
# 检查点：线程安全
# 差：非线程安全
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1  # 非原子操作

# 好：线程安全
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.count += 1
```

---

## 5. 可维护性

### 5.1 SOLID原则检查

| 原则 | 检查点 |
|------|--------|
| 单一职责 | 类/函数是否只有一个变化原因 |
| 开闭原则 | 是否对扩展开放，对修改关闭 |
| 里氏替换 | 子类是否可以替换父类 |
| 接口隔离 | 接口是否足够小 |
| 依赖倒置 | 是否依赖抽象而非具体 |

```python
# 检查点：依赖倒置
# 差：依赖具体实现
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # 直接依赖具体类

# 好：依赖抽象
class UserService:
    def __init__(self, db: Database):  # 依赖接口
        self.db = db
```

### 5.2 文档完整性

| 检查项 | 说明 |
|--------|------|
| 模块文档 | 模块顶部有说明 |
| 类文档 | 类有docstring |
| 函数文档 | 公共函数有docstring |
| 类型注解 | 参数和返回值有类型注解 |

```python
# 检查点：文档完整性
def calculate_discount(
    price: float,
    discount_rate: float,
    min_price: float = 0.0
) -> float:
    """
    计算折扣后的价格。

    Args:
        price: 原始价格
        discount_rate: 折扣率 (0.0 - 1.0)
        min_price: 最低价格限制

    Returns:
        折扣后的价格，不低于 min_price

    Raises:
        ValueError: 如果 price 为负数或 discount_rate 不在有效范围内

    Example:
        >>> calculate_discount(100, 0.2)
        80.0
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1")

    discounted = price * (1 - discount_rate)
    return max(discounted, min_price)
```

---

## 6. 测试覆盖

### 6.1 测试检查清单

| 检查项 | 说明 |
|--------|------|
| 正常路径 | 主要功能是否测试 |
| 边界条件 | 边界值是否测试 |
| 异常路径 | 异常情况是否测试 |
| 覆盖率 | 代码覆盖率是否达标 |

```python
# 检查点：测试覆盖
class TestCalculateDiscount:
    """折扣计算测试"""

    def test_normal_discount(self):
        """测试正常折扣"""
        assert calculate_discount(100, 0.2) == 80.0

    def test_zero_discount(self):
        """测试零折扣"""
        assert calculate_discount(100, 0) == 100.0

    def test_full_discount(self):
        """测试全额折扣"""
        assert calculate_discount(100, 1.0) == 0.0

    def test_min_price_limit(self):
        """测试最低价格限制"""
        assert calculate_discount(100, 0.9, min_price=20) == 20.0

    def test_negative_price_raises(self):
        """测试负价格抛出异常"""
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_discount(-100, 0.2)

    def test_invalid_discount_rate_raises(self):
        """测试无效折扣率抛出异常"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            calculate_discount(100, 1.5)
```

---

## 审查报告模板

```markdown
# 代码审查报告

## 基本信息
- **审查日期**: YYYY-MM-DD
- **审查人**: [审查人姓名]
- **代码作者**: [作者姓名]
- **PR/MR链接**: [链接]

## 审查结果
- [ ] 通过
- [ ] 需要修改后通过
- [ ] 不通过

## 问题清单

### 严重问题 (必须修复)
| # | 文件 | 行号 | 问题描述 | 建议 |
|---|------|------|----------|------|
| 1 | | | | |

### 一般问题 (建议修复)
| # | 文件 | 行号 | 问题描述 | 建议 |
|---|------|------|----------|------|
| 1 | | | | |

### 建议优化 (可选)
| # | 文件 | 行号 | 问题描述 | 建议 |
|---|------|------|----------|------|
| 1 | | | | |

## 总体评价
[对代码质量的总体评价和建议]
```

---

## 快速检查清单

### 提交前自查

- [ ] 代码能正常运行
- [ ] 所有测试通过
- [ ] 没有调试代码（print、debugger）
- [ ] 没有硬编码的敏感信息
- [ ] 类型注解完整
- [ ] 必要的注释已添加
- [ ] 代码格式化（black/isort）
- [ ] 静态检查通过（mypy/pylint）

### 审查时检查

- [ ] 功能实现正确
- [ ] 边界条件处理
- [ ] 异常处理完善
- [ ] 无安全漏洞
- [ ] 性能可接受
- [ ] 代码可读性好
- [ ] 测试覆盖充分
