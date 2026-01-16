# LivePage Backend - Architecture Documentation

## 🏗️ System Architecture

### High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A[Frontend/Browser]
        B[Mobile App]
        C[API Client]
    end
    
    subgraph "API Gateway"
        D[CORS Middleware]
        E[Django URLs Router]
    end
    
    subgraph "Presentation Layer"
        F[GeneratePageView]
        G[LivePageView]
        H[UserHistoryView]
        I[AdminAnalyticsView]
    end
    
    subgraph "Business Logic Layer"
        J[GenericPageService<br/>Orchestrator]
        K[OpenRouterService<br/>AI Integration]
        L[HtmlSanitizationService<br/>Security]
    end
    
    subgraph "Data Layer"
        M[Page Model]
        N[Django ORM]
        O[(PostgreSQL<br/>Database)]
    end
    
    subgraph "External Services"
        P[OpenRouter AI API<br/>Mistral 7B]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    E --> G
    E --> H
    E --> I
    
    F --> J
    J --> K
    K --> P
    P --> K
    J --> L
    L --> J
    J --> M
    
    H --> M
    G --> M
    I --> M
    
    M --> N
    N --> O
    
    style F fill:#e1f5ff
    style G fill:#e1f5ff
    style H fill:#e1f5ff
    style I fill:#e1f5ff
    style J fill:#fff3cd
    style K fill:#fff3cd
    style L fill:#fff3cd
    style M fill:#d4edda
    style O fill:#d4edda
    style P fill:#f8d7da
```

---

## 🔄 Request Flow Diagrams

### Page Generation Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant API as GeneratePageView
    participant Service as GenericPageService
    participant AI as OpenRouterService
    participant Sanitizer as HtmlSanitizationService
    participant DB as PostgreSQL
    
    User->>FE: Enter prompt + email
    FE->>API: POST /api/generate/
    
    Note over API: Validate request<br/>serializer
    
    API->>Service: generate_page(email, prompt, type, theme)
    
    Service->>AI: generate_html(prompt, type, theme)
    AI->>AI: Build system prompt
    AI->>OpenRouter: API call
    
    alt API Success
        OpenRouter-->>AI: Return HTML
        AI-->>Service: raw_html
    else API Failure
        OpenRouter-->>AI: Error
        AI-->>Service: fallback_html
    end
    
    Service->>Sanitizer: sanitize(raw_html)
    Sanitizer->>Sanitizer: Remove scripts
    Sanitizer->>Sanitizer: Filter tags
    Sanitizer->>Sanitizer: Add Tailwind CDN
    Sanitizer-->>Service: clean_html
    
    Service->>DB: Create Page record
    DB-->>Service: page object
    
    Service-->>API: page
    API->>API: Serialize response
    API-->>FE: {id, live_url, created_at}
    
    FE-->>User: Show success + live link
```

---

### Live Page Rendering Flow

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant View as LivePageView
    participant DB as PostgreSQL
    
    User->>Browser: Visit /p/{uuid}/
    Browser->>View: GET request
    
    View->>DB: Get Page by ID
    
    alt Page Exists
        DB-->>View: page object
        View->>DB: Atomic increment view_count
        View->>View: Prepare HTML response
        View-->>Browser: HTML content (text/html)
        Browser->>Browser: Render page
        Browser-->>User: Display generated page
    else Page Not Found
        DB-->>View: DoesNotExist
        View-->>Browser: 404 Not Found
        Browser-->>User: Error page
    end
