# 项目健康度评估指南

## 评估维度详解

### 1. 需求清晰度 (0-20分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无需求 | 无任何需求文档，只有模糊描述 |
| 6-10 | 需求模糊 | 有简单描述或 README，缺乏细节 |
| 11-15 | 需求基本清晰 | 有 PRD 或需求文档，覆盖主要功能 |
| 16-20 | 需求完整 | PRD 完整(≥4个文档)，包含角色、功能、交互 |

**检查命令:**
```bash
# PRD 文档数量
ls docs/prd/*.md 2>/dev/null | wc -l

# 检查关键需求文档
for f in PRD.md README.md requirements.md 需求.md; do
    [ -f "$f" ] && echo "✓ $f exists"
done

# 检查 PRD 内容完整性
grep -l "功能\|角色\|用户\|需求" docs/prd/*.md 2>/dev/null | wc -l
```

**评分逻辑:**
```python
def score_requirements():
    prd_count = count_files('docs/prd/*.md')
    has_prd = file_exists('PRD.md')
    has_readme = file_exists('README.md')

    if prd_count >= 4:
        return 20  # 完整 PRD
    elif prd_count >= 2 or has_prd:
        return 15  # 基本清晰
    elif prd_count >= 1 or has_readme:
        return 10  # 有描述
    elif has_readme:
        return 5   # 仅 README
    else:
        return 0   # 无需求
```

---

### 2. 代码完整度 (0-25分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无代码 | 无任何代码文件 |
| 6-10 | 骨架代码 | 有基础结构，无实际功能 |
| 11-15 | 部分功能 | 核心功能部分实现 |
| 16-20 | 功能基本完整 | 核心功能已实现，有少量缺失 |
| 21-25 | 功能完整 | 所有需求功能已实现 |

**检查命令:**
```bash
# 统计代码文件
py_count=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" | wc -l)
ts_count=$(find . -name "*.ts" -o -name "*.tsx" | wc -l)
js_count=$(find . -name "*.js" -o -name "*.jsx" -not -path "./node_modules/*" | wc -l)

echo "Python: $py_count, TypeScript: $ts_count, JavaScript: $js_count"

# 检查核心模块
ls src/routes/*.py src/models/*.py 2>/dev/null | wc -l

# 检查 API 端点数量
grep -r "@app\.\|@router\.\|@api\." src/ 2>/dev/null | wc -l
```

**评分逻辑:**
```python
def score_code():
    total_files = count_py() + count_ts() + count_js()
    has_routes = dir_exists('src/routes') or dir_exists('app/routes')
    has_models = dir_exists('src/models') or dir_exists('app/models')
    api_count = count_api_endpoints()

    if total_files >= 50 and api_count >= 10:
        return 25  # 功能完整
    elif total_files >= 30 and api_count >= 5:
        return 20  # 基本完整
    elif total_files >= 15 and has_routes:
        return 15  # 部分功能
    elif total_files >= 5:
        return 10  # 骨架代码
    elif total_files >= 1:
        return 5   # 有代码
    else:
        return 0   # 无代码
```

---

### 3. 测试覆盖度 (0-20分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无测试 | 无任何测试文件 |
| 6-10 | 少量测试 | 有测试文件，覆盖率 < 30% |
| 11-15 | 基础测试 | 核心功能有测试，覆盖率 30-60% |
| 16-20 | 测试充分 | 覆盖率 > 60%，包含单元和集成测试 |

**检查命令:**
```bash
# 统计测试文件
test_count=$(find . -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.spec.ts" | wc -l)
echo "测试文件数: $test_count"

# 运行测试并检查通过率
pytest --tb=no -q 2>/dev/null

# 检查覆盖率（如果有）
pytest --cov=src --cov-report=term-missing 2>/dev/null | grep TOTAL
```

**评分逻辑:**
```python
def score_tests():
    test_count = count_test_files()
    code_count = count_code_files()

    if test_count == 0:
        return 0

    ratio = test_count / max(code_count, 1)

    if ratio >= 0.5 and test_count >= 10:
        return 20  # 测试充分
    elif ratio >= 0.3 and test_count >= 5:
        return 15  # 基础测试
    elif test_count >= 2:
        return 10  # 少量测试
    else:
        return 5   # 有测试
```

