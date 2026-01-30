# Language-Specific Project Structures

## Java/Spring Boot Backend

```
{module}-backend/
├── src/
│   ├── main/
│   │   ├── java/com/company/{module}/
│   │   │   ├── Application.java
│   │   │   ├── controller/          # 控制层 - API入口
│   │   │   │   ├── BaseController.java
│   │   │   │   └── {Feature}Controller.java
│   │   │   ├── service/             # 服务层 - 业务逻辑
│   │   │   │   ├── {Feature}Service.java (interface)
│   │   │   │   └── impl/
│   │   │   │       └── {Feature}ServiceImpl.java
│   │   │   ├── repository/          # 数据访问层
│   │   │   │   └── {Entity}Repository.java
│   │   │   ├── entity/              # 实体层 - 数据库映射
│   │   │   │   ├── BaseEntity.java
│   │   │   │   └── {Entity}.java
│   │   │   ├── dto/                 # 数据传输对象
│   │   │   │   ├── request/
│   │   │   │   └── response/
│   │   │   ├── config/              # 配置类
│   │   │   ├── exception/           # 异常处理
│   │   │   │   ├── BaseException.java
│   │   │   │   └── GlobalExceptionHandler.java
│   │   │   ├── util/                # 工具类
│   │   │   └── constant/            # 常量定义
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       └── db/migration/        # Flyway迁移脚本
│   └── test/
│       └── java/com/company/{module}/
│           ├── controller/
│           ├── service/
│           └── repository/
├── pom.xml
└── README.md
```

## Python/FastAPI Backend

```
{module}_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # 应用入口
│   ├── api/                         # 控制层 - API路由
│   │   ├── __init__.py
│   │   ├── deps.py                  # 依赖注入
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           └── {feature}.py
│   ├── services/                    # 服务层 - 业务逻辑
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── {feature}_service.py
│   ├── repositories/                # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── {entity}_repository.py
│   ├── models/                      # 实体层 - ORM模型
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── {entity}.py
│   ├── schemas/                     # 数据传输对象
│   │   ├── __init__.py
│   │   ├── request/
│   │   └── response/
│   ├── core/                        # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── exceptions/                  # 异常处理
│   │   ├── __init__.py
│   │   └── handlers.py
│   └── utils/                       # 工具类
├── migrations/                      # Alembic迁移
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   └── services/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Node.js/Express Backend

```
{module}-backend/
├── src/
│   ├── index.ts                     # 应用入口
│   ├── app.ts                       # Express配置
│   ├── controllers/                 # 控制层
│   │   ├── base.controller.ts
│   │   └── {feature}.controller.ts
│   ├── services/                    # 服务层
│   │   ├── base.service.ts
│   │   └── {feature}.service.ts
│   ├── repositories/                # 数据访问层
│   │   ├── base.repository.ts
│   │   └── {entity}.repository.ts
│   ├── entities/                    # 实体层
│   │   ├── base.entity.ts
│   │   └── {entity}.entity.ts
│   ├── dto/                         # 数据传输对象
│   │   ├── request/
│   │   └── response/
│   ├── middlewares/                 # 中间件
│   ├── config/                      # 配置
│   ├── exceptions/                  # 异常处理
│   ├── utils/                       # 工具类
│   └── types/                       # 类型定义
├── migrations/                      # 数据库迁移
├── tests/
│   ├── unit/
│   └── integration/
├── package.json
├── tsconfig.json
└── README.md
```

## Go/Gin Backend

```
{module}-backend/
├── cmd/
│   └── server/
│       └── main.go                  # 应用入口
├── internal/
│   ├── handler/                     # 控制层 - HTTP处理
│   │   ├── base.go
│   │   └── {feature}_handler.go
│   ├── service/                     # 服务层 - 业务逻辑
│   │   ├── base.go
│   │   └── {feature}_service.go
│   ├── repository/                  # 数据访问层
│   │   ├── base.go
│   │   └── {entity}_repository.go
│   ├── model/                       # 实体层
│   │   ├── base.go
│   │   └── {entity}.go
│   ├── dto/                         # 数据传输对象
│   │   ├── request/
│   │   └── response/
│   └── middleware/                  # 中间件
├── pkg/                             # 公共包
│   ├── config/
│   ├── errors/
│   └── utils/
├── migrations/                      # 数据库迁移
├── tests/
├── go.mod
├── go.sum
└── README.md
```

## React/Vue Frontend

```
{module}-frontend/
├── src/
│   ├── main.tsx                     # 应用入口
│   ├── App.tsx
│   ├── api/                         # API层 - 接口调用
│   │   ├── client.ts                # HTTP客户端
│   │   ├── types.ts                 # API类型定义
│   │   └── modules/
│   │       └── {feature}.api.ts
│   ├── services/                    # 服务层 - 业务逻辑封装
│   │   └── {feature}.service.ts
│   ├── stores/                      # 状态管理层
│   │   ├── index.ts
│   │   └── {feature}.store.ts
│   ├── pages/                       # 页面层
│   │   └── {Feature}/
│   │       ├── index.tsx
│   │       └── components/
│   ├── components/                  # 公共组件层
│   │   ├── base/                    # 基础组件
│   │   └── business/                # 业务组件
│   ├── hooks/                       # 自定义Hooks
│   ├── utils/                       # 工具函数
│   ├── types/                       # 类型定义
│   ├── constants/                   # 常量
│   └── styles/                      # 样式
├── tests/
│   ├── unit/
│   └── e2e/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Shared Module Structure

```
shared/
├── constants/                       # 共享常量
│   ├── error-codes.ts
│   └── enums.ts
├── types/                           # 共享类型
│   ├── common.ts
│   └── api.ts
├── utils/                           # 共享工具
│   ├── validators.ts
│   └── formatters.ts
└── contracts/                       # API契约
    └── {feature}.contract.ts
```
