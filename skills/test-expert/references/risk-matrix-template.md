# Risk Matrix Template

## 1. 风险评分方法

推荐最少使用：
- Likelihood：1-5
- Impact：1-5
- Score = Likelihood × Impact

也可以加入：
- Detectability
- Exposure window
- Reversibility

---

## 2. 风险类别建议

- 功能正确性
- 数据完整性
- 权限/安全
- 集成/外部依赖
- 性能/容量
- 发布/迁移/回滚
- 可观测性不足
- 人工操作风险

---

## 3. 风险矩阵字段

| 字段 | 说明 |
|---|---|
| Risk ID | 唯一编号 |
| Scenario | 具体风险场景 |
| Type | 风险类别 |
| Likelihood | 发生可能性 |
| Impact | 业务/技术影响 |
| Score | 风险优先级 |
| Detection | 如何发现 |
| Prevention | 如何预防 |
| Test layer | small / medium / large / exploratory / security / NFR |

---

## 4. 优先级建议

- 16-25：必须优先覆盖；默认阻断上线或至少需要强缓解
- 9-15：必须有明确测试与监控证据
- 4-8：可降级处理，但要记录
- 1-3：可延后

---

## 5. 常见高风险例子

- 重试导致重复扣费/重复下单
- 越权读写他人数据
- canary 与全量配置不一致
- 数据迁移后回滚不可逆
- 告警不存在，问题已发生但没人发现
