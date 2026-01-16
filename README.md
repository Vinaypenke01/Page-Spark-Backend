# LivePage Backend - AI-Powered HTML Page Generator

![Django](https://img.shields.io/badge/Django-6.0-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.x-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Code Review Summary](#code-review-summary)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Security](#security)
- [Testing](#testing)
- [Configuration](#configuration)
- [Deployment Considerations](#deployment-considerations)
- [Contributing](#contributing)

---

## 🎯 Overview

**LivePage Backend** is a Django REST Framework (DRF) powered backend service that generates AI-powered HTML pages on demand. Users submit prompts via API, and the system leverages OpenRouter AI to generate complete, sanitized, single-file HTML pages with Tailwind CSS styling.

### Key Capabilities
- ✅ AI-powered HTML generation via OpenRouter (Mistral 7B)
- ✅ Comprehensive HTML sanitization to prevent XSS attacks
- ✅ User history tracking by email
- ✅ Live page serving with view count analytics
- ✅ Admin analytics dashboard
- ✅ PostgreSQL database with UUID-based page identification
- ✅ Fallback mechanism for API failures
- ✅ CORS-enabled for frontend integration

---

## 🏗 Architecture

The backend follows a **clean 3-layer architecture**:

```
┌─────────────────────────────────────────────┐
│           API Layer (Views)                 │
│  - Request Validation                       │
│  - Response Serialization                   │
│  - HTTP Handling                            │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       Business Logic (Services)             │
│  - GenericPageService (Orchestrator)        │
│  - OpenRouterService (AI Integration)       │
│  - HtmlSanitizationService (Security)       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Data Layer (Models)                 │
│  - Page Model                               │
│  - Database Operations                      │
└─────────────────────────────────────────────┘
```

### Design Patterns
1. **Service Layer Pattern**: Business logic isolated in service classes
2. **Orchestrator Pattern**: `GenericPageService` coordinates multi-step workflows
3. **Separation of Concerns**: Views handle HTTP, services handle logic, models handle data
4. **Fail-Safe Pattern**: Fallback HTML generation when AI API fails

---

## 📊 Code Review Summary

### ✅ Strengths

#### **1. Clean Architecture**
- Well-separated concerns between views, services, and models
- Service layer properly abstracts business logic from API layer
- Clear separation of AI generation, sanitization, and persistence

#### **2. Security Implementation**
- **HTML Sanitization**: Robust Bleach-based sanitization prevents XSS
- **Script Blocking**: All JavaScript stripped except Tailwind CDN
- **Safe Tag Whitelist**: Only approved HTML tags allowed
- **UUID-based IDs**: Prevents enumeration attacks

#### **3. Error Handling**
- Graceful fallback when OpenRouter API fails
- Try-except blocks with logging
- Meaningful error responses to clients

#### **4. Performance Optimizations**
- **Atomic Operations**: Uses `F()` expressions for view count increments
- **Database Indexing**: Email field indexed for fast history queries
- **Efficient Queries**: No N+1 query issues detected

#### **5. Developer Experience**
- Comprehensive test suites (`comprehensive_tests.py`, `test_api.py`)
- Clear docstrings in views
- Environment-based configuration

---

### ⚠️ Areas for Improvement

#### **1. Admin Model Registration** (Priority: Medium)
**Issue**: [`core/admin.py`](file:///d:/livepage/backend/core/admin.py) is empty - Page model not registered
```python
# Current: Empty admin.py
# Recommended:
from django.contrib import admin
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'page_type', 'theme', 'view_count', 'created_at']
    list_filter = ['page_type', 'theme', 'is_public', 'created_at']
    search_fields = ['email', 'prompt']
    readonly_fields = ['id', 'created_at', 'view_count']
    date_hierarchy = 'created_at'
```

#### **2. API Rate Limiting** (Priority: High)
**Issue**: No rate limiting configured - vulnerable to abuse
**Recommendation**:
```python
# Install: pip install django-ratelimit
# Add to settings.py
RATELIMIT_ENABLE = True

# In views:
from django_ratelimit.decorators import ratelimit

@method_decorator(ratelimit(key='user_or_ip', rate='10/h'), name='dispatch')
class GeneratePageView(APIView):
    pass
```

#### **3. Logging Configuration** (Priority: Medium)
**Issue**: Logger instantiated but no logging configuration in settings
**Recommendation**:
```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

#### **4. Environment Variable Validation** (Priority: Medium)
**Issue**: Missing validation for required environment variables
**Current Line 134** in [`settings.py`](file:///d:/livepage/backend/config/settings.py#L134):
```python
OPENROUTER_API_KEY = env('OPENAI_API_KEY')  # Typo here, should be OPENROUTER_API_KEY
```
**Recommendation**:
```python
# Validate required keys on startup
required_vars = ['SECRET_KEY', 'DATABASE_URL', 'OPENROUTER_API_KEY']
for var in required_vars:
    if not env(var, default=None):
        raise ImproperlyConfigured(f"Missing required environment variable: {var}")
```

#### **5. API Documentation** (Priority: Low)
**Issue**: No API schema generation or documentation
**Recommendation**:
```bash
pip install drf-spectacular
```
```python
# settings.py
INSTALLED_APPS += ['drf_spectacular']
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
```

#### **6. Test Coverage** (Priority: Medium)
**Issue**: No unit tests for services, only integration tests
**Recommendation**: Add unit tests for `HtmlSanitizationService` and `OpenRouterService`

#### **7. Sanitization Edge Case** (Priority: High)
**Issue**: Tailwind CDN script tag added without sanitization in [`services.py:185-194`](file:///d:/livepage/backend/core/services.py#L185-L194)
**Potential Issue**: If `clean_html` contains malicious `<head>` tag manipulation
**Recommendation**: Use BeautifulSoup for safer DOM manipulation

#### **8. Database Constraints** (Priority: Medium)
**Issue**: No constraints on `page_type` and `theme` fields in [`models.py`](file:///d:/livepage/backend/core/models.py#L8-L9)
**Recommendation**:
```python
class Page(models.Model):
    PAGE_TYPES = [
        ('landing', 'Landing Page'),
        ('portfolio', 'Portfolio'),
        ('blog', 'Blog'),
    ]
    THEMES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
        ('colorful', 'Colorful'),
    ]
    page_type = models.CharField(max_length=50, choices=PAGE_TYPES)
    theme = models.CharField(max_length=50, choices=THEMES)
```

---

## 🚀 Features

### Core Functionality
1. **AI Page Generation**
   - Generates complete HTML pages from text prompts
   - Supports multiple page types and themes
   - Automatic Tailwind CSS integration
   
2. **Live Page Serving**
   - Direct HTML rendering via unique URLs
   - Automatic view tracking
   - Public/private page support

3. **User History**
   - Track all pages by email
   - Chronological ordering
   - Full page metadata access

4. **Admin Dashboard**
   - System-wide analytics
   - Total page count tracking
   - Protected by authentication

---

## 🛠 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 6.0 |
| API Framework | Django REST Framework | 3.x |
| Database | PostgreSQL | Latest |
| AI Provider | OpenRouter (Mistral 7B) | API v1 |
| HTML Sanitization | Bleach | Latest |
| Environment Management | django-environ | Latest |
| CORS Handling | django-cors-headers | Latest |

---

## 📁 Project Structure

```
backend/
├── config/                      # Django project configuration
│   ├── __init__.py
│   ├── settings.py             # ⚙️ Main settings (environment-based)
│   ├── urls.py                 # 🌐 Root URL configuration
│   ├── wsgi.py                 # 🚀 WSGI entry point
│   └── asgi.py                 # ⚡ ASGI entry point
│
├── core/                        # Main application
│   ├── migrations/
│   │   └── 0001_initial.py     # 📊 Initial database schema
│   ├── __init__.py
│   ├── admin.py                # 🔧 Admin interface (needs implementation)
│   ├── apps.py                 # 📦 App configuration
│   ├── models.py               # 🗃️ Database models (Page)
│   ├── serializers.py          # 🔄 DRF serializers
│   ├── services.py             # 💼 Business logic layer
│   ├── views.py                # 🎯 API endpoints
│   ├── urls.py                 # 🔗 App-level URLs
│   └── tests.py                # 🧪 (Empty - tests in root)
│
├── .env                         # 🔑 Environment variables (not in version control)
├── manage.py                    # 🎮 Django management script
├── requirements.txt             # 📦 Python dependencies
├── comprehensive_tests.py       # 🧪 Integration test suite
├── test_api.py                  # 🧪 Manual API testing script
├── manual_insert.py             # 🔧 Database seeding utility
└── README.md                    # 📖 This file
```

---

## ⚡ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL installed and running
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Step 1: Clone and Setup Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the backend root:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgres://username:password@localhost:5432/livepage_db

# OpenRouter AI Configuration
OPENROUTER_API_KEY=your-openrouter-api-key
```

### Step 4: Database Setup
```bash
# Create database
createdb livepage_db

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
```

### Step 5: Run Development Server
```bash
python manage.py runserver
```

Server will start at `http://127.0.0.1:8000`

---

## 🌐 API Endpoints

### **1. Generate Page**
**POST** `/api/generate/`

Generates a new AI-powered HTML page.

**Request:**
```json
{
  "email": "user@example.com",
  "prompt": "A modern landing page for a coffee shop with dark theme",
  "page_type": "landing",
  "theme": "dark"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "live_url": "http://127.0.0.1:8000/p/550e8400-e29b-41d4-a716-446655440000/",
  "created_at": "2026-01-14T02:08:25.123456Z"
}
```

**Validation:**
- Email: Must be valid email format
- Prompt: 10-5000 characters
- Page Type: Max 50 characters
- Theme: Max 50 characters

---

### **2. View Live Page**
**GET** `/p/<uuid:page_id>/`

Renders the generated HTML page and increments view count.

**Response:**
- Content-Type: `text/html`
- Returns raw HTML content

---

### **3. Get User History**
**GET** `/api/history/?email=<email>`

Retrieves all pages created by a specific email.

**Query Parameters:**
- `email` (required): User's email address

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "live_url": "http://127.0.0.1:8000/p/550e8400-e29b-41d4-a716-446655440000/",
    "created_at": "2026-01-14T02:08:25.123456Z"
  }
]
```

---

### **4. Admin Analytics**
**GET** `/api/admin/stats/`

**Authentication Required:** Admin user

**Response (200 OK):**
```json
{
  "total_pages": 42
}
```

---

## 🗃️ Database Schema

### **Page Model**

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Auto-generated, unique |
| `email` | EmailField | User email | Indexed |
| `prompt` | TextField | User's generation prompt | - |
| `page_type` | CharField(50) | Type of page | - |
| `theme` | CharField(50) | Design theme | - |
| `html_content` | TextField | Sanitized HTML | - |
| `is_public` | BooleanField | Visibility flag | Default: `True` |
| `view_count` | IntegerField | Page views | Default: `0` |
| `created_at` | DateTimeField | Creation timestamp | Auto |
| `meta_data` | JSONField | Additional metadata | Default: `{}` |

**Indexes:**
- Primary Key: `id` (UUID)
- Index: `email` (for history queries)

**Ordering:** `-created_at` (newest first)

---

## 🔒 Security

### Implemented Security Measures

#### **1. HTML Sanitization**
- **Library**: Bleach (industry-standard)
- **Process**: All AI-generated HTML sanitized before storage
- **Protections**:
  - XSS prevention (script tag removal)
  - Tag whitelist enforcement
  - Attribute filtering
  - Inline style sanitization

#### **2. Script Blocking**
- All `<script>` tags stripped except Tailwind CDN
- No user-controlled JavaScript execution
- Event handlers removed (`onclick`, `onerror`, etc.)

#### **3. CORS Configuration**
- Currently: `CORS_ALLOW_ALL_ORIGINS = True` (development)
- **Production Recommendation**:
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

#### **4. Environment Variables**
- Secrets stored in `.env` file
- Never committed to version control
- `.env` in `.gitignore`

---

### Security Recommendations

1. **Add Rate Limiting**
   ```bash
   pip install django-ratelimit
   ```

2. **Enable HTTPS in Production**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

3. **Database Connection Pooling**
   ```bash
   pip install django-db-pool
   ```

4. **Content Security Policy**
   ```bash
   pip install django-csp
   ```

---

## 🧪 Testing

### Running Tests

#### **Comprehensive Test Suite**
```bash
python comprehensive_tests.py
```

**Tests Included:**
- ✅ Successful page generation
- ✅ Email validation
- ✅ Prompt length validation
- ✅ Live page rendering
- ✅ 404 handling
- ✅ History retrieval
- ✅ Admin authentication

#### **Manual API Testing**
```bash
python test_api.py
```

**Tests Included:**
- Page generation workflow
- Live page access
- History retrieval

---

### Test Results Location
Test outputs saved to: `test_results.txt`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | ✅ Yes | Django secret key | `django-insecure-...` |
| `DEBUG` | ❌ No | Debug mode | `True` / `False` |
| `ALLOWED_HOSTS` | ❌ No | Allowed hostnames | `localhost,127.0.0.1` |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection | `postgres://user:pass@localhost/db` |
| `OPENROUTER_API_KEY` | ✅ Yes | OpenRouter API key | `sk-or-v1-...` |

---

### Django Settings Highlights

**CORS Configuration:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ Change in production
```

**Database:**
```python
DATABASES = {
    'default': env.db()  # Loaded from DATABASE_URL
}
```

**Static Files:**
```python
STATIC_URL = 'static/'
```

---

## 🚀 Deployment Considerations

### Pre-Deployment Checklist

- [ ] Set `DEBUG = False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Update CORS settings to specific origins
- [ ] Enable HTTPS redirects
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure static file serving (Whitenoise/Nginx)
- [ ] Set up PostgreSQL connection pooling
- [ ] Configure logging to file/service
- [ ] Add health check endpoint
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Implement database backups
- [ ] Add rate limiting
- [ ] Review OpenRouter API quotas

### Recommended Production Stack

```
┌─────────────────┐
│   Nginx/Caddy   │  (Reverse Proxy, SSL)
└────────┬────────┘
         │
┌────────▼────────┐
│   Gunicorn      │  (WSGI Server)
└────────┬────────┘
         │
┌────────▼────────┐
│  Django App     │
└────────┬────────┘
         │
┌────────▼────────┐
│  PostgreSQL     │
└─────────────────┘
```

### Example Gunicorn Config

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

---

## 📈 Performance Optimization

### Current Optimizations
- ✅ Database indexing on email field
- ✅ Atomic view count updates with `F()` expressions
- ✅ Efficient query ordering

### Recommended Additions
1. **Caching Layer** (Redis)
   ```bash
   pip install django-redis
   ```

2. **Database Query Optimization**
   - Use `select_related()` if adding foreign keys
   - Implement pagination for history endpoint

3. **CDN for Static Files**
   - CloudFront, Cloudflare, or similar

---

## 🤝 Contributing

### Development Guidelines
1. Follow PEP 8 style guide
2. Write docstrings for all public methods
3. Add tests for new features
4. Update this README for major changes
5. Use meaningful commit messages

### Code Quality Tools
```bash
# Linting
pip install flake8
flake8 .

# Code Formatting
pip install black
black .

# Type Checking
pip install mypy
mypy .
```

---

## 📝 License

This project is proprietary. All rights reserved.

---

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Contact the development team
- Check existing documentation

---

## 🎯 Roadmap

### Planned Features
- [ ] User authentication system
- [ ] Page editing capabilities
- [ ] Template library
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Custom domain support
- [ ] Theme customization API
- [ ] Webhook notifications

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [Bleach Documentation](https://bleach.readthedocs.io/)

---

**Last Updated:** January 14, 2026
**Version:** 1.0.0
**Maintained by:** LivePage Development Team
