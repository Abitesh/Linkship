# Linkship 🚀

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-Async-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![Tests](https://img.shields.io/badge/Tests-11%2F11_Passing-brightgreen?style=for-the-badge)](#-testing)

**A highly scalable, production-ready URL shortener featuring async background processing, deep click analytics, QR code generation, and geolocation tracking.**

[Live Demo](https://linkship-production.up.railway.app) · [API Docs](https://linkship-production.up.railway.app/api/docs/) · [Report Bug](https://github.com/Abitesh/Linkship/issues)

</div>

---

## 📖 Why Linkship? (Project Overview)

Long, complex URLs are difficult to share, impossible to remember, and offer zero visibility into user engagement. 

**Linkship** solves this by converting cumbersome links into clean, branded short-codes while silently gathering enterprise-grade analytics in the background. Built with a focus on **high throughput and low latency**, Linkship utilizes caching and asynchronous task queues to ensure that users are redirected instantly, without being delayed by heavy database writes or geographic IP lookups.

---

## 📸 Dashboard & Interface

<div align="center">
  <img width="800" alt="Linkship Dashboard" src="https://github.com/user-attachments/assets/92a9d649-2b8d-4588-b101-71490b3ce5dd" />
  <br><br>
  <img width="800" alt="Linkship Analytics" src="https://github.com/user-attachments/assets/35bfb071-9983-45ea-8166-be40f4d0b4de" />
</div>

---

## ✨ Core Features

*   🔗 **Smart Link Shortening:** Automatically generate collision-free Base62 short codes or define custom, human-readable aliases.
*   ⚡ **Ultra-Fast Redirects:** Heavy read operations are cached in Redis, keeping redirect latency under 50ms.
*   📊 **Deep Analytics Engine:** Tracks total clicks, daily trends, device types (mobile/desktop), and browser families.
*   🌍 **Geolocation Tracking:** Maps incoming IP addresses to specific countries and cities using the MaxMind GeoLite2 database.
*   📷 **QR Code Generation:** Automatically generates and stores downloadable QR code images for every created link.
*   🔐 **Secure Authentication:** Full user profile management with secure JWT (JSON Web Token) based API authentication.
*   ⏳ **Link Expiration:** Set automatic expiration dates to disable links after temporary campaigns end.

---

## 🏗️ System Design & Architecture

Linkship is designed to handle high traffic volumes without bottlenecking the main web threads. 

```mermaid
flowchart LR
    Client([🌐 Client / Browser]) --> LB[Railway Load Balancer]

    subgraph Cloud ["☁️ Cloud Environment"]
        LB --> Web[🐍 Django Web Server]
        Web <--> Cache[(⚡ Redis Cache)]
        Web <--> DB[(🐘 PostgreSQL Database)]
        
        Cache <--> Worker[🔄 Celery Background Worker]
        Worker <--> DB
        Worker --> GeoDB[(🗺️ GeoLite2 IP DB)]
    end

    style Cloud fill:#0d1117,stroke:#30363d,color:#c9d1d9

Architectural Decisions
    1.Redis Caching: When a user hits a short link, the system checks Redis first. If the mapping exists, it redirects instantly, bypassing a Postgres lookup.

    2.Asynchronous Analytics: Parsing User-Agent strings and executing GeoIP database lookups are             CPU-intensive. Instead of blocking the HTTP response, the web server passes the raw request data to a Celery message queue. A background worker processes the analytics and safely writes to the database.

Layer,Technology
Backend Framework,"Django 6.0.7, Django REST Framework 3.17"
Database,PostgreSQL 16 (Production) / SQLite (Local)
Cache & Message Broker,Redis 7
Background Tasks,Celery 5.6
Frontend / Templates,"Bootstrap 5, Django Crispy Forms"
Authentication,JWT via djangorestframework-simplejwt
Geolocation / Utilities,"GeoLite2 (MaxMind), qrcode, Pillow"
Infrastructure,"Docker, Gunicorn, Whitenoise, Railway"
API Documentation,drf-spectacular (Swagger UI / ReDoc)

📁 Project Structure

Linkship/
├── analytics/         # Click tracking, Celery tasks, and GeoIP logic
├── config/
│   ├── settings/
│   │   ├── base.py       # Core shared settings
│   │   ├── local.py      # Local development (SQLite, Debug=True)
│   │   └── production.py # Railway deployment (Postgres, Whitenoise)
│   ├── urls.py        # Global routing & Swagger UI
│   ├── celery.py      # Celery app initialization
│   └── wsgi.py / asgi.py
├── links/             # Link generation, Base62 encoding, QR generation
├── users/             # JWT Auth, Profiles, and user signals
├── Dockerfile         # Production container definition
├── docker-compose.yml # Local multi-container orchestration
└── Procfile           # Railway deployment commands (Migrate + Gunicorn)

🧪 Testing
Linkship maintains high reliability through automated testing. The test suite covers URL shortening logic, Base62 generation, database signals, and JWT authentication flows.

Status: 11/11 Tests Passing ✅

To run the test suite locally:
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test users

💻 Local Setup (Without Docker)
Prerequisites
    Python 3.13+
    Redis server running locally (brew install redis or apt-get install redis-server)

Steps
1. Clone the repository
git clone [https://github.com/Abitesh/Linkship.git](https://github.com/Abitesh/Linkship.git)
cd Linkship

2. Create a virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

3. Install dependencies
pip install -r requirements.txt

4. Set up the Database
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

5. Start the Services
You will need two terminal windows:
# Terminal 1: Start the Django web server
python manage.py runserver

# Terminal 2: Start the Celery worker for background analytics
celery -A config worker --loglevel=info

🐳 Docker Setup (Recommended)
The fastest way to spin up the entire application stack (Django + Postgres + Redis + Celery) locally.
docker-compose up --build
The web server will be available at http://localhost:8000.

.

🔑 Environment Variables
For production or Docker environments, provide the following variables:
# Core Django
SECRET_KEY=your_secure_secret_key
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=yourdomain.com,localhost

# Database & Cache
DATABASE_URL=postgres://user:password@hostname:5432/dbname
REDIS_URL=redis://localhost:6379/0

# Geolocation
GEOIP2_DB_PATH=/path/to/GeoLite2-City.mmdb

📖 API Reference
Linkship ships with an interactive Swagger UI to easily test endpoints. View the live docs at: /api/docs/
Authentication
POST /api/auth/jwt/login/ - Obtain JWT access & refresh tokens

POST /api/auth/jwt/refresh/ - Get a new access token

POST /api/register/ - Register a new user via API

Links Management
POST /api/links/urls/ - Create a new shortened link

GET /api/links/urls/ - List all links for the authenticated user

GET /api/links/urls/{id}/ - Retrieve details for a specific link

DELETE /api/links/urls/{id}/ - Delete a link

GET /api/links/urls/{id}/qr/ - Download the generated QR code image

Analytics
GET /api/links/urls/{id}/analytics/ - Retrieve total clicks, daily graphs, top browsers, devices, and countries.

🚀 Deployment (Railway)
This project is optimized for deployment on Railway.app using the provided Dockerfile and Procfile.

Connect your GitHub repository to Railway.

Provision a PostgreSQL and Redis service within your Railway project.

Map the DATABASE_URL and REDIS_URL to your Django service.

Add DJANGO_SETTINGS_MODULE=config.settings.production to your environment variables.

Railway will automatically build the image, run migrations (python manage.py migrate), and serve static files via Whitenoise.

🔮 Future Improvements
[ ] Custom Domains: Allow users to attach their own domains (e.g., link.mybrand.com/promo).

[ ] Browser Extension: 1-click URL shortening directly from the browser toolbar.

[ ] CI/CD Pipeline: Implement GitHub Actions to automate running the test suite on every pull request.

🤝 Contributing
Contributions, issues, and feature requests are welcome!

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

👤 Author
Abitesh

GitHub: @Abitesh
