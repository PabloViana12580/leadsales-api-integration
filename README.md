# 🌀 Lead Sales API Integration with Django

This is a Django-based web application that integrates with the [LeadSales](https://leadsales.io) API to fetch and display sales data in a structured, user-friendly format.

---

## 📦 Features

- 🔄 Fetches and displays:
  - Funnels
  - Stages
  - Leads in each stage
- 🎛️ Dynamically generates buttons for each funnel
- 🗂️ Loads data into Django models
- 🔐 Uses `.env` for secure API token and database settings

---

## 🚀 Getting Started

### 1. 📥 Clone the Repository

```bash
git clone https://github.com/your-username/lead-sales-api-django.git
cd lead-sales-api-django
```

---

### 2. 🧪 Set Up the Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. 🛠️ Create Your `.env` File

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=DJANGO_SECRET_KEY
DEBUG=DEBUG

DB_NAME=DB_NAME
DB_USER=DB_USER
DB_PASSWORD=DB_PASSWORD
DB_HOST=DB_HOST
DB_PORT=DB_PORT
WORKSPACE_ID=WORKSPACE_ID
PUBLISHABLE_KEY=PUBLISHABLE_KEY
SECRET_KEY=SECRET_KEY
```

---

### 4. 🐘 Install and Configure PostgreSQL (Linux/Kali)

#### ✅ Install PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### ✅ Verify Installation

```bash
which psql
```

#### ✅ Start PostgreSQL (version 17 in this case)

```bash
sudo systemctl start postgresql@17-main
```

#### ✅ Check Status

```bash
sudo systemctl status postgresql@17-main
```

#### ✅ Open Postgres Shell

```bash
sudo -u postgres psql -p 5433
```

> ⚠️ Use the correct port shown by `pg_lsclusters`, typically 5433 for PostgreSQL 17.

#### ✅ Create Database & User

Inside the `psql` shell:

```sql
CREATE DATABASE leadsales_db;
CREATE USER leadsales_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE leadsales_db TO leadsales_user;
\q
```

---

### 5. 🧬 Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6. ✅ Run the Server

```bash
python manage.py runserver
```

---

## 📂 Project Structure

```
lead-sales-api-django/
├── app/
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

---

## 🔐 Environment Variables Reference

| Key                 | Description                          |
| ------------------- | ------------------------------------ |
| `SECRET_KEY`        | Django secret key                    |
| `DB_NAME`           | PostgreSQL database name             |
| `DB_USER`           | PostgreSQL user                      |
| `DB_PASSWORD`       | PostgreSQL password                  |
| `DB_HOST`           | PostgreSQL host (default: localhost) |
| `DB_PORT`           | PostgreSQL port (e.g. 5433)          |
| `LEADSALES_API_KEY` | API token for LeadSales              |
| `DEBUG`             | Django debug mode (True/False)       |
