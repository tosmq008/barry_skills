# 测试方案与测试用例模板

## 测试方案模板

```markdown
# 测试方案: [功能名称]

## 1. 测试范围
- 被测功能：[功能描述]
- 测试类型：单元测试 / 集成测试 / 功能测试 / E2E测试

## 2. 测试方法
- [ ] 黑盒测试：验证输入输出
- [ ] 边界值测试：边界条件验证
- [ ] 等价类划分：有效/无效输入

## 3. 测试数据
- 数据来源：测试用例自行创建
- 数据清理：每个用例执行后自动清理
- 隔离方式：独立测试数据库

## 4. 测试环境
- 数据库：SQLite (test.db)
- 后端：本地 FastAPI 测试服务器
- 前端：Jest + React Testing Library

## 5. 通过标准
- 所有测试用例通过
- 代码覆盖率 > 60% (核心逻辑)
- 无阻塞性Bug
```

## 测试用例模板

```markdown
# 测试用例: TC_[模块]_[编号]

## 基本信息
- 用例ID: TC_USER_001
- 用例名称: 用户注册成功
- 测试类型: 功能测试
- 优先级: P0

## 前置条件
- 测试数据库已初始化
- 手机号 13800001111 未被注册

## 测试步骤
1. 调用注册接口 POST /api/register
2. 传入参数: {"phone": "13800001111", "password": "123456"}

## 预期结果
- 返回状态码 201
- 返回用户ID
- 数据库中存在该用户记录

## 测试数据
- 本用例自行创建，执行后自动清理

## 独立性声明
- 不依赖任何其他用例
- 不为其他用例提供数据
```

---

## 单元测试示例

```python
# tests/unit/test_utils.py
import pytest
from src.utils import hash_password, verify_password

class TestPasswordUtils:
    """密码工具函数单元测试 - 每个用例独立"""
    
    def test_hash_password_returns_hash(self):
        """TC_UNIT_001: 密码哈希返回非空字符串"""
        result = hash_password("123456")
        assert result is not None
        assert len(result) > 0
        assert result != "123456"
    
    def test_verify_password_correct(self):
        """TC_UNIT_002: 正确密码验证通过"""
        hashed = hash_password("123456")
        assert verify_password("123456", hashed) is True
    
    def test_verify_password_incorrect(self):
        """TC_UNIT_003: 错误密码验证失败"""
        hashed = hash_password("123456")
        assert verify_password("wrong", hashed) is False
```

## 集成测试示例 (API Test)

```python
# tests/integration/test_user_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_test_session

client = TestClient(app)

class TestUserAPI:
    """用户API集成测试 - 每个用例独立"""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """每个用例执行前后自动清理数据库"""
        yield
        db_session.rollback()
    
    def test_register_success(self, db_session):
        """TC_API_001: 用户注册成功"""
        # Arrange - 本用例独立准备数据
        user_data = {
            "phone": "13800001111",
            "password": "123456",
            "nickname": "测试用户"
        }
        
        # Act
        response = client.post("/api/register", json=user_data)
        
        # Assert
        assert response.status_code == 201
        assert "id" in response.json()
    
    def test_register_duplicate_phone(self, db_session):
        """TC_API_002: 重复手机号注册失败"""
        # Arrange - 本用例自己创建前置数据
        existing_user = {"phone": "13800002222", "password": "123456", "nickname": "已存在"}
        client.post("/api/register", json=existing_user)
        
        # Act - 再次注册相同手机号
        response = client.post("/api/register", json=existing_user)
        
        # Assert
        assert response.status_code == 400
        assert "已注册" in response.json()["detail"]
    
    def test_login_success(self, db_session):
        """TC_API_003: 用户登录成功"""
        # Arrange - 本用例自己创建测试用户
        user_data = {"phone": "13800003333", "password": "123456", "nickname": "登录测试"}
        client.post("/api/register", json=user_data)
        
        # Act
        response = client.post("/api/login", json={
            "phone": "13800003333",
            "password": "123456"
        })
        
        # Assert
        assert response.status_code == 200
        assert "token" in response.json()
```

## 功能测试示例

