# Tap2Cart

A FastAPI-based e-commerce backend project with async database support and Alembic migrations for database versioning.

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Tap2Cart
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚡ Database Setup & Alembic Migrations

### 1. Initialize Alembic (if migrations folder not present)

```bash
alembic init migrations
```

### 2. Configure `alembic.ini`

* Open `alembic.ini` and set:

```ini
sqlalchemy.url = %(DATABASE_URL)s
```

### 3. Update `.env` file

Ensure the `.env` file contains the correct database URL:

```env
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/ecom"
```

### 4. Configure `migrations/env.py` for async database

```python

from app.core.database import Base
import app.models
from app.config import settings

# Use sync driver for Alembic
sync_url = settings.database_url.replace("asyncpg", "psycopg2")
config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata
```

### 5. Generate migrations

```bash
alembic revision --autogenerate -m "init"
```

### 6. Apply migrations

```bash
alembic upgrade head
```

---

## ⚡ Seed the Database

Example:

```bash
GET api/v1/products/seed-db
```

Populates the database with default data

NB. Make sure the server is running


## 🔄 Future Workflow

* **Generate new migration after model changes**

```bash
alembic revision --autogenerate -m "added new table"
```

* **Apply migrations**

```bash
alembic upgrade head
```

* **Rollback last migration**

```bash
alembic downgrade -1
```

* **View migration history**

```bash
alembic history
```

---

## 🚀 Run the Application

```bash
uvicorn runserver:app --reload
```

* The API will be available at: `http://127.0.0.1:8000`
* For production, use a proper ASGI server setup (e.g., Gunicorn + Uvicorn workers).

---

## 📦 Notes

* The project uses **asyncpg** for async database operations.
* Alembic migrations run using a synchronous driver (`psycopg2`) for compatibility.
