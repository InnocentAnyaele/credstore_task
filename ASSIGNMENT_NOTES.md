# Assignment Notes: Product Verification System

## Architecture Overview

This implementation strictly follows a layered clean architecture pattern:

```
API Layer (FastAPI Routers)
    ↓
Use Case Layer (Orchestration)
    ↓
Application Service Layer (Business Operations)
    ↓
Domain Layer (Business Logic & Rules)
    ↓
Infrastructure Layer (Repositories & Adapters)
```

## Layer Responsibilities

### 1. API Layer (`src/api/`)
- **Purpose**: HTTP request/response mapping only
- **Files**:
  - `router.py`: FastAPI route handlers
  - `schemas.py`: Pydantic request/response models
  - `container.py`: Dependency injection container
  - `app.py`: FastAPI application setup

**Key Design Decision**: Routers never call repositories or services directly. They only call use cases and map domain objects to API responses.

### 2. Use Case Layer (`src/use_cases/`)
- **Purpose**: Orchestrate workflows and manage transaction boundaries
- **Files**:
  - `create_product.py`: CreateProductUseCase
  - `verify_product.py`: VerifyProductUseCase
  - `get_product.py`: GetProductUseCase

**Key Design Decision**: Use cases own the UnitOfWork transaction boundary and coordinate between services. They dispatch domain events after successful commits. No HTTP concerns exist at this layer.

### 3. Application Service Layer (`src/application/`)
- **Purpose**: Business operations and domain coordination
- **Files**:
  - `product_service.py`: ProductService

**Key Design Decision**: Services perform specific business operations like creating products and evaluating verifications. They work with domain entities and repositories but have no knowledge of HTTP or persistence details.

### 4. Domain Layer (`src/domain/`)
- **Purpose**: Core business logic, rules, and entities
- **Files**:
  - `product.py`: Product entity with state machine
  - `verification_policy.py`: Verification rules and evaluation logic
  - `repositories.py`: Repository interfaces (abstractions)
  - `event_dispatcher.py`: Event dispatcher interface and implementation

**Key Design Decision**: 
- Product entity enforces state transition rules (pending_verification → active/rejected)
- Verification policy encapsulates all verification rules as a domain policy object
- Domain events capture important business events
- No infrastructure dependencies in this layer

### 5. Infrastructure Layer (`src/infrastructure/`)
- **Purpose**: External system adapters and persistence
- **Files**:
  - `mysql_models.py`: SQLAlchemy ORM models
  - `mysql_repository.py`: MySQL implementation of ProductRepository
  - `mongo_repository.py`: MongoDB implementation of VerificationRepository
  - `unit_of_work.py`: Transaction coordinator across databases

## MySQL vs MongoDB Storage Strategy

### MySQL (Relational)
**What is stored**:
- Core product record: id, name, price, currency, category, stock_quantity, assets, status
- Timestamps: created_at, updated_at

**Why MySQL**:
- Transactional integrity for product state
- Strong consistency requirements
- Structured, predictable schema
- Primary source of truth for product existence and status

### MongoDB (Document)
**What is stored**:
- Verification records: product_id, checks (dictionary), reasons (list), verified_at
- Flexible verification metadata

**Why MongoDB**:
- Flexible schema for verification check results
- Semi-structured data (checks can vary)
- Append-only audit trail of verification attempts
- No need for immediate consistency with product record
- Natural fit for storing variable validation reasons

## State Machine Implementation

Product status follows strict state transitions:

```
[pending_verification] → [active]     (verification passed)
[pending_verification] → [rejected]   (verification failed)
```

Invalid transitions throw `ValueError`. This is enforced in the Product entity's `transition_to_active()` and `transition_to_rejected()` methods.

## Verification Rules

The `ProductVerificationPolicy` evaluates six checks:

1. **name present**: Name must not be empty
2. **category present**: Category must not be empty
3. **currency present**: Currency must not be empty
4. **price > 0**: Price must be positive
5. **stock_quantity >= 0**: Stock cannot be negative
6. **At least 1 asset**: Assets list must have at least one item

If ANY check fails, status becomes `rejected` and reasons are stored in MongoDB.

