# DoD and Quality Gates Guide

## 1. AC、DoD、Release Gate 的区别

### Acceptance Criteria
描述某个 Story / Slice 的行为预期。
问题：这个需求算实现正确了吗？

### Definition of Done
描述交付项要达到的通用完成标准。
问题：这个工作项算真正完成了吗？

### Release Gate
描述是否允许将一批变更暴露给真实用户。
问题：这次发布现在能上吗？

---

## 2. 常见 DoD 项

- 代码合并与审查完成
- 自动化测试通过
- 监控/日志/告警补齐
- 文档/Runbook 更新
- 安全/合规检查通过
- 回滚路径可用

---

## 3. 常见 Release Gate 项

- 关键切片验证通过
- 高风险缺陷关闭或获批例外
- canary / staging 结果达标
- hypercare 值班已安排
- rollback 演练或至少脚本就绪
- 客服/运营准备完成（如适用）

---

## 4. 例外机制

任何 gate 例外都必须记录：
- 例外项
- 风险
- 缓解措施
- 批准人
- 失效日期
