# 项目健康度评估指南

## 评估维度详解

### 1. 需求清晰度 (0-20分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无需求 | 无任何需求文档，只有模糊描述 |
| 6-10 | 需求模糊 | 有简单描述，缺乏细节 |
| 11-15 | 需求基本清晰 | 有PRD或需求文档，覆盖主要功能 |
| 16-20 | 需求完整 | PRD完整，包含角色、功能、交互、视觉规范 |

**检查项:**
```bash
# 检查 PRD 文档
ls docs/prd/*.md 2>/dev/null | wc -l  # 期望 >= 4

# 检查需求文档内容
grep -l "功能\|角色\|用户" docs/prd/*.md 2>/dev/null | wc -l
```

### 2. 代码完整度 (0-25分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无代码 | 无任何代码文件 |
| 6-10 | 骨架代码 | 有基础结构，无实际功能 |
| 11-15 | 部分功能 | 核心功能部分实现 |
| 16-20 | 功能基本完整 | 核心功能已实现，有少量缺失 |
| 21-25 | 功能完整 | 所有需求功能已实现 |

**检查项:**
```bash
# 统计代码文件
find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" | wc -l

# 检查核心模块
ls src/routes/*.py src/models/*.py 2>/dev/null | wc -l

# 检查 API 端点数量
grep -r "@app\.\|@router\." src/ 2>/dev/null | wc -l
```

### 3. 测试覆盖度 (0-20分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无测试 | 无任何测试文件 |
| 6-10 | 少量测试 | 有测试文件，覆盖率 < 30% |
| 11-15 | 基础测试 | 核心功能有测试，覆盖率 30-60% |
| 16-20 | 测试充分 | 覆盖率 > 60%，包含单元和集成测试 |

**检查项:**
```bash
# 统计测试文件
find . -name "test_*.py" -o -name "*_test.py" | wc -l

# 运行测试并检查通过率
pytest --tb=no -q 2>/dev/null

# 检查覆盖率（如果有）
pytest --cov=src --cov-report=term-missing 2>/dev/null | grep TOTAL
```

### 4. 可运行性 (0-20分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 无法运行 | 缺少依赖、配置错误、启动失败 |
| 6-10 | 部分可运行 | 能启动但有明显错误 |
| 11-15 | 基本可运行 | 能启动，核心功能可用 |
| 16-20 | 完全可运行 | 启动正常，所有功能可用 |

**检查项:**
```bash
# 检查依赖文件
ls pyproject.toml package.json requirements.txt 2>/dev/null

# 尝试启动
timeout 30 ./start.sh &
sleep 10
curl -s http://localhost:8000/health

# 检查错误日志
tail -20 logs/*.log 2>/dev/null | grep -i error
```

### 5. 代码质量 (0-15分)

| 分数 | 状态 | 判断标准 |
|------|------|----------|
| 0-5 | 质量差 | 大量代码问题、无规范 |
| 6-10 | 质量一般 | 有一些问题，基本可维护 |
| 11-15 | 质量好 | 代码规范、结构清晰、无明显问题 |

**检查项:**
```bash
# Python 代码检查
ruff check . --quiet 2>/dev/null && echo "OK" || echo "有问题"

# TypeScript 代码检查
npx eslint . --quiet 2>/dev/null && echo "OK" || echo "有问题"

# 检查代码复杂度
radon cc src/ -a 2>/dev/null | tail -1
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

def assess_health():
    score = {
        "requirements": 0,
        "code": 0,
        "tests": 0,
        "runnable": 0,
        "quality": 0
    }

    # 1. 需求清晰度
    prd_count = len(list(Path("docs/prd").glob("*.md"))) if Path("docs/prd").exists() else 0
    if prd_count >= 8:
        score["requirements"] = 20
    elif prd_count >= 4:
        score["requirements"] = 15
    elif prd_count >= 1:
        score["requirements"] = 10
    elif Path("PRD.md").exists() or Path("README.md").exists():
        score["requirements"] = 5

    # 2. 代码完整度
    py_files = len(list(Path(".").rglob("*.py")))
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
    if test_files >= 10:
        score["tests"] = 20
    elif test_files >= 5:
        score["tests"] = 15
    elif test_files >= 2:
        score["tests"] = 10
    elif test_files >= 1:
        score["tests"] = 5

    # 4. 可运行性 (简化检查)
    has_start = Path("start.sh").exists()
    has_deps = Path("pyproject.toml").exists() or Path("package.json").exists()
    has_main = Path("src/main.py").exists() or Path("src/index.ts").exists()

    if has_start and has_deps and has_main:
        score["runnable"] = 15  # 需要实际运行验证才能给满分
    elif has_deps and has_main:
        score["runnable"] = 10
    elif has_deps:
        score["runnable"] = 5

    # 5. 代码质量 (简化检查)
    # 检查是否有明显的代码问题
    score["quality"] = 10  # 默认中等，需要实际检查调整

    # 计算总分
    total = sum(score.values())

    return {
        "breakdown": score,
        "total": total,
        "usable": total >= 80
    }

if __name__ == "__main__":
    result = assess_health()
    print(json.dumps(result, indent=2))
```

---

## 健康度提升策略

### 从 0-20 提升到 40

**重点:** 建立需求和基础代码

1. 创建 PRD 文档 (+15-20)
2. 搭建项目骨架 (+10-15)
3. 实现第一个功能 (+5-10)

### 从 40 提升到 60

**重点:** 功能实现

1. 实现核心功能 (+10-15)
2. 添加基础测试 (+5-10)
3. 确保可运行 (+5-10)

### 从 60 提升到 80

**重点:** 质量和测试

1. 补充测试用例 (+5-10)
2. 修复已知Bug (+5-10)
3. 代码质量优化 (+5)

### 从 80 提升到 100

**重点:** 完善和优化

1. 提高测试覆盖率 (+5)
2. 完善文档 (+5)
3. 性能优化 (+5)
4. 安全加固 (+5)

---

## 健康度变化追踪

```json
{
  "health_history": [
    {
      "timestamp": "2024-01-31T09:00:00Z",
      "score": 0,
      "action": "项目初始化"
    },
    {
      "timestamp": "2024-01-31T10:00:00Z",
      "score": 18,
      "action": "创建 PRD 文档",
      "delta": "+18"
    },
    {
      "timestamp": "2024-01-31T12:00:00Z",
      "score": 45,
      "action": "实现用户认证模块",
      "delta": "+27"
    },
    {
      "timestamp": "2024-01-31T15:00:00Z",
      "score": 65,
      "action": "添加单元测试",
      "delta": "+20"
    },
    {
      "timestamp": "2024-01-31T18:00:00Z",
      "score": 82,
      "action": "修复 Bug 并优化",
      "delta": "+17"
    }
  ]
}
```
