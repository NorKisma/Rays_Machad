# Rays Madrasah SaaS Transformation Roadmap

Converting a single-tenant application into a SaaS (Multi-Tenant) platform requires moving from a logic where everyone shares one database to a logic where multiple "Tenants" (Madrasahs) are isolated from each other.

---

## 🛠️ Step 1: Choose Your Architecture

There are two main ways to convert this specific Flask app into a SaaS:

### Option A: Database-per-Tenant (Isolated & Secure)
*The app detects the subdomain (e.g., `alnoor.raystechcenter.online`) and connects to `madrasah_alnoor` database.*
- **Best for:** High security, easy backups for individual schools.
- **Effort:** Medium. Requires a "Master Database" to track tenants.

### Option B: Shared Database (Scalable & Cost-Effective)
*One database for everyone. Every table gets a `tenant_id` column.*
- **Best for:** Small schools, low server costs, massive scale.
- **Effort:** High. Every single database model and query must be updated.

---

## 🚀 Step 2: Implementation (Option A - Recommended)

### 1. The "Master" Database
Create a new database called `madrasah_master`. This will store:
- **Tenants Table**: `id`, `name`, `subdomain`, `db_connection_string`, `is_active`.
- **Subscriptions Table**: Billing status, expiry date.

### 2. Middleware for Dynamic DB Switching
In `app/extensions.py` and `app/__init__.py`, you need to modify how the database is connected. Instead of a fixed string in `.env`, the app should:
1. Capture the request hostname.
2. Look up the tenant in the **Master DB**.
3. Set the `SQLALCHEMY_DATABASE_URI` dynamically for that request.

**Example Logic:**
```python
@app.before_request
def identify_tenant():
    host = request.host.split(':')[0] # e.g., madrasah1.com
    tenant = MasterDB.query.filter_by(domain=host).first()
    if tenant:
        current_app.config['SQLALCHEMY_DATABASE_URI'] = tenant.db_url
```

### 3. Centralized Gunicorn / Single Socket
Instead of running 10 different Gunicorn processes (which uses a lot of RAM), you run **one** process that handles all tenants by switching the database context on the fly.

---

## 📦 Step 3: Global SaaS Features

### 1. The "Super Admin" Dashboard
A dedicated URL (like `admin.raystechcenter.online`) where YOU (RaysTech) can:
- Create a new Madrasah.
- Terminate access if they don't pay.
- View global statistics (total students across all schools).

### 2. Automatic Provisioning Script
Create a script (e.g., `scripts/provision_tenant.py`) that:
1. Creates a new database: `CREATE DATABASE madrasah_[name]`.
2. Runs `flask db upgrade` on that specific DB.
3. Seeds the initial admin user for that school.
4. Adds the entry to the Master Database.

---

## 💰 Step 4: Monetization (The "S" in SaaS)
- **Whitelabeling:** Allow schools to use their own domains (e.g., `portal.alnoor.edu`).
- **Billing Integration:** Add Stripe or local payment gateways to the "Master" level to automate monthly/yearly payments.

---

## 🛠️ Immediate Next Steps for your Team:
1. **Decide Architecture:** Do you prefer individual databases (Security) or a shared database (Cost)?
2. **Setup Domain Wildcards:** Configure your DNS so that `*.raystechcenter.online` points to your server IP.
3. **Master DB Creation:** Start by creating a separate table for "Companies" or "Organizations".
