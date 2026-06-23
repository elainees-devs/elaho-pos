
---

# 🔄 ElahoPOS Sync Engine Design

## Overview

The ElahoPOS Sync Engine is responsible for maintaining **eventual consistency** between:

* The **client-side offline database (IndexedDB via Dexie.js)**
* The **server-side system of record (PostgreSQL via Django REST API)**

It enables the system to function fully offline while ensuring that all changes are reliably synchronized when connectivity is restored.

---

## 🎯 Core Objectives

The sync engine is designed to:

* Support **offline-first operations**
* Guarantee **eventual consistency**
* Prevent **data loss during network failures**
* Handle **conflicts gracefully**
* Ensure **ordered transaction processing**
* Minimize **network usage via batching**

---

## 🧠 Sync Model

ElahoPOS uses a:

> **Queued Event-Based Sync Model with Conflict Resolution**

All changes are treated as **immutable events** stored locally first, then synchronized.

---

## 🏗️ Sync Architecture

```id="v1qk2a"
React PWA (User Action)
        ↓
IndexedDB (Dexie Local DB)
        ↓
Sync Queue (Pending Operations)
        ↓
Sync Engine (Client Worker)
        ↓
REST API (Django Backend)
        ↓
PostgreSQL (Source of Truth)
        ↓
Response + Conflict Data
        ↓
Client State Reconciliation
```

---

## 📦 Core Components

### 1. Local Data Store (IndexedDB)

Acts as the **primary database during offline mode**.

Stores:

* Sales transactions
* Inventory updates
* Expense entries
* Customer updates
* Sync queue events

---

### 2. Sync Queue

The Sync Queue stores **all pending operations** that have not yet been confirmed by the server.

Each entry contains:

```ts id="queue-schema"
{
  id: string;
  entity: "sale" | "inventory" | "expense" | "customer";
  operation: "CREATE" | "UPDATE" | "DELETE";
  payload: object;
  timestamp: number;
  retryCount: number;
  status: "pending" | "syncing" | "failed";
}
```

---

### 3. Sync Engine (Client-Side Worker)

The Sync Engine is responsible for:

* Detecting network availability
* Processing queued operations
* Sending batched requests to backend
* Handling retries and failures
* Updating local state after sync

---

### 4. Backend Sync API (Django REST)

Receives batched sync requests:

```
POST /api/sync/
```

Responsibilities:

* Validate incoming operations
* Apply business rules
* Persist to PostgreSQL
* Detect conflicts
* Return sync results

---

### 5. Conflict Resolver

Handles discrepancies between:

* Local state
* Server state

---

## 🔄 Sync Workflow

### Step 1: Offline Operation

Example: A cashier creates a sale.

```id="offline-flow"
User creates sale
      ↓
Saved to IndexedDB immediately
      ↓
Added to Sync Queue
      ↓
UI updates instantly (no server required)
```

---

### Step 2: Network Detection

The sync engine listens for:

* `navigator.onLine`
* periodic heartbeat checks
* service worker network events

---

### Step 3: Batch Sync Request

When online:

```id="batch-sync"
Sync Engine collects queued items
        ↓
Groups by entity type
        ↓
Sends batch request to backend
        ↓
POST /api/sync/
```

Example payload:

```json id="payload"
{
  "device_id": "device-123",
  "operations": [
    {
      "entity": "sale",
      "operation": "CREATE",
      "payload": { ... },
      "timestamp": 1710000000
    },
    {
      "entity": "inventory",
      "operation": "UPDATE",
      "payload": { ... },
      "timestamp": 1710000020
    }
  ]
}
```

---

### Step 4: Backend Processing

The backend:

1. Validates authentication
2. Processes operations in order
3. Applies business logic
4. Writes to PostgreSQL
5. Detects conflicts

---

### Step 5: Response Handling

Example response:

```json id="response"
{
  "success": true,
  "results": [
    {
      "temp_id": "sale-123",
      "status": "synced",
      "server_id": "sale-789"
    },
    {
      "temp_id": "inventory-456",
      "status": "conflict",
      "reason": "stock mismatch",
      "server_version": 5
    }
  ]
}
```

---

### Step 6: Client Reconciliation

The client:

* Marks synced items as complete
* Updates local IDs with server IDs
* Resolves conflicts using rules
* Removes completed items from queue

---

## ⚔️ Conflict Resolution Strategy

Conflicts occur when:

* Same record modified on multiple devices
* Out-of-order sync events
* Stale offline edits

---

### Resolution Rules

#### 1. Last Write Wins (Default)

Based on `updated_at` timestamp.

---

#### 2. Version-Based Control

Each entity includes:

```ts
version: number;
```

If mismatch:

* server rejects update
* client pulls latest version

---

#### 3. Field-Level Merge (Advanced)

Used for:

* inventory adjustments
* non-critical updates

---

#### 4. Manual Resolution (Edge Cases)

Triggered when:

* financial data conflicts
* stock inconsistencies

---

## 🔁 Retry Mechanism

If sync fails:

* Retry up to `n = 5` times
* Exponential backoff strategy:

  * 1s → 2s → 4s → 8s → 16s

After max retries:

* Mark as `failed`
* Keep in queue for manual retry

---

## 📡 Network Strategy

The sync engine uses:

* Online/offline event listeners
* heartbeat polling (fallback)
* service worker sync triggers

---

## 🧾 Data Integrity Guarantees

ElahoPOS ensures:

* No transaction is lost
* No duplicate sync execution
* Idempotent API operations
* Ordered processing per device

---

## 🔐 Security Considerations

* JWT authentication on all sync requests
* Device-level identification (`device_id`)
* Payload validation at API layer
* Rate limiting per tenant
* Audit logging for all synced events

---

## ⚙️ Performance Optimizations

* Batch syncing (reduces API calls)
* Compression of payloads (future enhancement)
* Local write-first UX (instant UI updates)
* IndexedDB indexing for fast queue access

---

## 📈 Scalability Strategy

### Phase 1

* Single sync endpoint
* Monolithic Django backend

---

### Phase 2

* Dedicated sync worker service
* Redis queue integration

---

### Phase 3

* Event-driven architecture
* Kafka/RabbitMQ for sync streams
* Horizontal scaling per tenant

---

## 🔮 Future Enhancements

* Real-time sync (WebSockets)
* Delta sync (only changed fields)
* Conflict visualization UI
* Background sync scheduling API
* Multi-device reconciliation dashboard

---

## 🧠 Summary

The ElahoPOS Sync Engine ensures that:

* The system works fully offline
* All actions are safely queued
* Data is eventually consistent
* Conflicts are detected and resolved
* Businesses never lose transactions

It is the **core reliability layer** of the entire platform.

---
