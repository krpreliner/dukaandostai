# DukaanDost AI - Authentication & Multi-Tenant RBAC Guide

## 1. Overview

DukaanDost AI features an enterprise-grade multi-tenant authentication and authorization system built with JSON Web Tokens (JWT), bcrypt password hashing, and Role-Based Access Control (RBAC).

Each user can create or be invited to multiple store workspaces (e.g., Sharma General Store Ranchi, Branch 2 Dhanbad). All business data is strictly isolated by `store_id`.

---

## 2. Token Specifications

| Parameter | Access Token | Refresh Token |
| :--- | :--- | :--- |
| **Algorithm** | HMAC-SHA256 (`HS256`) | HMAC-SHA256 (`HS256`) |
| **Default Lifetime** | 1,440 minutes (24 hours) | 7 days |
| **Claims** | `sub` (email), `user_id`, `type: "access"`, `exp` | `sub` (email), `user_id`, `type: "refresh"`, `exp` |
| **Storage (Client)** | In-memory React AuthContext + `localStorage` | `localStorage` |
| **Header Transport** | `Authorization: Bearer <TOKEN>` | Body payload in `/api/auth/refresh` |

---

## 3. Multi-Tenant Tenancy Model

The database represents tenancy via three relational models:

1. **`User`**: Account identity (email, hashed password, full name, active status).
2. **`Store`**: A distinct retail store entity (`store_id`, `name`, `location`, `owner_name`, `created_at`).
3. **`StoreMember`**: Association table mapping `User` to `Store` with an assigned `role`.

```
+------------+       1:N       +-----------------+       N:1       +-------------+
|    User    | <-------------> |   StoreMember   | <-------------> |    Store    |
| (email, pwd)                 |  (role, joined) |                 | (store_id)  |
+------------+                 +-----------------+                 +-------------+
```

---

## 4. Role-Based Access Control (RBAC) Matrix

| Capability / Resource | OWNER | MANAGER | STAFF | VIEWER |
| :--- | :---: | :---: | :---: | :---: |
| **View Dashboard & Financial Overview** | Yes | Yes | Yes | Yes |
| **View Product Catalog & Customer List** | Yes | Yes | Yes | Yes |
| **View AI Agent Plans & Insights** | Yes | Yes | Yes | Yes |
| **Trigger Autonomous Growth Run** | Yes | Yes | No | No |
| **Approve / Reject Sensitive Actions** | Yes | Yes | No | No |
| **Update Product Prices Manually** | Yes | Yes | Yes | No |
| **Import Catalog via Google Sheets CSV** | Yes | Yes | No | No |
| **Configure AI Providers & API Keys** | Yes | No | No | No |
| **Add / Remove Store Team Members** | Yes | Yes | No | No |
| **Delete Store Workspace** | Yes | No | No | No |

---

## 5. API Endpoints

### 5.1 `POST /api/auth/register`
Creates a new user and automatically establishes their first store workspace with the `OWNER` role.
```json
{
  "email": "sharma.ji@sharmastore.com",
  "password": "SharmaStore2026!",
  "full_name": "Sharma Ji",
  "store_name": "Sharma General Store",
  "store_location": "Ranchi, Jharkhand"
}
```

### 5.2 `POST /api/auth/login`
Validates credentials and returns JWT access and refresh tokens, user profile, and accessible store workspaces.
```json
{
  "email": "owner@sharmastore.com",
  "password": "SharmaStore2026!"
}
```

### 5.3 `GET /api/auth/me`
Returns authenticated user identity and all store workspaces they belong to.
Header required: `Authorization: Bearer <TOKEN>`.

### 5.4 `POST /api/auth/refresh`
Exchanges a valid refresh token for a fresh access token without requiring re-entry of passwords.

### 5.5 `GET /api/auth/stores/{store_id}/members`
Lists all authorized team members for the specified store workspace.

### 5.6 `POST /api/auth/stores/{store_id}/members`
Assigns a registered user to a store workspace with an RBAC role (`OWNER`, `MANAGER`, `STAFF`, `VIEWER`). Restricted to `OWNER` or `MANAGER`.

---

## 6. Pre-Configured Demo Credentials

For immediate evaluation without manual registration, the database is pre-seeded with:

- **Email:** `owner@sharmastore.com`
- **Password:** `SharmaStore2026!`
- **Store Name:** Sharma General Store
- **Store ID:** `STORE_001`
- **Role:** `OWNER`
