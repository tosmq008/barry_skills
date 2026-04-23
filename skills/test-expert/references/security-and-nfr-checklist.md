# Security and NFR Checklist

## 1. Security

至少检查：

- 认证与会话
- 授权与越权
- 输入校验
- 文件上传/下载
- 审计日志
- 速率限制 / 防刷
- 敏感数据掩码 / 保留
- 关键管理后台操作保护

### 证据示例
- 安全测试记录
- 审计日志样例
- 越权检查结果
- WAF/rate-limit 配置验证

---

## 2. Performance / Capacity

至少检查：

- 关键路径延迟
- 并发下稳定性
- 资源放大点
- 队列积压 / backpressure
- 峰值与恢复

### 证据示例
- 压测结果
- SLI dashboard 截图/链接
- 资源利用率记录

---

## 3. Reliability / Recovery

至少检查：

- Retry / timeout / fallback
- 幂等
- 数据补偿
- 断路器/降级
- 故障演练或故障注入

### 证据示例
- chaos / failure drill 结果
- runbook 验证
- rollback 演练记录

---

## 4. Accessibility / UX Stability

按需检查：

- 键盘可达性
- 屏幕阅读器关键路径
- 错误状态反馈
- loading / empty / error 一致性
- 多语言 / 文案溢出风险

---

## 5. Compatibility

按需检查：

- 浏览器/设备
- API backward compatibility
- 数据/事件 schema compatibility
