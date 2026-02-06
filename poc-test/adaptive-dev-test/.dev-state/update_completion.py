#!/usr/bin/env python3
"""更新状态文件 - 标记 product-expert 任务完成"""
import json
from datetime import datetime
from pathlib import Path

state_file = Path('.dev-state/state.json')

with open(state_file, 'r') as f:
    state = json.load(f)

# 添加完成的 agent 记录
completed_agent = {
    "agent": "product-expert",
    "task": "prd_creation",
    "status": "completed",
    "completed_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "deliverables": [
        "docs/prd/01-project-overview.md",
        "docs/prd/03-competitive-analysis.md",
        "docs/prd/04-feature-architecture.md",
        "docs/prd/05-role-permission.md",
        "docs/prd/07-page-list.md",
        "docs/prd/10-visual-style.md",
        "docs/prd/11-functional-spec.md",
        "docs/prd/13-acceptance-criteria.md",
        "docs/prd/README.md"
    ]
}

state['agent_coordination']['completed_agents'].append(completed_agent)

# 更新当前行动状态
state['current_action'] = None

# 添加行动历史
action_record = {
    "type": "prd_creation",
    "agent": "product-expert",
    "started_at": state['decision_log'][0]['timestamp'],
    "completed_at": completed_agent['completed_at'],
    "result": "成功创建完整PRD文档，包含9个核心文档",
    "deliverables": completed_agent['deliverables']
}
state['action_history'].append(action_record)

# 更新心跳
state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("✅ 状态文件已更新")
print(f"Agent: {completed_agent['agent']}")
print(f"任务: {completed_agent['task']}")
print(f"状态: {completed_agent['status']}")
print(f"完成时间: {completed_agent['completed_at']}")
print(f"\n交付物:")
for deliverable in completed_agent['deliverables']:
    print(f"  - {deliverable}")
