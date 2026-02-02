# Playwright UI 自动化测试指南

## Playwright 简介

Playwright 是一个现代化的端到端测试框架，支持 Chromium、Firefox 和 WebKit 浏览器。

## 环境配置

### 安装 Playwright

```bash
# 使用 npm
npm init playwright@latest

# 或手动安装
npm install -D @playwright/test
npx playwright install
```

### 配置文件

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 测试目录
  testDir: './tests/e2e',
  
  // 全局超时
  timeout: 30000,
  
  // 期望超时
  expect: {
    timeout: 5000
  },
  
  // 失败重试
  retries: process.env.CI ? 2 : 0,
  
  // 并行执行
  workers: process.env.CI ? 1 : undefined,
  
  // 报告器
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }]
  ],
  
  // 全局配置
  use: {
    // 基础 URL
    baseURL: 'http://localhost:3000',
    
    // 截图策略
    screenshot: 'only-on-failure',
    
    // 视频录制
    video: 'retain-on-failure',
    
    // 追踪
    trace: 'retain-on-failure',
  },
  
  // 浏览器配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  // 启动开发服务器
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 测试编写规范

### 基本结构

```typescript
// tests/e2e/[module].spec.ts
import { test, expect } from '@playwright/test';

test.describe('[模块名] UI 自动化测试', () => {
  
  // 每个测试前执行
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });
  
  // 每个测试后执行
  test.afterEach(async ({ page }) => {
    // 清理操作
  });
  
  test('TC_UI_001: [测试描述]', async ({ page }) => {
    // 测试步骤
  });
});
```

### 详细步骤记录

> ⚠️ **每个 UI 自动化测试用例必须有详细的操作步骤记录**

```typescript
test('TC_UI_001: 用户登录成功', async ({ page }) => {
  /**
   * 测试用例: TC_UI_001
   * 用例名称: 用户登录成功
   * 优先级: P0
   * 
   * 测试步骤:
   * 1. 打开登录页面 /login
   * 2. 输入用户名: test@example.com
   * 3. 输入密码: password123
   * 4. 点击登录按钮
   * 5. 验证跳转到首页 /home
   * 6. 验证显示欢迎信息
   */
  
  // Step 1: 打开登录页面
  await test.step('打开登录页面', async () => {
    await page.goto('/login');
    await expect(page).toHaveURL('/login');
    await expect(page.locator('h1')).toContainText('登录');
  });
  
  // Step 2: 输入用户名
  await test.step('输入用户名', async () => {
    const usernameInput = page.locator('[data-testid="username"]');
    await usernameInput.fill('test@example.com');
    await expect(usernameInput).toHaveValue('test@example.com');
  });
  
  // Step 3: 输入密码
  await test.step('输入密码', async () => {
    const passwordInput = page.locator('[data-testid="password"]');
    await passwordInput.fill('password123');
  });
  
  // Step 4: 点击登录按钮
  await test.step('点击登录按钮', async () => {
    await page.click('[data-testid="login-btn"]');
  });
  
  // Step 5: 验证跳转到首页
  await test.step('验证跳转到首页', async () => {
    await expect(page).toHaveURL('/home');
  });
  
  // Step 6: 验证显示欢迎信息
  await test.step('验证显示欢迎信息', async () => {
    await expect(page.locator('[data-testid="welcome"]')).toBeVisible();
    await expect(page.locator('[data-testid="welcome"]')).toContainText('欢迎');
  });
});
```

---

## 元素定位策略

### 推荐的定位方式

| 优先级 | 定位方式 | 示例 | 说明 |
|--------|----------|------|------|
| 1 | data-testid | `[data-testid="login-btn"]` | 最推荐，专为测试设计 |
| 2 | role | `getByRole('button', { name: '登录' })` | 语义化定位 |
| 3 | text | `getByText('登录')` | 文本定位 |
| 4 | label | `getByLabel('用户名')` | 表单元素 |
| 5 | placeholder | `getByPlaceholder('请输入用户名')` | 输入框 |
| 6 | CSS | `.login-btn` | 不推荐，易变 |

### 定位示例

```typescript
// 推荐：使用 data-testid
await page.locator('[data-testid="submit-btn"]').click();

// 推荐：使用 role
await page.getByRole('button', { name: '提交' }).click();

// 推荐：使用 text
await page.getByText('登录').click();

// 推荐：使用 label
await page.getByLabel('用户名').fill('test@example.com');

// 不推荐：使用 CSS 类名
await page.locator('.btn-primary').click();
```

---

## Page Object 模式

### 页面对象定义

```typescript
// pages/LoginPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  
  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.locator('[data-testid="username"]');
    this.passwordInput = page.locator('[data-testid="password"]');
    this.loginButton = page.locator('[data-testid="login-btn"]');
    this.errorMessage = page.locator('[data-testid="error-msg"]');
  }
  
  async goto() {
    await this.page.goto('/login');
  }
  
  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
  
  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }
}
```

### 使用页面对象

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('登录功能', () => {
  let loginPage: LoginPage;
  
  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });
  
  test('TC_UI_001: 登录成功', async ({ page }) => {
    await loginPage.login('test@example.com', 'password123');
    await expect(page).toHaveURL('/home');
  });
  
  test('TC_UI_002: 密码错误', async () => {
    await loginPage.login('test@example.com', 'wrongpassword');
    await loginPage.expectError('密码错误');
  });
});
```

---

## 常用断言

```typescript
// 页面断言
await expect(page).toHaveURL('/home');
await expect(page).toHaveTitle('首页');

// 元素可见性
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();

// 文本内容
await expect(locator).toHaveText('确切文本');
await expect(locator).toContainText('部分文本');

// 属性值
await expect(locator).toHaveAttribute('href', '/home');
await expect(locator).toHaveClass(/active/);
await expect(locator).toHaveValue('输入值');

// 数量
await expect(locator).toHaveCount(5);

// 截图对比
await expect(page).toHaveScreenshot('homepage.png');
```

---

## 测试数据管理

```typescript
// tests/fixtures/testData.ts
export const testUsers = {
  validUser: {
    username: 'test@example.com',
    password: 'password123'
  },
  invalidUser: {
    username: 'invalid@example.com',
    password: 'wrongpassword'
  }
};

// 使用测试数据
import { testUsers } from '../fixtures/testData';

test('登录成功', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login(
    testUsers.validUser.username,
    testUsers.validUser.password
  );
});
```

---

## 运行测试

```bash
# 运行所有测试
npx playwright test

# 运行特定文件
npx playwright test tests/e2e/login.spec.ts

# 运行特定浏览器
npx playwright test --project=chromium

# 运行带标签的测试
npx playwright test --grep @smoke

# 调试模式
npx playwright test --debug

# UI 模式
npx playwright test --ui

# 生成报告
npx playwright show-report
```

---

## 截图和录屏

```typescript
// 手动截图
await page.screenshot({ path: 'screenshot.png' });

// 元素截图
await page.locator('[data-testid="chart"]').screenshot({ 
  path: 'chart.png' 
});

// 全页截图
await page.screenshot({ 
  path: 'fullpage.png', 
  fullPage: true 
});
```

---

## 最佳实践

1. **使用 data-testid 定位元素**
2. **使用 Page Object 模式组织代码**
3. **每个测试用例独立，不依赖其他用例**
4. **记录详细的测试步骤**
5. **失败时自动截图和录屏**
6. **使用 test.step 组织测试步骤**
7. **避免硬编码等待时间**
8. **使用 expect 进行断言**