```python
# tests/functional/test_user_flow.py
class TestUserFunctional:
    """用户功能测试 - 每个用例独立验证完整功能"""
    
    def test_user_can_update_profile(self, db_session):
        """TC_FUNC_001: 用户可以修改个人资料"""
        # Arrange - 创建并登录用户
        user = create_test_user(db_session, phone="13800004444")
        token = login_user(user)
        
        # Act - 修改资料
        response = client.put(
            "/api/user/profile",
            json={"nickname": "新昵称"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["nickname"] == "新昵称"
    
    def test_user_can_change_password(self, db_session):
        """TC_FUNC_002: 用户可以修改密码"""
        # Arrange - 本用例独立创建用户
        user = create_test_user(db_session, phone="13800005555", password="old123")
        token = login_user(user)
        
        # Act
        response = client.put(
            "/api/user/password",
            json={"old_password": "old123", "new_password": "new456"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        # 验证新密码可以登录
        login_response = client.post("/api/login", json={
            "phone": "13800005555",
            "password": "new456"
        })
        assert login_response.status_code == 200
```

## E2E测试示例 (UI自动化)

```typescript
// tests/e2e/user.spec.ts
import { test, expect } from '@playwright/test';

test.describe('用户流程E2E测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 每个用例前重置测试数据
    await resetTestDatabase();
  });
  
  test('TC_E2E_001: 用户可以完成注册流程', async ({ page }) => {
    // Arrange
    await page.goto('/register');
    
    // Act
    await page.fill('[data-testid="phone"]', '13800006666');
    await page.fill('[data-testid="password"]', '123456');
    await page.fill('[data-testid="nickname"]', 'E2E测试用户');
    await page.click('[data-testid="submit"]');
    
    // Assert
    await expect(page).toHaveURL('/home');
    await expect(page.locator('[data-testid="welcome"]')).toContainText('E2E测试用户');
  });
  
  test('TC_E2E_002: 用户可以完成登录流程', async ({ page }) => {
    // Arrange - 本用例独立创建测试用户
    await createTestUser({ phone: '13800007777', password: '123456' });
    await page.goto('/login');
    
    // Act
    await page.fill('[data-testid="phone"]', '13800007777');
    await page.fill('[data-testid="password"]', '123456');
    await page.click('[data-testid="submit"]');
    
    // Assert
    await expect(page).toHaveURL('/home');
  });
});
```

---

## 测试数据原则

```markdown
# 测试数据原则

1. **独立性原则**
   - 每个测试用例使用独立的测试数据
   - 测试数据在用例执行前创建，执行后清理
   - 不依赖其他用例产生的数据

2. **隔离性原则**
   - 测试环境与生产环境完全隔离
   - 使用独立的测试数据库 (test.db)
   - 每次测试前重置数据库状态

3. **可重复性原则**
   - 测试必须能任意次数重复执行
   - 每次执行结果必须一致
   - 不受执行顺序影响

4. **最小化原则**
   - 只创建测试所需的最少数据
   - 避免复杂的数据依赖关系
   - 测试数据简单明确
```

## 测试用例独立性示例

```python
# ✅ 正确示例：独立的测试用例
class TestUserAPI:
    
    def test_create_user(self, db_session):
        """测试创建用户 - 独立用例"""
        # Arrange: 准备测试数据
        user_data = {"phone": "13800001111", "nickname": "测试用户"}
        
        # Act: 执行操作
        response = client.post("/api/users", json=user_data)
        
        # Assert: 验证结果
        assert response.status_code == 201
        assert response.json()["phone"] == "13800001111"
    
    def test_get_user(self, db_session):
        """测试获取用户 - 独立用例，自己创建所需数据"""
        # Arrange: 本用例自己创建测试数据
        user = User(phone="13800002222", nickname="查询测试")
        db_session.add(user)
        db_session.commit()
        
        # Act
        response = client.get(f"/api/users/{user.id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["nickname"] == "查询测试"

# ❌ 错误示例：用例间存在依赖
class TestUserAPIBad:
    created_user_id = None  # 共享状态 - 错误！
    
    def test_create_user(self):
        response = client.post("/api/users", json={...})
        self.created_user_id = response.json()["id"]  # 保存给其他用例用 - 错误！
    
    def test_get_user(self):
        # 依赖上一个用例创建的数据 - 错误！
        response = client.get(f"/api/users/{self.created_user_id}")
```

## 测试分层策略

```
┌─────────────────────────────────────────────────────────────────┐
│                        测试金字塔                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                         ┌─────────┐                             │
│                         │  E2E    │  ← 少量核心流程              │
│                         │  Tests  │    (UI自动化)                │
│                       ┌─┴─────────┴─┐                           │
│                       │ Integration │  ← API层测试               │
│                       │    Tests    │    (接口测试)              │
│                     ┌─┴─────────────┴─┐                         │
│                     │   Unit Tests    │  ← 大量单元测试          │
│                     │                 │    (函数/方法)           │
│                     └─────────────────┘                         │
│                                                                 │
│  快速原型重点：集成测试 (API) + 功能测试 (核心流程)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
