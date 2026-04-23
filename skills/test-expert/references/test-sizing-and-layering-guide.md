# Test Sizing and Layering Guide

## 目标

优先使用更小、更快、更稳定的测试；只有风险真的需要时才上更重的测试。

---

## 1. Small

### 适合
- 纯逻辑
- 规则计算
- 输入校验
- 边界条件
- 策略与权限决策

### 要求
- 无真实网络
- 无真实文件系统依赖（尽可能）
- 运行快、可并行、结果稳定

---

## 2. Medium

### 适合
- 模块间集成
- DB / queue / service 在可控环境下联动
- 合同/契约验证
- 关键适配器验证

### 要求
- 依赖可控
- 环境可重置
- 证据可追溯

---

## 3. Large

### 适合
- 端到端用户路径
- 发布前 smoke / canary 关键验证
- 跨系统集成
- 高风险真实流程验证

### 要求
- 只覆盖少量关键闭环
- 尽量避免大量脆弱 UI 操作
- 数据与环境可恢复
- 结果要和放行门禁关联

---

## 4. Contract Tests

适合：
- API schema
- event schema
- provider/consumer contract
- backward compatibility

---

## 5. Exploratory

适合：
- 新功能体验
- 复杂状态组合
- 跨角色协同
- 观察性与可调试性验证

---

## 6. 分层建议

优先顺序：
1. small 覆盖规则与边界
2. medium 覆盖模块与契约
3. large 覆盖少量关键闭环
4. exploratory 覆盖未知风险
5. security / NFR 按风险补齐

---

## 7. 反模式

- 用大量 E2E 代替中小型测试
- UI 测试依赖实现细节
- 没有环境重置策略
- 所有发布风险都寄托给“手工回归”