## Event Dispatcher Design

**Implementation**: `InMemoryEventDispatcher`

**Features**:
- Logs events to console
- Stores events in-memory list for testing
- Injected via dependency injection container
- Async-compatible interface

**Design Rationale**:
- Simple to test (no external dependencies)
- Easy to swap with real message queue (RabbitMQ, Kafka, SQS) later
- Follows dependency inversion principle via EventDispatcher interface
- Events dispatched AFTER successful commit to prevent inconsistencies

## UnitOfWork Pattern

Coordinates transactions across MySQL and MongoDB:

```python
async with uow:
    # Work with repositories
    await uow.products.save(product)
    await uow.verifications.save_verification(...)
    await uow.commit()  # Commits MySQL transaction
```

**Design Trade-off**: MongoDB operations happen immediately (no transaction support in free tier), but UnitOfWork provides consistent interface and rollback capability for MySQL.

## Dependency Injection

The `Container` class manages all dependencies:

- Database connections (MySQL engine, MongoDB client)
- Repository instantiation
- Event dispatcher singleton
- Use case creation with injected dependencies

This enables:
- Easy testing with mock dependencies
- Configuration management
- Lifecycle control (startup/shutdown)

## Testing Strategy

### Unit Tests (`tests/test_verification_policy.py`)
- Test verification logic in isolation
- Cover all success and failure scenarios
- No database dependencies
- Fast execution

### Integration Tests (`tests/test_integration.py`)
- Test full create → verify → get flow
- Exercise all layers together
- Use real HTTP client (httpx)
- Verify end-to-end behavior

## Key Assumptions and Trade-offs

### Assumptions
1. Product verification is immediate (not async background job)
2. Product data contains category/stock/assets even though not in API response
3. Verification can be attempted multiple times (stores each attempt in Mongo)
4. Events are fire-and-forget (no retry logic)

### Trade-offs
1. **MySQL + MongoDB complexity**: Adds operational overhead but demonstrates intentional use of both databases
2. **Event dispatcher simplicity**: In-memory implementation trades durability for simplicity
3. **Repository granularity**: Separate repositories for Product and Verification trades simplicity for separation of concerns
4. **Synchronous verification**: Simpler but blocks request; async verification would require job queue
5. **No caching layer**: Direct database access trades performance for consistency

## Running the Application

### Prerequisites
```bash
docker-compose up -d
pip install -r requirements.txt
```

### Start Server
```bash
python main.py
```

### Run Tests
```bash
pytest -v
```

### API Example Flow
```bash
# 1. Create product (status: pending_verification)
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15",
    "price": 999.99,
    "currency": "USD",
    "category": "Electronics",
    "stock_quantity": 50,
    "assets": ["image1.jpg"]
  }'

# Response: {"product_id": "...", "status": "pending_verification", ...}

# 2. Verify product (checks pass → status: active)
curl -X POST http://localhost:8000/api/v1/products/{product_id}/verify

# Response: {"product_id": "...", "status": "active", ...}

# 3. Get product
curl http://localhost:8000/api/v1/products/{product_id}
```

## Architecture Validation

**No business logic in routers**: Routers only map requests to use case calls
**No repository calls from routers**: All repository access via use cases
**Use cases exist as distinct layer**: Separate folder with clear orchestration responsibility  
**Tests included**: Unit tests for verification logic, integration tests for workflows
**Status starts as pending_verification**: Enforced in Product entity constructor
**MySQL + MongoDB integration**: Intentional separation of concerns
**Event dispatcher with DI**: Interface-based design with injectable implementation
**State transitions enforced**: Domain entity guards invalid state changes

## Project Structure
```
product_verification/
├── src/
│   ├── api/              # API Layer
│   ├── use_cases/        # Use Case Layer
│   ├── application/      # Application Service Layer
│   ├── domain/           # Domain Layer
│   └── infrastructure/   # Infrastructure Layer
├── tests/
│   ├── test_verification_policy.py   # Unit tests
│   └── test_integration.py           # Integration tests
├── docker-compose.yml    # Database containers
├── requirements.txt      # Dependencies
├── main.py              # Entry point
└── README.md            # Setup instructions
```
