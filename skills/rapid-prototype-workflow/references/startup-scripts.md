# 一键启动脚本模板

## Mac/Linux 启动脚本 (start.sh)

```bash
#!/bin/bash

# ============================================
# 一键启动脚本 - Mac/Linux
# ============================================

# ============ 端口配置（可修改）============
CLIENT_BACKEND_PORT=8000
CLIENT_FRONTEND_PORT=3000
ADMIN_BACKEND_PORT=8001
ADMIN_FRONTEND_PORT=3001
# ==========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       一键启动开发环境                  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Client Backend:  http://localhost:${CLIENT_BACKEND_PORT}"
echo -e "Client Frontend: http://localhost:${CLIENT_FRONTEND_PORT}"
echo -e "Admin Backend:   http://localhost:${ADMIN_BACKEND_PORT}"
echo -e "Admin Frontend:  http://localhost:${ADMIN_FRONTEND_PORT}"
echo -e "Website (静态):  cd website && python -m http.server 4000"
echo ""

# 导出端口环境变量供前端使用
export VITE_CLIENT_API_URL="http://localhost:${CLIENT_BACKEND_PORT}"
export VITE_ADMIN_API_URL="http://localhost:${ADMIN_BACKEND_PORT}"

# 创建日志目录
mkdir -p logs

# 启动 Client Backend
echo -e "${YELLOW}[1/4] 启动 Client Backend...${NC}"
cd client/backend
uv run uvicorn src.main:app --reload --port ${CLIENT_BACKEND_PORT} > ../../logs/client-backend.log 2>&1 &
CLIENT_BACKEND_PID=$!
cd ../..

# 启动 Admin Backend
echo -e "${YELLOW}[2/4] 启动 Admin Backend...${NC}"
cd admin/backend
uv run uvicorn src.main:app --reload --port ${ADMIN_BACKEND_PORT} > ../../logs/admin-backend.log 2>&1 &
ADMIN_BACKEND_PID=$!
cd ../..

# 等待后端启动
sleep 3

# 启动 Client Frontend
echo -e "${YELLOW}[3/4] 启动 Client Frontend...${NC}"
cd client/frontend
npm run dev -- --port ${CLIENT_FRONTEND_PORT} > ../../logs/client-frontend.log 2>&1 &
CLIENT_FRONTEND_PID=$!
cd ../..

# 启动 Admin Frontend
echo -e "${YELLOW}[4/4] 启动 Admin Frontend...${NC}"
cd admin/frontend
npm run dev -- --port ${ADMIN_FRONTEND_PORT} > ../../logs/admin-frontend.log 2>&1 &
ADMIN_FRONTEND_PID=$!
cd ../..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       所有服务已启动                    ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "进程 PID:"
echo -e "  Client Backend:  ${CLIENT_BACKEND_PID}"
echo -e "  Client Frontend: ${CLIENT_FRONTEND_PID}"
echo -e "  Admin Backend:   ${ADMIN_BACKEND_PID}"
echo -e "  Admin Frontend:  ${ADMIN_FRONTEND_PID}"
echo ""
echo -e "日志文件: logs/"
echo -e "停止服务: ./stop.sh 或 Ctrl+C"
echo -e "官网预览: cd website && python -m http.server 4000"
echo ""

# 保存 PID 到文件
echo "${CLIENT_BACKEND_PID}" > .pids
echo "${CLIENT_FRONTEND_PID}" >> .pids
echo "${ADMIN_BACKEND_PID}" >> .pids
echo "${ADMIN_FRONTEND_PID}" >> .pids

# 等待用户中断
wait
```

## Windows 启动脚本 (start.bat)

```batch
@echo off
chcp 65001 >nul

REM ============================================
REM 一键启动脚本 - Windows
REM ============================================

REM ============ 端口配置（可修改）============
set CLIENT_BACKEND_PORT=8000
set CLIENT_FRONTEND_PORT=3000
set ADMIN_BACKEND_PORT=8001
set ADMIN_FRONTEND_PORT=3001
REM ==========================================

echo ========================================
echo        一键启动开发环境
echo ========================================
echo.
echo Client Backend:  http://localhost:%CLIENT_BACKEND_PORT%
echo Client Frontend: http://localhost:%CLIENT_FRONTEND_PORT%
echo Admin Backend:   http://localhost:%ADMIN_BACKEND_PORT%
echo Admin Frontend:  http://localhost:%ADMIN_FRONTEND_PORT%
echo Website (静态):  cd website ^&^& python -m http.server 4000
echo.

REM 导出端口环境变量供前端使用
set VITE_CLIENT_API_URL=http://localhost:%CLIENT_BACKEND_PORT%
set VITE_ADMIN_API_URL=http://localhost:%ADMIN_BACKEND_PORT%

REM 创建日志目录
if not exist logs mkdir logs

REM 启动 Client Backend
echo [1/4] 启动 Client Backend...
start /B cmd /c "cd client\backend && uv run uvicorn src.main:app --reload --port %CLIENT_BACKEND_PORT% > ..\..\logs\client-backend.log 2>&1"

REM 启动 Admin Backend
echo [2/4] 启动 Admin Backend...
start /B cmd /c "cd admin\backend && uv run uvicorn src.main:app --reload --port %ADMIN_BACKEND_PORT% > ..\..\logs\admin-backend.log 2>&1"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动 Client Frontend
echo [3/4] 启动 Client Frontend...
start /B cmd /c "cd client\frontend && npm run dev -- --port %CLIENT_FRONTEND_PORT% > ..\..\logs\client-frontend.log 2>&1"

REM 启动 Admin Frontend
echo [4/4] 启动 Admin Frontend...
start /B cmd /c "cd admin\frontend && npm run dev -- --port %ADMIN_FRONTEND_PORT% > ..\..\logs\admin-frontend.log 2>&1"

echo.
echo ========================================
echo        所有服务已启动
echo ========================================
echo.
echo 日志文件: logs\
echo 停止服务: 运行 stop.bat 或关闭此窗口
echo.

pause
```

