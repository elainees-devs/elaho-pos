# 📦 ElahoPOS

## Overview

ElahoPOS is an offline-first Point of Sale (POS) and inventory management system designed for small and medium-sized businesses across Kenya and Africa.

The platform helps business owners manage inventory, track sales, monitor expenses, manage suppliers and customers, and generate business reports even in areas with unreliable internet connectivity.

ElahoPOS is being built with a focus on:

* Offline-first functionality
* Inventory management
* Sales tracking
* Expense management
* Business reporting
* eTIMS-ready architecture
* Mobile and desktop accessibility

---

## 🎯 Vision

To provide affordable, reliable, and easy-to-use business management software for African SMEs.

Many businesses still rely on paper records, notebooks, spreadsheets, or disconnected systems. ElahoPOS aims to simplify daily operations while preparing businesses for digital compliance and growth.

---

## ✨ Key Features

### 📦 Inventory Management

* Product catalog management
* Stock-in and stock-out tracking
* Low-stock alerts
* Category management
* Supplier tracking

### 🧾 Sales Management

* Create and manage sales transactions
* Generate receipts
* Track payment methods (Cash, M-Pesa, Credit)
* Daily sales summaries
* Sales history

### 💰 Expense Tracking

* Record business expenses
* Categorize expenses
* Generate expense reports

### 👥 Customer Management

* Store customer information
* Track customer purchases
* Manage contractor and fundi accounts

### 📊 Reporting

* Daily sales reports
* Weekly and monthly reports
* Profit analysis
* Inventory valuation

### 📡 Offline-First Support

* Full functionality without internet
* Local data storage (IndexedDB via Dexie.js)
* Automatic sync when connectivity is restored

---

## 🔮 Future Features

* M-Pesa Integration
* Barcode Scanning
* Credit Sales Management
* Multi-Branch Support
* Multi-Tenant SaaS Architecture
* eTIMS Integration
* Purchase Orders
* Supplier Management Portal

---

## 🛠️ Technology Stack

### Frontend

* React
* TypeScript
* Tailwind CSS
* React Query
* Dexie.js (IndexedDB)

### Backend

* Django
* Django REST Framework
* PostgreSQL

### Infrastructure

* Docker
* Nginx
* Gunicorn
* VPS Hosting

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** v18+ and **npm** / **yarn**
- **Python** 3.11+ and **pip** / **uv**
- **Django** 5+ and **Django REST Framework**
- **PostgreSQL** 15+
- **Docker** & **Docker Compose** (optional, for containerized setup)

### Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/yourusername/elahopos.git
cd elahopos

# Copy environment file and adjust as needed
cp .env.example .env

# Start all services
docker compose up --build
```

The app will be available at `http://localhost:3000` (frontend) and `http://localhost:8000` (API).

### Manual Development Setup

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed sample data (optional)
python manage.py seed_db

# Start dev server
python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

#### Sync Service (optional)

```bash
cd sync-service

# Requires Redis running locally or via Docker
python worker.py
```

### Database Setup

Create a PostgreSQL database and update the `DATABASE_URL` in your `.env`:

```env
DATABASE_URL=postgres://user:password@localhost:5432/elahopos
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Verify Installation

- Frontend: open `http://localhost:5173`
- API health check: `curl http://localhost:8000/api/health/`
- Admin panel: `http://localhost:8000/admin/`

---

## 🧠 Architecture

The ElahoPOS system follows a local-first, offline-capable architecture where the browser acts as the primary execution layer and the backend acts as the system of record.

The full system design and technical documentation is split into dedicated modules:

📚 System Documentation

All architecture details are documented in the /docs folder:

🧠 System Architecture → [docs/architecture.md](docs/architecture.md)
🔄 Sync Engine Design → [docs/sync-engine.md](docs/sync-engine.md)
🌐 API Specification → [docs/api-spec.md](docs/api-spec.md)
🗄️ Database Design (ERD) → [docs/erd.md](docs/erd.md)
🚀 Deployment Guide → [docs/deployment.md](docs/deployment.md)



---

## 📁 Project Structure

