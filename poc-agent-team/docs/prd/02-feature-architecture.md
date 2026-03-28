# 02 Feature Architecture

## 核心架构
* 控制节点 (Overseer)：负责解读任务目标并切分为微任务。
* 执行节点 (Workers)：包含 Python Expert, Frontend Expert, Test Expert 等。
* 状态总线 (State Bus)：共享的上下文缓存区。