---

### 4. 可运行性 (0-20分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无法运行 | 缺少依赖、配置错误、启动失败 |
| 6-10 | 部分可运行 | 能启动但有明显错误 |
| 11-15 | 基本可运行 | 能启动，核心功能可用 |
| 16-20 | 完全可运行 | 启动正常，所有功能可用 |

**检查命令:**
```bash
# 检查依赖文件
[ -f "pyproject.toml" ] && echo "✓ pyproject.toml"
[ -f "package.json" ] && echo "✓ package.json"
[ -f "requirements.txt" ] && echo "✓ requirements.txt"

# 检查启动脚本
[ -f "start.sh" ] && echo "✓ start.sh"
[ -f "docker-compose.yml" ] && echo "✓ docker-compose.yml"

# 尝试启动并检查健康端点
if [ -f "start.sh" ]; then
    timeout 30 ./start.sh &
    sleep 10
    curl -s http://localhost:8000/health && echo "✓ 健康检查通过"
    pkill -f "uvicorn\|npm"
fi
```

**评分逻辑:**
```python
def score_runnable():
    has_deps = file_exists('pyproject.toml') or file_exists('package.json')
    has_start = file_exists('start.sh')
    has_main = file_exists('src/main.py') or file_exists('src/index.ts')

    # 尝试启动检查
    can_start = try_start_project()
    health_ok = check_health_endpoint()

    if can_start and health_ok:
        return 20  # 完全可运行
    elif can_start:
        return 15  # 基本可运行
    elif has_deps and has_main:
        return 10  # 部分可运行
    elif has_deps:
        return 5   # 有配置
    else:
        return 0   # 无法运行
```

---

### 5. 代码质量 (0-15分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 质量差 | 大量代码问题、无规范 |
| 6-10 | 质量一般 | 有一些问题，基本可维护 |
| 11-15 | 质量好 | 代码规范、结构清晰、无明显问题 |

**检查命令:**
```bash
# Python 代码检查
if command -v ruff &>/dev/null; then
    ruff check . --quiet 2>/dev/null && echo "✓ Python 代码规范"
fi

# TypeScript 代码检查
if command -v npx &>/dev/null && [ -f "package.json" ]; then
    npx eslint . --quiet 2>/dev/null && echo "✓ TypeScript 代码规范"
fi

# 检查代码复杂度
if command -v radon &>/dev/null; then
    radon cc src/ -a 2>/dev/null | tail -1
fi
```

**评分逻辑:**
```python
def score_quality():
    lint_errors = run_linter()
    complexity = check_complexity()

    if lint_errors == 0 and complexity < 10:
        return 15  # 质量好
    elif lint_errors < 10:
        return 10  # 质量一般
    elif lint_errors < 50:
        return 5   # 有问题
    else:
        return 0   # 质量差
```

---

## 自动评估脚本

