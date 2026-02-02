# Skill 集成指南

## 阶段与 Skill 映射

| 阶段 | Skill | 主要任务 |
|------|-------|----------|
| development | rapid-prototype-workflow | PRD、UI设计、代码实现 |
| testing | test-expert | 测试方案、用例、执行、报告 |
| bugfix | test-report-followup | 解析报告、分派任务、修复 |
| regression | test-expert | 回归验证、确认修复 |

---

## 调用 Prompt 模板

### Development 阶段

```markdown
你是持续开发助手，正在执行 7×24 自动化开发任务。

## 当前状态
- 项目目录: {project_dir}
- 状态文件: {state_file}
- 当前阶段: development
- 使用 Skill: rapid-prototype-workflow

## 执行要求
1. 读取状态文件获取当前任务和断点
2. 使用 **rapid-prototype-workflow** skill 继续开发
3. 按照 skill 定义的 4 个阶段执行:
   - Phase 1: PRD 文档 (8个)
   - Phase 2: UI 设计 (5轮 Review)
   - Phase 3: 代码实现 (三端)
   - Phase 4: 测试发布
4. 每完成一个子任务，更新状态文件
5. 开发完成后，设置 workflow.current_phase = "testing"

## 断点信息
{checkpoint}

请从断点继续执行。
```

### Testing 阶段

```markdown
你是持续开发助手，正在执行 7×24 自动化开发任务。

## 当前状态
- 项目目录: {project_dir}
- 状态文件: {state_file}
- 当前阶段: testing
- 使用 Skill: test-expert

## 执行要求
1. 读取状态文件获取当前任务
2. 使用 **test-expert** skill 执行测试
3. 按照 skill 定义的 6 个阶段执行:
   - Phase 1: 需求分析
   - Phase 2: 测试设计
   - Phase 3: 测试执行
   - Phase 4: 报告生成
   - Phase 5: 回归测试 (如有历史报告)
   - Phase 6: 产品评审
4. 生成测试报告: docs/test/test-report-v{version}.md
5. 测试完成后:
   - 如果有 Bug → workflow.current_phase = "bugfix"
   - 如果无 Bug → status = "completed"

## 断点信息
{checkpoint}

请从断点继续执行。
```

### Bugfix 阶段

```markdown
你是持续开发助手，正在执行 7×24 自动化开发任务。

## 当前状态
- 项目目录: {project_dir}
- 状态文件: {state_file}
- 当前阶段: bugfix
- 使用 Skill: test-report-followup

## 执行要求
1. 读取状态文件和测试报告
2. 使用 **test-report-followup** skill 执行修复
3. 按照 skill 定义的流程:
   - Phase 1: 报告解析
   - Phase 2: 问题分类
   - Phase 3: 任务分派
   - Phase 4: 修复执行
   - Phase 5: 回归测试 (调用 test-expert)
   - Phase 6: 迭代循环
4. 修复完成后，设置 workflow.current_phase = "regression"

## 测试报告
{test_report_path}

## 断点信息
{checkpoint}

请从断点继续执行。
```

### Regression 阶段

```markdown
你是持续开发助手，正在执行 7×24 自动化开发任务。

## 当前状态
- 项目目录: {project_dir}
- 状态文件: {state_file}
- 当前阶段: regression
- 使用 Skill: test-expert

## 执行要求
1. 读取状态文件和上一版本测试报告
2. 使用 **test-expert** skill 执行回归测试
3. 重点验证:
   - 所有已修复的 Bug
   - 受影响的功能模块
   - P0/P1 核心用例
4. 生成回归测试报告
5. 回归完成后:
   - 全部通过 → status = "completed"
   - 有新 Bug → workflow.current_phase = "bugfix", iteration++

## 上一版本报告
{previous_report_path}

## 断点信息
{checkpoint}

请从断点继续执行。
```

---

## 状态更新规则

### 任务完成时

```python
# 更新进度
state['progress'][phase]['completed'] += 1

# 检查阶段是否完成
if all_tasks_done:
    state['workflow']['phase_status'][phase] = 'completed'
    
    # 阶段流转
    if phase == 'development':
        state['workflow']['current_phase'] = 'testing'
    elif phase == 'testing':
        if has_bugs:
            state['workflow']['current_phase'] = 'bugfix'
        else:
            state['status'] = 'completed'
    elif phase == 'bugfix':
        state['workflow']['current_phase'] = 'regression'
    elif phase == 'regression':
        if has_new_bugs:
            state['workflow']['current_phase'] = 'bugfix'
            state['workflow']['iteration'] += 1
        else:
            state['status'] = 'completed'
```

### 断点保存

```python
state['current_task']['checkpoint'] = {
    'step': 'current_step_name',
    'file': 'path/to/current/file',
    'line': 123,
    'context': '当前正在做什么',
    'saved_at': datetime.utcnow().isoformat()
}
```

---

## 错误处理

### 任务失败

```python
state['current_task']['retry_count'] += 1

if state['current_task']['retry_count'] >= 3:
    # 标记失败，跳过
    state['progress'][phase]['failed'] += 1
    state['errors'].append({
        'task_id': task_id,
        'error': error_message,
        'timestamp': datetime.utcnow().isoformat()
    })
    # 继续下一个任务
    state['status'] = 'continue'
else:
    # 重试
    state['status'] = 'continue'
    state['exit_reason'] = 'retry'
```

### 阶段失败

如果某个阶段失败次数过多，可以选择:
1. 跳过该阶段，继续下一阶段
2. 暂停等待人工干预
3. 回退到上一阶段

```python
if phase_failure_count >= 5:
    state['status'] = 'paused'
    state['exit_reason'] = 'phase_failed'
    # 发送告警
```
