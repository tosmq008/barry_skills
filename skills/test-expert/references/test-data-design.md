# 测试数据设计规范

## 测试数据设计原则

### 核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| 独立性 | 每个用例使用独立数据 | 用例A和用例B使用不同的测试账号 |
| 可重复性 | 数据可重复创建和清理 | 每次执行前创建，执行后删除 |
| 最小化 | 只创建必要的测试数据 | 测试登录只需要一个用户，不需要创建订单 |
| 真实性 | 数据符合业务规则 | 手机号格式正确，金额在合理范围 |
| 隔离性 | 测试数据与生产数据隔离 | 使用独立的测试数据库 |

---

## 测试数据分类

### 1. 基础数据 (Base Data)
- 系统运行必需的数据
- 测试开始前初始化
- 所有用例共享（只读）

```markdown
## 基础数据清单
| 数据类型 | 数据内容 | 初始化方式 |
|----------|----------|------------|
| 系统配置 | 默认配置项 | SQL 脚本 |
| 字典数据 | 状态码、类型码 | SQL 脚本 |
| 管理员账号 | 超级管理员 | SQL 脚本 |
```

### 2. 用例数据 (Test Case Data)
- 单个用例专用的数据
- 用例执行前创建
- 用例执行后清理

```python
# 示例：用例数据管理
class TestUserLogin:
    
    def test_login_success(self, db_session):
        """用例数据在用例内创建和清理"""
        # Arrange - 创建用例专用数据
        test_user = User(
            phone="13800001111",  # 用例专用手机号
            password=hash_password("123456"),
            nickname="登录测试用户"
        )
        db_session.add(test_user)
        db_session.commit()
        
        # Act
        response = client.post("/api/login", json={
            "phone": "13800001111",
            "password": "123456"
        })
        
        # Assert
        assert response.status_code == 200
        
        # Cleanup - 自动回滚（使用 fixture）
```

### 3. 共享数据 (Shared Data) - ⚠️ 禁止使用
- 多个用例共享的可变数据
- **禁止使用**，会导致用例间依赖

```python
# ❌ 错误示例：共享数据
class TestUserBad:
    shared_user_id = None  # 共享状态 - 禁止！
    
    def test_create_user(self):
        response = client.post("/api/users", json={...})
        self.shared_user_id = response.json()["id"]  # 保存给其他用例 - 禁止！
    
    def test_get_user(self):
        # 依赖上一个用例的数据 - 禁止！
        response = client.get(f"/api/users/{self.shared_user_id}")
```

---

## 测试数据设计方法

### 1. 等价类划分

将输入数据划分为有效等价类和无效等价类：

```markdown
## 用户注册 - 手机号输入
| 等价类 | 类型 | 测试数据 | 预期结果 |
|--------|------|----------|----------|
| 有效手机号 | 有效 | 13800001111 | 注册成功 |
| 空手机号 | 无效 | "" | 提示手机号不能为空 |
| 格式错误 | 无效 | 1380000111 | 提示手机号格式错误 |
| 非数字 | 无效 | 138abcd1111 | 提示手机号格式错误 |
| 已注册 | 无效 | 13800002222 | 提示手机号已注册 |
```

### 2. 边界值分析

针对边界条件设计测试数据：

```markdown
## 密码长度限制 (6-20位)
| 边界 | 测试数据 | 预期结果 |
|------|----------|----------|
| 最小值-1 | "12345" (5位) | 提示密码长度不足 |
| 最小值 | "123456" (6位) | 验证通过 |
| 最小值+1 | "1234567" (7位) | 验证通过 |
| 最大值-1 | 19位密码 | 验证通过 |
| 最大值 | 20位密码 | 验证通过 |
| 最大值+1 | 21位密码 | 提示密码长度超限 |
```

### 3. 错误推测

基于经验推测可能的错误情况：

```markdown
## 常见错误数据
| 场景 | 测试数据 | 预期结果 |
|------|----------|----------|
| SQL 注入 | "'; DROP TABLE users;--" | 安全处理，不执行 |
| XSS 攻击 | "<script>alert(1)</script>" | 转义处理 |
| 特殊字符 | "用户@#$%名" | 正常处理或提示 |
| 超长输入 | 10000字符 | 截断或提示 |
| 空格处理 | "  test  " | 去除首尾空格 |
| 大小写 | "TEST@EXAMPLE.COM" | 统一处理 |
```

---

## 测试数据管理

### 数据库 Fixture 示例

```python
# conftest.py
import pytest
from sqlmodel import Session, SQLModel, create_engine

@pytest.fixture(scope="function")
def db_session():
    """每个测试函数使用独立的数据库会话"""
    # 使用内存数据库或测试数据库
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
        session.rollback()  # 自动回滚，清理数据

@pytest.fixture
def test_user(db_session):
    """创建测试用户的 fixture"""
    user = User(
        phone="13800000000",
        password=hash_password("123456"),
        nickname="测试用户"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

### 测试数据工厂

```python
# tests/factories.py
from faker import Faker

fake = Faker('zh_CN')

class UserFactory:
    """用户测试数据工厂"""
    
    @staticmethod
    def create(db_session, **kwargs):
        """创建测试用户"""
        defaults = {
            "phone": fake.phone_number(),
            "password": hash_password("123456"),
            "nickname": fake.name(),
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_batch(db_session, count, **kwargs):
        """批量创建测试用户"""
        return [UserFactory.create(db_session, **kwargs) for _ in range(count)]
```

---

## 测试数据模板

### 用户数据模板

```markdown
## 用户测试数据
| 数据项 | 有效值 | 无效值 | 边界值 |
|--------|--------|--------|--------|
| 手机号 | 13800001111 | "", "abc", "1380000" | 11位数字 |
| 密码 | "123456" | "", "12345" | 6位, 20位 |
| 昵称 | "测试用户" | "" | 1字符, 20字符 |
| 邮箱 | "test@example.com" | "invalid", "" | - |
```

### API 请求数据模板

```markdown
## POST /api/register 请求数据
| 场景 | 请求体 | 预期状态码 |
|------|--------|------------|
| 正常注册 | {"phone":"13800001111","password":"123456"} | 201 |
| 缺少手机号 | {"password":"123456"} | 400 |
| 缺少密码 | {"phone":"13800001111"} | 400 |
| 手机号已存在 | {"phone":"已存在","password":"123456"} | 400 |
| 密码太短 | {"phone":"13800001111","password":"123"} | 400 |
```

---

## 测试数据检查清单

- [ ] 每个用例使用独立的测试数据
- [ ] 测试数据在用例执行后自动清理
- [ ] 不存在用例间的数据依赖
- [ ] 测试数据符合业务规则
- [ ] 覆盖了有效等价类
- [ ] 覆盖了无效等价类
- [ ] 覆盖了边界值
- [ ] 考虑了特殊字符和异常输入
