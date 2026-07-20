# Linkship 🚀

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A scalable, production-ready URL shortener with deep analytics, QR code generation, and geolocation tracking — built with Django.**

[Live Demo](https://your-live-url.railway.app) · [API Docs](https://your-live-url.railway.app/api/docs/) · [Report Bug](https://github.com/Abitesh/Linkship/issues)

</div>

---

## 📸 Preview

> _(Add a screenshot or GIF of your dashboard here — drag & drop an image into this file on GitHub)_

---

## 📋 Table of Contents

- [Features](#-core-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Local Setup](#-local-setup)
- [Docker Setup](#-docker-setup)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)

---

## ✨ Core Features

| Feature | Description |
|---|---|
| 🔗 **Link Shortening** | Generate random short codes or custom human-readable aliases |
| 📊 **Deep Analytics** | Track clicks, device types, browsers, OS, and referrer sources |
| 🌍 **Geolocation Tracking** | Map user locations per click using GeoLite2 IP database |
| 📷 **QR Code Generation** | Auto-generate downloadable QR codes for every shortened link |
| 👤 **User Profiles** | Full authentication with customizable profiles and avatars |
| 🔐 **JWT API Auth** | Secure REST API with JSON Web Token authentication |
| ⚡ **Async Tasks** | Non-blocking analytics processing via Celery + Redis |

---

## 📊 System Architecture

```mermaid
flowchart LR
    Client([🌐 Client / Browser]) --> LB[Railway Load Balancer]

    subgraph Cloud ["☁️ Railway.app Cloud Environment"]
        LB --> Web[🐍 Django Web Server]
        Web <--> DB[(🐘 PostgreSQL Database)]
        Web <--> Redis[(⚡ Redis Cache / Broker)]
        Redis <--> Worker[🔄 Celery Background Worker]
        Worker <--> DB
        Web --> GeoDB[(🗺️ GeoLite2 IP Database)]
    end

    style Cloud fill:#0d1117,stroke:#30363d,color:#c9d1d9
```

**Request lifecycle:**
1. Client hits the Railway load balancer
2. Django handles the redirect and logs the raw click event
3. Celery worker asynchronously processes analytics (device, browser, geo lookup)
4. Results are cached in Redis and persisted to PostgreSQL

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 4.x, Django REST Framework |
| **Database** | PostgreSQL 16 |
| **Cache / Queue** | Redis 7, Celery |
| **Frontend** | Bootstrap 5, Crispy Forms |
| **Auth** | JWT via `djangorestframework-simplejwt` |
| **Geolocation** | GeoLite2 (MaxMind) |
| **QR Codes** | `qrcode` Python library |
| **Infrastructure** | Docker, Docker Compose, Railway |
| **API Docs** | drf-spectacular (Swagger / ReDoc) |

---

## 📁 Project Structure
Linkship/
├── analytics/ # Click tracking models, views, signals
├── config/
│ ├── settings/
│ │ ├── base.py # Shared settings
│ │ ├── dev.py # Development overrides
│ │ └── prod.py # Production overrides
│ └── urls.py # Root URL configuration
├── core/ # Shared utilities, base models
├── geo/ # GeoLite2 IP lookup integration
├── links/ # URL shortening logic, models, API views
├── users/ # Auth, profiles, avatars
├── Dockerfile
├── docker-compose.yml
├── Procfile # Railway / Heroku process config
└── requirements.txt


---

## 💻 Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL running locally (or use Docker)
- Redis running locally (or use Docker)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/Abitesh/Linkship.git
cd Linkship
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Copy the example env file and fill in your values:
```bash
cp .env.example .env
```
See the [Environment Variables](#-environment-variables) section for all required keys.

**5. Run migrations and start**
```bash
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

**6. Start the Celery worker** _(in a separate terminal)_
```bash
celery -A config worker --loglevel=info
```

App will be live at `http://127.0.0.1:8000` 🎉

---

## 🐳 Docker Setup

The fastest way to get the full stack (Django + PostgreSQL + Redis + Celery) running with a single command:

```bash
docker-compose up --build
```

This spins up all four services as defined in `docker-compose.yml`. The web server will be available at `http://localhost:8000`.

To stop all services:
```bash
docker-compose down
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root with these keys:

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True                        # Set False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/linkship_db

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# GeoLite2 (download from MaxMind)
GEOIP_PATH=/path/to/GeoLite2-City.mmdb
```

> ⚠️ Never commit your `.env` file. It's already listed in `.gitignore`.

---

## 📖 API Documentation

Linkship ships with a fully interactive **Swagger UI** powered by `drf-spectacular`.

| Endpoint | Description |
|---|---|
| `GET /api/docs/` | Interactive Swagger UI |
| `GET /api/redoc/` | Alternative ReDoc UI |
| `GET /api/schema/` | Raw OpenAPI 3.0 schema (JSON/YAML) |

### Key API Endpoints
POST /api/auth/token/ → Obtain JWT token pair
POST /api/auth/token/refresh/ → Refresh access token

POST /api/links/ → Create a shortened link
GET /api/links/ → List all links for authenticated user
GET /api/links/{short_code}/ → Get link details
DELETE /api/links/{short_code}/ → Delete a link

GET /api/links/{short_code}/analytics/ → Get click analytics


> Start the server and visit [`http://127.0.0.1:8000/api/docs/`](http://127.0.0.1:8000/api/docs/) to explore and test all endpoints interactively.

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

---

## 👤 Author

**Abitesh** · [GitHub](https://github.com/Abitesh)

---

<div align="center">
⭐ If you found this project useful, consider giving it a star!
</div>