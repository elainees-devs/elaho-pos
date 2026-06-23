
---

# 🌐 ElahoPOS API Specification

## Overview

The ElahoPOS API is a **REST-based backend service** built using Django REST Framework. It serves as the **system of record** for all business operations including sales, inventory, expenses, customers, and synchronization from offline clients.

The API is designed to support:

* Offline-first sync operations
* Multi-tenant SME businesses
* Secure financial transactions
* Scalable SaaS architecture

---

## Base URL

```
/api/v1/
```

---

## Authentication

### 🔐 JWT Authentication

ElahoPOS uses JWT tokens for secure API access.

### Endpoints

#### Register User

```
POST /auth/register/
```

**Request**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "business_name": "John Hardware"
}
```

**Response**

```json
{
  "message": "User created successfully",
  "user_id": "uuid"
}
```

---

#### Login

```
POST /auth/login/
```

**Request**

```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response**

```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_refresh_token",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "business_id": "uuid"
  }
}
```

---

## 🧾 Core Modules

---

# 📦 1. Inventory API

## Create Product

```
POST /inventory/products/
```

**Request**

```json
{
  "name": "Cement 50kg",
  "sku": "CEM-001",
  "price": 750,
  "stock_quantity": 100,
  "category_id": "uuid",
  "supplier_id": "uuid"
}
```

---

## Get Products

```
GET /inventory/products/
```

**Response**

```json
[
  {
    "id": "uuid",
    "name": "Cement 50kg",
    "price": 750,
    "stock_quantity": 100
  }
]
```

---

## Update Product

```
PATCH /inventory/products/{id}/
```

---

## Delete Product

```
DELETE /inventory/products/{id}/
```

---

## Stock Movement Log

```
GET /inventory/logs/
```

Tracks:

* stock-in
* stock-out
* adjustments

---

# 🧾 2. Sales API

## Create Sale

```
POST /sales/
```

**Request**

```json
{
  "customer_id": "uuid",
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "price": 750
    }
  ],
  "payment_method": "M-PESA",
  "total_amount": 1500
}
```

---

## Get Sales

```
GET /sales/
```

---

## Get Single Sale

```
GET /sales/{id}/
```

---

## Sales Receipt

```
GET /sales/{id}/receipt/
```

Returns printable receipt data.

---

# 💰 3. Expenses API

## Create Expense

```
POST /expenses/
```

```json
{
  "category": "Transport",
  "amount": 500,
  "description": "Stock delivery"
}
```

---

## Get Expenses

```
GET /expenses/
```

---

# 👥 4. Customers API

## Create Customer

```
POST /customers/
```

```json
{
  "name": "Mary Wanjiku",
  "phone": "0712345678"
}
```

---

## Get Customers

```
GET /customers/
```

---

## Customer Purchase History

```
GET /customers/{id}/sales/
```

---

# 🚚 5. Suppliers API

## Create Supplier

```
POST /suppliers/
```

---

## Get Suppliers

```
GET /suppliers/
```

---

# 📊 6. Reports API

## Daily Sales Report

```
GET /reports/daily/
```

## Monthly Report

```
GET /reports/monthly/
```

## Profit Summary

```
GET /reports/profit/
```

---

# 🔄 7. Sync API (CORE SYSTEM)

This is the **most important endpoint in the entire system**.

---

## Sync Batch Endpoint

```
POST /sync/
```

### Purpose:

Handles offline-to-online data synchronization.

---

### Request

```json
{
  "device_id": "device-123",
  "operations": [
    {
      "entity": "sale",
      "operation": "CREATE",
      "payload": {
        "total": 1000,
        "items": []
      },
      "timestamp": 1710000000
    },
    {
      "entity": "inventory",
      "operation": "UPDATE",
      "payload": {
        "product_id": "uuid",
        "stock_change": -2
      },
      "timestamp": 1710000020
    }
  ]
}
```

---

### Response

```json
{
  "status": "success",
  "results": [
    {
      "temp_id": "op-1",
      "status": "synced",
      "server_id": "sale-789"
    },
    {
      "temp_id": "op-2",
      "status": "conflict",
      "reason": "stock mismatch",
      "server_version": 4
    }
  ]
}
```

---

## Sync Rules

* Idempotent operations (safe retries)
* Ordered processing per device
* Conflict detection enabled
* Partial success allowed

---

# 🧾 8. ETIMS (Tax Compliance Module)

## Generate Tax Invoice

```
POST /etims/invoices/
```

## Get Invoice History

```
GET /etims/invoices/
```

---

# 🔐 9. Users API

## Get Profile

```
GET /users/me/
```

## Update Profile

```
PATCH /users/me/
```

---

# 🧠 Error Handling

## Standard Error Format

```json
{
  "error": true,
  "message": "Invalid request",
  "code": "INVALID_INPUT"
}
```

---

## Common Status Codes

| Code | Meaning      |
| ---- | ------------ |
| 200  | Success      |
| 201  | Created      |
| 400  | Bad Request  |
| 401  | Unauthorized |
| 403  | Forbidden    |
| 404  | Not Found    |
| 409  | Conflict     |
| 500  | Server Error |

---

# 🔒 Security Design

* JWT Authentication
* Role-Based Access Control (RBAC)
* Multi-tenant isolation (business-level separation)
* HTTPS-only communication
* Request validation at service layer

---

# ⚙️ Performance Considerations

* Batch sync reduces API load
* Pagination on all list endpoints
* Indexed database queries (PostgreSQL indexes)
* Stateless API design for horizontal scaling

---

# 📈 Scalability Design

### Phase 1

* Single Django monolith
* REST API + PostgreSQL

### Phase 2

* Redis queue for sync processing
* Background workers

### Phase 3

* Microservices split (sync, reporting, billing)
* Multi-region deployment

---

# 🧠 Summary

The ElahoPOS API is designed to be:

* Offline-sync compatible
* Secure and multi-tenant
* Lightweight for SMEs
* Scalable into SaaS architecture
* Fully aligned with POS business workflows

---
