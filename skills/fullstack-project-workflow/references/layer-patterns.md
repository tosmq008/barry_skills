# OOP Layered Architecture Patterns

## Core Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              (Controller / Handler / API)                    │
│         职责: 接收请求、参数校验、调用服务、返回响应              │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                            │
│                   (Business Logic)                           │
│         职责: 业务逻辑、事务管理、跨实体协调                     │
├─────────────────────────────────────────────────────────────┤
│                    Repository Layer                          │
│                   (Data Access)                              │
│         职责: 数据持久化、查询封装、缓存管理                     │
├─────────────────────────────────────────────────────────────┤
│                     Entity Layer                             │
│                   (Domain Model)                             │
│         职责: 数据结构定义、领域行为、业务规则                   │
└─────────────────────────────────────────────────────────────┘
```

## OOP Design Principles

### 1. Abstraction (抽象)

```java
// 定义接口，隐藏实现细节
public interface UserService {
    User findById(Long id);
    User create(CreateUserRequest request);
    void delete(Long id);
}

// 具体实现
public class UserServiceImpl implements UserService {
    @Override
    public User findById(Long id) {
        // 实现细节
    }
}
```

### 2. Encapsulation (封装)

```java
// 实体封装内部状态和行为
public class Order {
    private OrderStatus status;
    private List<OrderItem> items;
    
    // 通过方法暴露行为，而非直接暴露状态
    public void addItem(Product product, int quantity) {
        validateCanModify();
        items.add(new OrderItem(product, quantity));
        recalculateTotal();
    }
    
    public void submit() {
        validateCanSubmit();
        this.status = OrderStatus.SUBMITTED;
    }
    
    private void validateCanModify() {
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException("Cannot modify submitted order");
        }
    }
}
```

### 3. Inheritance & Composition (继承与组合)

```java
// 基类定义通用行为
public abstract class BaseEntity {
    protected Long id;
    protected LocalDateTime createdAt;
    protected LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
}

// 子类继承并扩展
public class User extends BaseEntity {
    private String username;
    private String email;
}

// 组合优于继承
public class OrderService {
    private final OrderRepository orderRepository;  // 组合
    private final PaymentService paymentService;    // 组合
    private final NotificationService notificationService;
}
```

### 4. Polymorphism (多态)

```java
// 策略模式实现多态
public interface PaymentStrategy {
    PaymentResult pay(Order order);
}

public class CreditCardPayment implements PaymentStrategy {
    @Override
    public PaymentResult pay(Order order) {
        // 信用卡支付逻辑
    }
}

public class WechatPayment implements PaymentStrategy {
    @Override
    public PaymentResult pay(Order order) {
        // 微信支付逻辑
    }
}

// 使用时通过接口调用
public class PaymentService {
    public PaymentResult processPayment(Order order, PaymentStrategy strategy) {
        return strategy.pay(order);
    }
}
```

## Layer Communication Rules

### 1. Dependency Direction

```
Controller → Service → Repository → Entity
     ↓           ↓           ↓
    DTO        DTO/Entity   Entity
```

- 上层依赖下层，下层不依赖上层
- 通过接口依赖，不依赖具体实现

### 2. Data Transfer Objects (DTO)

```java
// Request DTO - 接收外部输入
public class CreateUserRequest {
    @NotBlank
    private String username;
    @Email
    private String email;
}

// Response DTO - 返回外部输出
public class UserResponse {
    private Long id;
    private String username;
    private String email;
    private LocalDateTime createdAt;
    
    public static UserResponse from(User user) {
        // Entity → DTO 转换
    }
}

// 内部 DTO - 层间传递
public class UserDTO {
    // 服务层内部使用
}
```

### 3. Exception Handling

```java
// 基础异常类
public abstract class BaseException extends RuntimeException {
    private final String errorCode;
    private final String message;
}

// 业务异常
public class BusinessException extends BaseException {
    public BusinessException(String errorCode, String message) {
        super(errorCode, message);
    }
}

// 全局异常处理
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse(e.getErrorCode(), e.getMessage()));
    }
}
```

## Frontend Layer Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                      View Layer                              │
│                   (Pages / Components)                       │
│              职责: UI渲染、用户交互、事件处理                    │
├─────────────────────────────────────────────────────────────┤
│                     Store Layer                              │
│                   (State Management)                         │
│              职责: 状态管理、状态派生、状态持久化                 │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer                             │
│                  (Business Logic)                            │
│              职责: 业务逻辑封装、数据转换、缓存                   │
├─────────────────────────────────────────────────────────────┤
│                      API Layer                               │
│                   (HTTP Client)                              │
│              职责: HTTP请求、响应处理、错误处理                   │
└─────────────────────────────────────────────────────────────┘
```

## Cross-Module Communication

```
┌──────────────┐     ┌──────────────┐
│ Client Side  │     │ Admin Side   │
├──────────────┤     ├──────────────┤
│   Frontend   │     │   Frontend   │
│      ↓       │     │      ↓       │
│   Backend    │←───→│   Backend    │
└──────────────┘     └──────────────┘
        ↓                   ↓
   ┌─────────────────────────────┐
   │      Shared Database        │
   │      Message Queue          │
   │      Shared Services        │
   └─────────────────────────────┘
```