```python
#!/usr/bin/env python3
"""项目健康度自动评估"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

def count_files(pattern):
    """统计匹配的文件数"""
    result = subprocess.run(
        f"find . -name '{pattern}' 2>/dev/null | wc -l",
        shell=True, capture_output=True, text=True
    )
    return int(result.stdout.strip() or 0)

def file_exists(path):
    return Path(path).exists()

def dir_exists(path):
    return Path(path).is_dir()

def assess_health():
    """执行完整健康度评估"""
    score = {
        "requirements": 0,
        "code": 0,
        "tests": 0,
        "runnable": 0,
        "quality": 0
    }

    # 1. 需求清晰度
    prd_count = len(list(Path("docs/prd").glob("*.md"))) if Path("docs/prd").exists() else 0
    if prd_count >= 4:
        score["requirements"] = 20
    elif prd_count >= 2 or file_exists("PRD.md"):
        score["requirements"] = 15
    elif prd_count >= 1:
        score["requirements"] = 10
    elif file_exists("README.md"):
        score["requirements"] = 5

    # 2. 代码完整度
    py_files = len(list(Path(".").rglob("*.py"))) - len(list(Path("venv").rglob("*.py"))) if Path("venv").exists() else len(list(Path(".").rglob("*.py")))
    ts_files = len(list(Path(".").rglob("*.ts"))) + len(list(Path(".").rglob("*.tsx")))
    total_code = py_files + ts_files

    if total_code >= 50:
        score["code"] = 25
    elif total_code >= 30:
        score["code"] = 20
    elif total_code >= 15:
        score["code"] = 15
    elif total_code >= 5:
        score["code"] = 10
    elif total_code >= 1:
        score["code"] = 5

    # 3. 测试覆盖度
    test_files = len(list(Path(".").rglob("test_*.py"))) + len(list(Path(".").rglob("*_test.py")))
    test_files += len(list(Path(".").rglob("*.test.ts"))) + len(list(Path(".").rglob("*.spec.ts")))

    if test_files >= 10:
        score["tests"] = 20
    elif test_files >= 5:
        score["tests"] = 15
    elif test_files >= 2:
        score["tests"] = 10
    elif test_files >= 1:
        score["tests"] = 5

    # 4. 可运行性
    has_start = file_exists("start.sh")
    has_deps = file_exists("pyproject.toml") or file_exists("package.json")
    has_main = file_exists("src/main.py") or file_exists("app/main.py")

    if has_start and has_deps and has_main:
        score["runnable"] = 15  # 需要实际运行验证才能给满分
    elif has_deps and has_main:
        score["runnable"] = 10
    elif has_deps:
        score["runnable"] = 5

    # 5. 代码质量 (简化检查)
    score["quality"] = 10  # 默认中等

    # 计算总分
    total = sum(score.values())

    return {
        "breakdown": score,
        "total": total,
        "usable": total >= 80,
        "assessed_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }

def save_health_to_state(health):
    """保存健康度到状态文件"""
    state_file = Path('.dev-state/state.json')

    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
    else:
        state = {
            "version": "1.0.0",
            "project": {"name": Path.cwd().name, "path": str(Path.cwd())},
            "status": "ready",
            "sessions": {"count": 0},
            "action_history": []
        }

    state['health'] = {
        'score': health['total'],
        'breakdown': health['breakdown'],
        'usable': health['usable'],
        'assessed_at': health['assessed_at']
    }
    state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    state_file.parent.mkdir(exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state

if __name__ == "__main__":
    health = assess_health()
    print(f"\n{'='*50}")
    print("项目健康度评估结果")
    print(f"{'='*50}")
    print(f"需求清晰度: {health['breakdown']['requirements']}/20")
    print(f"代码完整度: {health['breakdown']['code']}/25")
    print(f"测试覆盖度: {health['breakdown']['tests']}/20")
    print(f"可运行性:   {health['breakdown']['runnable']}/20")
    print(f"代码质量:   {health['breakdown']['quality']}/15")
    print(f"{'='*50}")
    print(f"总分: {health['total']}/100")
    print(f"可用状态: {'✅ 是' if health['usable'] else '❌ 否'}")
    print(f"{'='*50}")

    save_health_to_state(health)
    print("\n已保存到 .dev-state/state.json")
```

---

## 健康度提升策略

### 从 0-20 提升到 40

**重点:** 建立需求和基础代码

| 行动 | 预期提升 | Agent |
|------|----------|-------|
| 创建 PRD 文档 | +15-20 | product-expert |
| 搭建项目骨架 | +10-15 | tech-manager |
| 实现第一个功能 | +5-10 | python-expert |

### 从 40 提升到 60

**重点:** 功能实现

| 行动 | 预期提升 | Agent |
|------|----------|-------|
| 实现核心功能 | +10-15 | python-expert + frontend-expert |
| 添加基础测试 | +5-10 | test-expert |
| 确保可运行 | +5-10 | tech-manager |

### 从 60 提升到 80

**重点:** 质量和测试

| 行动 | 预期提升 | Agent |
|------|----------|-------|
| 补充测试用例 | +5-10 | test-expert |
| 修复已知Bug | +5-10 | test-report-followup |
| 代码质量优化 | +5 | python-expert |

### 从 80 提升到 100

**重点:** 完善和优化（可选）

| 行动 | 预期提升 | Agent |
|------|----------|-------|
| 提高测试覆盖率 | +5 | test-expert |
| 完善文档 | +5 | product-expert |
| 性能优化 | +5 | python-expert |