```

---

## 📊 Data Flow Architecture

### Component Interaction

```mermaid
graph LR
    subgraph "Input Validation"
        A[User Request] --> B[PageRequestSerializer]
        B --> C{Valid?}
        C -->|No| D[400 Error Response]
        C -->|Yes| E[Validated Data]
    end
    
    subgraph "Business Logic"
        E --> F[GenericPageService]
        F --> G[OpenRouterService]
        G --> H[AI Generated HTML]
        H --> I[HtmlSanitizationService]
        I --> J[Clean HTML]
    end
    
    subgraph "Persistence"
        J --> K[Page.objects.create]
        K --> L[Database Record]
    end
    
    subgraph "Response"
        L --> M[PageResponseSerializer]
        M --> N[JSON Response]
    end
    
    style C fill:#fff3cd
    style I fill:#d4edda
    style L fill:#e1f5ff
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    PAGE {
        uuid id PK
        varchar email
        text prompt
        varchar page_type
        varchar theme
        text html_content
        boolean is_public
        int view_count
        timestamp created_at
        jsonb meta_data
    }
    
    PAGE ||--o{ PAGE_VIEW : "tracks"
    
    PAGE_VIEW {
        int id PK
        uuid page_id FK
        timestamp viewed_at
        varchar ip_address
    }
    
    USER {
        int id PK
        varchar email
        boolean is_admin
    }
    
    USER ||--o{ PAGE : "creates"
```

**Notes:**
- `PAGE_VIEW` entity not currently implemented (future enhancement)
- `USER` table managed by Django auth system
- Current implementation tracks views via `view_count` field

---

## 🔐 Security Architecture

### Security Layers

```mermaid
graph TD
    A[User Input] --> B[Django CSRF Protection]
    B --> C[DRF Serializer Validation]
    C --> D[Email Format Validation]
    C --> E[Prompt Length Validation]
    
    D --> F[AI Generation]
    E --> F
    
    F --> G[HTML Sanitization Layer]
    
    G --> H[Tag Whitelist Filter]
    G --> I[Attribute Filter]
    G --> J[Script Blocker]
    
    H --> K[Safe HTML]
    I --> K
    J --> K
    
    K --> L[Database Storage]
    L --> M[UUID-based Access]
    
    M --> N[Public Live Page]
    
    style G fill:#f8d7da
    style H fill:#fff3cd
    style I fill:#fff3cd
    style J fill:#fff3cd
    style M fill:#d4edda
```

### Sanitization Process

```mermaid
flowchart LR
    A[AI Generated HTML] --> B{Contains Scripts?}
    B -->|Yes| C[Remove Script Tags]
    B -->|No| D[Tag Whitelist Check]
    C --> D
    
    D --> E{All Tags Allowed?}
    E -->|No| F[Strip Disallowed Tags]
    E -->|Yes| G[Attribute Check]
    F --> G
    
    G --> H{Safe Attributes?}
    H -->|No| I[Remove Unsafe Attrs]
    H -->|Yes| J[Tailwind CDN Check]
    I --> J
    
    J --> K{CDN Present?}
    K -->|No| L[Inject Tailwind CDN]
    K -->|Yes| M[Clean HTML Output]
    L --> M
    
    style C fill:#f8d7da
    style F fill:#f8d7da
    style I fill:#f8d7da
    style M fill:#d4edda
```

---

## 🔄 Service Layer Design Patterns

### Orchestrator Pattern

```mermaid
classDiagram
    class GenericPageService {
        <<Orchestrator>>
        +generate_page(email, prompt, type, theme) Page
        -coordinate_services()
    }
    
    class OpenRouterService {
        <<External API>>
        +generate_html(prompt, type, theme) str
        -build_system_prompt() str
        -call_api() dict
        -handle_fallback() str
    }
    
    class HtmlSanitizationService {
        <<Security>>
        +sanitize(html_content) str
        -filter_tags() str
        -filter_attributes() str
        -ensure_tailwind_cdn() str
    }
    
    class Page {
        <<Model>>
        +id: UUID
        +email: str
        +prompt: str
        +html_content: str
        +view_count: int
    }
    
    GenericPageService --> OpenRouterService : uses
    GenericPageService --> HtmlSanitizationService : uses
    GenericPageService --> Page : creates
```

---

## 📡 API Architecture

### RESTful Endpoint Structure

```mermaid
mindmap
    root((LivePage API))
        Public Endpoints
            POST /api/generate/
                Generate new page
                Rate limited
            GET /p/:uuid/
                Render live page
                Track views
            GET /api/history/
                User's page history
                Email required
        Admin Endpoints
            GET /api/admin/stats/
                System analytics
                Auth required
            Django Admin
                /admin/
                CRUD operations
```

---

## 🚀 Deployment Architecture

### Recommended Production Setup

```mermaid
graph TB
    subgraph "Client Tier"
        A[Browser]
        B[Mobile App]
    end
    
    subgraph "CDN Layer"
        C[CloudFlare/CloudFront]
    end
    
    subgraph "Load Balancer"
        D[Nginx/Caddy]
    end
    
    subgraph "Application Tier"
        E1[Gunicorn Instance 1]
        E2[Gunicorn Instance 2]
        E3[Gunicorn Instance 3]
    end
    
    subgraph "Task Queue"
        F[Celery Workers]
        G[Redis Queue]
    end
    
    subgraph "Cache Layer"
        H[Redis Cache]
    end
    
    subgraph "Database Tier"
        I[(PostgreSQL Primary)]
        J[(PostgreSQL Replica)]
    end
    
    subgraph "External Services"
        K[OpenRouter AI]
    end
    
    A --> C
    B --> C
    C --> D
    
    D --> E1
    D --> E2
    D --> E3
    
    E1 --> H
    E2 --> H
    E3 --> H
    
    E1 --> G
    E2 --> G
    E3 --> G
    
    G --> F
    F --> K
    
    E1 --> I
    E2 --> I
    E3 --> I
    
    I --> J
    
    style C fill:#e1f5ff
    style H fill:#fff3cd
    style I fill:#d4edda
    style K fill:#f8d7da
```

---

## 🔧 Technology Stack Layers

### Full Stack Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React/Next.js]
        B[TypeScript]
        C[Tailwind CSS]
    end
    
    subgraph "API Layer"
        D[Django 6.0]
        E[Django REST Framework]
        F[CORS Headers]
    end
    
    subgraph "Business Logic"
        G[Custom Services]
        H[Bleach Sanitization]
    end
    
    subgraph "Data Persistence"
        I[Django ORM]
        J[PostgreSQL]
    end
    
    subgraph "External Integrations"
        K[OpenRouter API]
        L[Mistral 7B AI]
    end
    
    subgraph "Infrastructure"
        M[Gunicorn WSGI]
        N[Nginx]
        O[Redis Cache]
    end
    
    A --> D
    B --> D
    D --> E
    E --> F
    E --> G
    G --> H
    G --> I
    I --> J
    G --> K
    K --> L
    M --> D
    N --> M
    E --> O
```

---

## 📈 Scalability Architecture

### Horizontal Scaling Strategy

```mermaid
graph LR
    subgraph "Users"
        U1[User 1]
        U2[User 2]
        U3[User N]
    end
    
    subgraph "Load Distribution"
        LB[Load Balancer<br/>Round Robin]
    end
    
    subgraph "Application Servers"
        A1[Django App 1]
        A2[Django App 2]
        A3[Django App N]
    end
    
    subgraph "Shared Resources"
        DB[(Database<br/>Connection Pool)]
        Cache[(Redis<br/>Shared Cache)]
        Queue[(Task Queue)]
    end
    
    U1 --> LB
    U2 --> LB
    U3 --> LB
    
    LB --> A1
    LB --> A2
    LB --> A3
    
    A1 --> DB
    A2 --> DB
    A3 --> DB
    
    A1 --> Cache
    A2 --> Cache
    A3 --> Cache
    
    A1 --> Queue
    A2 --> Queue
    A3 --> Queue
    
    style LB fill:#e1f5ff
    style DB fill:#d4edda
    style Cache fill:#fff3cd
```

---

## 🔍 Monitoring Architecture

### Observability Stack (Recommended)

```mermaid
graph TB
    subgraph "Application"
        A[Django App]
    end
    
    subgraph "Logging"
        B[Application Logs]
        C[Error Logs]
        D[Access Logs]
    end
    
    subgraph "Metrics"
        E[Request Rate]
        F[Response Time]
        G[Error Rate]
        H[AI API Calls]
    end
    
    subgraph "Monitoring Tools"
        I[Prometheus]
        J[Grafana]
    end
    
    subgraph "Error Tracking"
        K[Sentry]
    end
    
    subgraph "Alerts"
        L[Email Alerts]
        M[Slack Notifications]
    end
    
    A --> B
    A --> C
    A --> D
    
    A --> E
    A --> F
    A --> G
    A --> H
    
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J
    
    C --> K
    K --> L
    K --> M
    
    style K fill:#f8d7da
    style J fill:#e1f5ff
```

---

## 📊 Performance Optimization Layers

```mermaid
graph TD
    A[User Request] --> B{Cache Hit?}
    
    B -->|Yes| C[Return Cached Response]
    B -->|No| D[Database Query]
    
    D --> E{Indexed Field?}
    E -->|Yes| F[Fast Index Lookup]
    E -->|No| G[Full Table Scan]
    
    F --> H[Query Result]
    G --> H
    
    H --> I[Serialize Data]
    I --> J[Cache Response]
    J --> K[Return to User]
    
    C --> K
    
    style C fill:#d4edda
    style F fill:#d4edda
    style G fill:#f8d7da
```

---

## 🔐 Authentication Flow (Future Enhancement)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant Auth as Authentication API
    participant JWT as JWT Service
    participant API as Protected API
    
    User->>FE: Login (email/password)
    FE->>Auth: POST /api/auth/login
    Auth->>Auth: Verify credentials
    Auth->>JWT: Generate token
    JWT-->>Auth: Access + Refresh tokens
    Auth-->>FE: {access_token, refresh_token}
    
    FE->>FE: Store tokens
    
    User->>FE: Generate page
    FE->>API: POST /api/generate/<br/>Authorization: Bearer {token}
    API->>JWT: Validate token
    JWT-->>API: Valid user
    API->>API: Process request
    API-->>FE: Success response
```

---

## 📝 Configuration Management

### Environment-Based Configuration

```mermaid
flowchart LR
    A[.env File] --> B{Environment}
    
    B -->|Development| C[settings_dev.py]
    B -->|Staging| D[settings_staging.py]
    B -->|Production| E[settings_prod.py]
    
    C --> F[DEBUG=True<br/>ALLOWED_HOSTS=*<br/>CORS=*]
    D --> G[DEBUG=False<br/>ALLOWED_HOSTS=staging.com<br/>CORS=specific]
    E --> H[DEBUG=False<br/>ALLOWED_HOSTS=livepage.com<br/>CORS=specific<br/>SSL=True]
    
    F --> I[Application]
    G --> I
    H --> I
    
    style F fill:#e1f5ff
    style G fill:#fff3cd
    style H fill:#d4edda
```

---

## 🎯 Summary

This architecture document provides comprehensive visual representations of:

1. **System Architecture** - High-level component interaction
2. **Request Flows** - Detailed sequence diagrams
3. **Data Flows** - Entity relationships and data movement
4. **Security Layers** - Protection mechanisms
5. **Service Patterns** - Design pattern implementations
6. **API Structure** - Endpoint organization
7. **Deployment Strategy** - Production infrastructure
8. **Scalability** - Horizontal scaling approach
9. **Monitoring** - Observability stack
10. **Performance** - Optimization strategies

### Key Architectural Principles

- ✅ **Separation of Concerns** - Clear layer boundaries
- ✅ **Service-Oriented Design** - Modular business logic
- ✅ **Defense in Depth** - Multiple security layers
- ✅ **Fail-Safe Defaults** - Graceful degradation
- ✅ **Stateless API** - Horizontal scalability
- ✅ **Database-Centric** - PostgreSQL as source of truth

---

**Architecture Version:** 1.0.0  
**Last Updated:** January 14, 2026  
**Maintained by:** LivePage Development Team