## Mac/Linux 停止脚本 (stop.sh)

```bash
#!/bin/bash

echo "停止所有服务..."

if [ -f .pids ]; then
    while read pid; do
        kill $pid 2>/dev/null && echo "已停止进程: $pid"
    done < .pids
    rm .pids
fi

# 确保清理所有相关进程
pkill -f "uvicorn src.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "所有服务已停止"
```

## Windows 停止脚本 (stop.bat)

```batch
@echo off
echo 停止所有服务...

taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM node.exe 2>nul

echo 所有服务已停止
pause
```

---

## 前端 API 地址配置

**前端必须从环境变量读取后端地址，确保端口修改后能正常串联：**

```typescript
// client/frontend/src/api/config.ts
export const API_BASE_URL = import.meta.env.VITE_CLIENT_API_URL || 'http://localhost:8000';

// admin/frontend/src/api/config.ts
export const API_BASE_URL = import.meta.env.VITE_ADMIN_API_URL || 'http://localhost:8001';
```

```typescript
// client/frontend/src/api/index.ts
import axios from 'axios';
import { API_BASE_URL } from './config';

const api = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    timeout: 10000,
});

export default api;
```

---

## 启动脚本检查清单

```markdown
# 一键启动脚本必须检查项

## 脚本文件
- [ ] start.sh 存在且可执行 (chmod +x start.sh)
- [ ] start.bat 存在
- [ ] stop.sh 存在且可执行
- [ ] stop.bat 存在

## 端口配置
- [ ] 端口变量在脚本顶部，易于修改
- [ ] 前端环境变量正确导出 (VITE_CLIENT_API_URL, VITE_ADMIN_API_URL)
- [ ] 前端代码从环境变量读取 API 地址

## 功能验证
- [ ] 修改端口后，前后端能正常通信
- [ ] 日志文件正确生成到 logs/ 目录
- [ ] stop 脚本能正确停止所有服务
```


---

## Website 官网说明 (纯静态页面)

Website 是纯静态 HTML 页面，无需构建工具，直接编写 HTML/CSS/JS 即可。

### 目录结构
```
website/
├── index.html          # 首页
├── features.html       # 功能介绍
├── pricing.html        # 定价页面
├── about.html          # 关于我们
├── contact.html        # 联系我们
├── 404.html            # 404页面
├── css/
│   └── style.css       # 样式文件
├── js/
│   └── main.js         # 脚本文件（如需要）
└── images/             # 图片资源
```

### 使用 frontend-design skill 优化官网

**必须使用 `frontend-design` skill 对官网页面进行 Review 和优化：**

```bash
# 激活 frontend-design skill 优化官网
/frontend-design

# 优化指令示例
"请使用 frontend-design skill 优化官网页面：
- 检查视觉层次和排版
- 优化色彩搭配和对比度
- 确保 CTA 按钮突出
- 检查响应式适配
- 优化首屏加载体验"
```

### 官网 Review 检查项

```markdown
# 官网页面 Review 检查项

## 视觉设计
- [ ] Hero 区域视觉冲击力足够
- [ ] CTA 按钮颜色突出、位置明显
- [ ] 色彩搭配和谐统一
- [ ] 字体层次清晰（标题/正文/辅助）
- [ ] 间距和留白充足

## 内容结构
- [ ] 首屏传达核心价值主张
- [ ] 功能介绍清晰易懂
- [ ] 定价方案对比明确
- [ ] 联系方式易于找到

## 响应式
- [ ] 移动端适配良好
- [ ] 导航在小屏幕可用
- [ ] 图片自适应

## SEO
- [ ] 每页有独立 title
- [ ] meta description 已设置
- [ ] 图片有 alt 属性
```

### 本地预览

```bash
# 使用 Python 简单服务器预览
cd website
python -m http.server 4000

# 或使用 npx serve
npx serve website -p 4000
```