```
elahopos/
│
├── README.md
├── docker-compose.yml
├── .env
├── .gitignore
├── Makefile
│
├── docs/
│   ├── architecture.md
│   ├── erd.png
│   ├── api-spec.md
│   ├── sync-engine.md
│   └── deployment.md
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── prod.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── users/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── permissions.py
│   │   │   └── services.py
│   │   │
│   │   ├── inventory/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── signals.py
│   │   │
│   │   ├── sales/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   └── receipts.py
│   │   │
│   │   ├── expenses/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── services.py
│   │   │
│   │   ├── customers/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── services.py
│   │   │
│   │   ├── suppliers/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── reports/
│   │   │   ├── analytics.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   │
│   │   ├── sync/
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   ├── queue.py
│   │   │   ├── conflict_resolver.py
│   │   │   └── urls.py
│   │   │
│   │   └── etims/
│   │       ├── models.py
│   │       ├── services.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       └── urls.py
│   │
│   └── shared/
│       ├── models.py
│       ├── utils.py
│       ├── constants.py
│       ├── middleware.py
│       └── exceptions.py
│
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   │
│   ├── public/
│   │   ├── icons/
│   │   ├── manifest.json
│   │   └── offline.html
│   │
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   │
│   │   ├── routes/
│   │   │   ├── index.tsx
│   │   │   ├── auth.routes.tsx
│   │   │   ├── dashboard.routes.tsx
│   │   │   └── pos.routes.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── pos/
│   │   │   ├── inventory/
│   │   │   ├── sales/
│   │   │   └── settings/
│   │   │
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   ├── forms/
│   │   │   ├── tables/
│   │   │   ├── charts/
│   │   │   └── pos/
│   │   │
│   │   ├── store/
│   │   │   ├── auth.store.ts
│   │   │   ├── cart.store.ts
│   │   │   ├── inventory.store.ts
│   │   │   └── sync.store.ts
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── inventory.api.ts
│   │   │   ├── sales.api.ts
│   │   │   └── sync.api.ts
│   │   │
│   │   ├── offline/
│   │   │   ├── db.ts
│   │   │   ├── schema.ts
│   │   │   ├── syncEngine.ts
│   │   │   ├── queue.ts
│   │   │   └── conflictResolver.ts
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useCart.ts
│   │   │   ├── useInventory.ts
│   │   │   └── useSync.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   ├── calculations.ts
│   │   │   └── constants.ts
│   │   │
│   │   └── assets/
│   │       ├── images/
│   │       └── fonts/
│   │
│   └── service-worker.ts
│
│
├── sync-service/
│   ├── worker.py
│   ├── queue_processor.py
│   ├── conflict_handler.py
│   ├── redis_client.py
│   └── Dockerfile
│
│
├── nginx/
│   └── default.conf
│
└── scripts/
    ├── setup.sh
    ├── seed_db.py
    └── backup.sh
```

---

## 📊 Database Design

To support offline-first synchronization and audit-safe financial tracking, ElahoPOS uses a **modular relational schema with strong audit trails and UUID-based identity mapping**.

Key relationships:

* Products belong to Categories and Suppliers (1-to-many)
* Sales contain multiple SaleItems (transaction breakdown)
* InventoryLogs track all stock mutations
* ETIMS_Receipts provide a compliance integration layer for tax reporting

---

## 🎯 Project Goals

### Phase 1 – MVP

* Authentication
* Product Management
* Inventory Tracking
* Sales Recording
* Expense Tracking
* Dashboard
* Offline Functionality

### Phase 2

* Supplier Management
* Customer Management
* Purchase Orders
* Credit Sales

### Phase 3

* M-Pesa Integration
* Barcode Support
* Multi-User Permissions
* Multi-Branch Support

### Phase 4

* eTIMS Integration
* Tax Reporting
* SaaS Subscription Management

---

## 🏪 Target Businesses

* Hardware stores
* Electrical shops
* Plumbing stores
* Agrovet shops
* Water refill businesses
* General retail shops
* Building material suppliers
* Small wholesalers

---

## ⚙️ Guiding Principles

### 📡 Offline First

ElahoPOS is designed to operate fully offline using IndexedDB as the primary local store. A background sync engine ensures data consistency with the server once connectivity is restored.

### 🎨 Simple UX

Optimized for fast retail workflows with minimal training required, large touch targets, and clear navigation.

### 📱 Mobile Friendly

Progressive Web App (PWA) that works across smartphones, tablets, and desktops without installation.

### 💰 Affordable for SMEs

Built on open-source technologies with a lightweight architecture to minimize operational costs.

### 🏗️ Scalable Architecture

Modular backend design allowing independent scaling of services such as sync, analytics, and reporting.

### 🔒 Data Security

All transactions are logged immutably with secure API communication and tenant-isolated data models.

### 🇰🇪 Compliance Ready (eTIMS)

Structured to support Kenya Revenue Authority (KRA) eTIMS integration for automated tax compliance.

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Reporting Issues

- Check [existing issues](https://github.com/yourusername/elahopos/issues) before filing a new one.
- Use a clear title and include steps to reproduce, expected vs actual behavior, and screenshots if relevant.

### Submitting Changes

1. Fork the repository and create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes, keeping code style consistent with the existing codebase.
3. Run tests and linting before committing:
   ```bash
   # Backend
   cd backend && python manage.py test

   # Frontend
   cd frontend && npm run lint && npm run typecheck
   ```
4. Write a clear commit message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add stock-in alerts
   fix: resolve sync conflict on duplicate items
   chore: update dependencies
   ```
5. Push your branch and open a Pull Request against `main`.
6. In the PR description, link any related issues and briefly describe your changes.

### Branch Naming

Use the following prefixes for branch names:

| Prefix   | Purpose                          |
|----------|----------------------------------|
| `feat/`  | New feature                      |
| `fix/`   | Bug fix                          |
| `chore/` | Tooling, dependencies, config    |
| `refactor/` | Code refactoring (no behavior change) |
| `docs/`  | Documentation changes            |
| `style/` | Formatting, missing semicolons   |

Examples: `feat/barcode-scanning`, `fix/sync-null-pointer`, `chore/upgrade-react-query`.

---

### Code Style

- **Python** — Follow PEP 8, use type hints, run `ruff` for linting.
- **TypeScript / React** — Follow the existing component patterns, use strict TypeScript.
- **CSS** — Use Tailwind utility classes; avoid custom CSS unless necessary.

---

## 📜 License

This project is under active development.
License will be added before production release.

---

## 👤 Author

**Elaine Muhombe**
Full Stack Developer (React • Django • Python)

Building practical digital systems for African businesses.

---
