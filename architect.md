# System Architecture — Module 1: Pharmacy & Medicine Discovery

> **Status:** Final — Ready for Team Lead's phased implementation plan  
> **Based on:** `srs-module1.md` (finalized) + Client decisions from Discovery Review and SRS Review  
> **Date:** July 2026  
> **Author:** Senior System Designer / Architect  
> **Document purpose:** This is the authoritative architecture document for Module 1. Every section contains a decision with its rationale, not an open menu. Backend and Frontend teams build against this document directly; the Team Lead translates it into phases.

---

## 1. System Overview

### 1.1 What the System Does

A two-sided pharmacy marketplace for Bangladesh. **Module 1** is the discovery and price-comparison phase only — no transactions. Pharmacy owners register and list their medicines with prices; customers search and compare prices across nearby pharmacies.

### 1.2 Target Platforms

| Platform | Purpose | Technology |
|---|---|---|
| Android app | Customer discovery (search, radius view, price comparison) | Flutter |
| Responsive website | Customer discovery + Pharmacy Owner dashboard + Admin dashboard | Django templates + htmx + Alpine.js |
| Shared REST API backend | All data operations | Django REST Framework |

### 1.3 Mental Model

```
[Customer Android App (Flutter)] ──┐
[Customer Website (Django+htmx)] ──┤──► [Django REST Framework API] ──► [PostgreSQL + PostGIS]
[Pharmacy Owner Dashboard (Web)] ──┤                                          │
[Admin Dashboard (Web)] ───────────┘                                    [Redis Cache]
                                                                              │
                                                                     [S3 Object Storage]
```

All four frontend surfaces consume the same Django backend. The website and dashboards are server-rendered Django templates with htmx for interactivity; the Android app consumes the DRF JSON API.

---

## 2. Architecture Style

### Decision: Modular Monolith (Django Project with Bounded-Context Apps)

**Chosen:** Modular monolith within a single Django project, with clear app boundaries that map to business domains.

**Alternatives considered and why they lost:**
- **Microservices:** Premature for a lean team and early-stage product. Adds network overhead, deployment complexity, data consistency challenges, and operational burden that doesn't justify itself until the team and traffic scale significantly. If the product succeeds, individual apps can be extracted into services later because the app boundaries are already domain-bounded.
- **Flat Django project (single app):** Loses the bounded-context boundaries that make future extraction possible. Would cause tight coupling between domains (e.g., pharmacy profile logic mixed with search logic mixed with catalog normalization).

### Rationale

- The SRS data model (Section 4) defines clear entity groupings that map naturally to Django apps
- Future modules (ordering, payments, prescriptions, delivery) each become new apps that import from base apps but never vice versa — this dependency direction is enforced at the code review level
- A single database with transactional guarantees is simpler than distributed transactions across services
- The entire team works in one repository, one deployment, one CI pipeline

### App Boundaries (Django Apps within the Project)

| App | Responsibility | Depends On |
|---|---|---|
| `accounts` | User models (Customer, PharmacyOwner, Admin), JWT auth, registration | — |
| `pharmacies` | Pharmacy profiles, storefront management, geolocation, operating hours | `accounts` |
| `catalog` | Master medicine catalog, pharmacy medicine listings (the pivot entity), bulk upload | `pharmacies` |
| `search` | Medicine search, pharmacy search, geospatial radius queries, price comparison views | `catalog`, `pharmacies` |
| `notifications` | "Notify me" subscriptions (stub for future push notifications) | `catalog`, `accounts` |
| `core` | Shared base models, mixins, utility functions, pagination, i18n helpers | — |

**Dependency rule:** `search` → `catalog` → `pharmacies` → `accounts`. `catalog` never imports from `search`. `pharmacies` never imports from `catalog`. This prevents circular dependencies and enforces the bounded context.

---

## 3. Components & Responsibilities

### 3.1 Django REST Framework Backend (django_project/)

#### 3.1.1 `accounts` app
- **Models:** `Customer`, `PharmacyOwner`, `Admin` (all extending Django's `AbstractUser` or using a shared `User` model with a `role` field — System Designer recommends a single `User` model with a `role` CharField using choices: `customer`, `pharmacy_owner`, `admin`)
- **Endpoints:** Registration (customer + pharmacy owner), login, token refresh, profile update
- **Auth:** JWT (access + refresh tokens) for API consumers (Flutter app); Django session auth for web dashboards
- **Boundary:** No knowledge of pharmacies, medicines, or search. Pure identity and authentication.

#### 3.1.2 `pharmacies` app
- **Models:** `Pharmacy` (name, address, lat/lng, DGDA license number, pharmacist info, operating hours JSON, status, is_verified placeholder)
- **Endpoints:** Pharmacy CRUD (owner-only), storefront view (public), geolocation update, pharmacy search
- **Boundary:** Owns all pharmacy-profile data. Does not know about medicines or listings — those live in `catalog`.

#### 3.1.3 `catalog` app
- **Models:** `MasterMedicine`, `PharmacyMedicineListing` (the pivot — references both `Pharmacy` and `MasterMedicine`)
- **Endpoints:** Master catalog CRUD (admin only), listing CRUD (pharmacy owner), bulk CSV upload, normalization interface (admin)
- **Boundary:** Owns all medicine data. `MasterMedicine.requires_prescription` and `PharmacyMedicineListing.stock_status` are present as boolean/choice fields from day one but are informational only in Module 1 — they gate nothing until future modules.

#### 3.1.4 `search` app
- **Models:** None (read-only queries across `pharmacies` and `catalog` models)
- **Endpoints:** Medicine search (with radius filter and price comparison), pharmacy search, radius-filtered pharmacy list
- **Boundary:** Query-only. Uses PostGIS geospatial functions for radius calculations. Does not modify data.

#### 3.1.5 `notifications` app
- **Models:** `NotifySubscription` (email/phone, medicine reference, created_at)
- **Endpoints:** Subscribe to "notify me when ordering available" (FR-27)
- **Boundary:** Minimal. Captures opt-in interest for Module 2 launch.

#### 3.1.6 `core` app
- **Contains:** Base model classes (timestamped mixin), shared pagination classes, custom DRF permissions, i18n helper configuration, error response formatting
- **Boundary:** Utility code only. Never imports from any other app.

### 3.2 Frontend: Android App (Flutter)

- **Single-page application** that consumes the DRF JSON API
- **State management:** Provider or Riverpod (lightweight — no complex state in Module 1)
- **Key screens:** Nearby pharmacy list/map, medicine search, medicine detail with price comparison, pharmacy storefront
- **i18n:** Flutter ARB localization files. English strings only for Module 1, Bengali stubs pre-created.
- **No offline storage required** for Module 1 (discovery is always online). Future modules may add local caching via `sqflite` or similar.
- **Minimal native plugin requirements:** Location services (geolocator package), HTTP client (dio or http), camera (future module — not needed now)

### 3.3 Frontend: Web Applications (Django Templates + htmx + Alpine.js)

**Three surfaces, one codebase:**
1. **Customer Website** — pharmacy browsing, search, price comparison (same functionality as Android app)
2. **Pharmacy Owner Dashboard** — storefront management, medicine listing, bulk upload
3. **Admin Dashboard** — pharmacy oversight, catalog normalization, platform statistics

- All three are served from the same Django project using Django template inheritance
- `django-htmx` middleware provides `request.htmx` for partial vs full-page rendering
- `Alpine.js` handles lightweight client-side interactivity (toggles, modals, inline edits) that doesn't need a server round trip
- Each surface has a separate base template and URL namespace but shares template partials where possible (e.g., medicine card partial shared between customer search and pharmacy storefront)
- Session-based authentication (Django's built-in auth) for all three web surfaces

---

## 4. Data Model

### 4.1 Schema Design (PostgreSQL)

#### Users (single table with role)

```sql
CREATE TABLE accounts_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'pharmacy_owner', 'admin')),
    default_latitude DOUBLE PRECISION,
    default_longitude DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Design note:** Single `User` table with a `role` column rather than separate models for each role. This avoids join overhead for auth lookups and keeps permissions straightforward (enforced via DRF permissions and Django's `user_passes_test`). If roles diverge significantly in future modules, profile extension models can be added without changing the auth flow.

#### Pharmacy

```sql
CREATE TABLE pharmacies_pharmacy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES accounts_user(id),
    name VARCHAR(255) NOT NULL,
    address_line VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    division VARCHAR(100) NOT NULL,
    location GEOGRAPHY(Point, 4326) NOT NULL,  -- PostGIS geography type
    dgda_license_number VARCHAR(100),
    pharmacist_name VARCHAR(255),
    pharmacist_registration_number VARCHAR(100),
    operating_hours JSONB,  -- e.g., {"mon": {"open": "09:00", "close": "21:00"}, ...}
    phone VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'pending_review')),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pharmacies_location ON pharmacies_pharmacy USING GIST (location);
```

**Geospatial note:** The `location` column uses PostGIS `GEOGRAPHY` type with SRID 4326 (WGS84). This enables accurate distance calculations on the sphere using `ST_DWithin` and `ST_Distance` without projecting coordinates. The GIST index enables efficient radius queries.

#### Master Medicine Catalog

```sql
CREATE TABLE catalog_master_medicine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    dosage_form VARCHAR(100) NOT NULL,  -- e.g., Tablet, Syrup, Injection
    strength VARCHAR(100) NOT NULL,     -- e.g., 500mg, 10mg/5ml
    description TEXT,
    category VARCHAR(100),             -- e.g., Antibiotic, Antihypertensive, OTC
    requires_prescription BOOLEAN DEFAULT FALSE,  -- PLACEHOLDER for future module
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (brand_name, manufacturer, strength, dosage_form)
);

CREATE INDEX idx_master_medicine_name ON catalog_master_medicine (brand_name);
CREATE INDEX idx_master_medicine_generic ON catalog_master_medicine (generic_name);
```

#### Pharmacy Medicine Listing (Pivot)

```sql
CREATE TABLE catalog_pharmacy_medicine_listing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pharmacy_id UUID NOT NULL REFERENCES pharmacies_pharmacy(id) ON DELETE CASCADE,
    master_medicine_id UUID REFERENCES catalog_master_medicine(id) ON DELETE SET NULL,
    -- Free-text fallback fields (used when master_medicine_id IS NULL)
    unmatched_name VARCHAR(255),
    unmatched_generic_name VARCHAR(255),
    unmatched_manufacturer VARCHAR(255),
    unmatched_dosage_form VARCHAR(100),
    unmatched_strength VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_status VARCHAR(20) DEFAULT 'unknown' CHECK (stock_status IN ('in_stock', 'out_of_stock', 'unknown')),
    is_active BOOLEAN DEFAULT TRUE,
    normalization_status VARCHAR(30) DEFAULT 'matched'
        CHECK (normalization_status IN ('matched', 'unmatched_pending', 'normalized_by_admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_listing_pharmacy ON catalog_pharmacy_medicine_listing (pharmacy_id);
CREATE INDEX idx_listing_master_medicine ON catalog_pharmacy_medicine_listing (master_medicine_id);
CREATE INDEX idx_listing_normalization ON catalog_pharmacy_medicine_listing (normalization_status)
    WHERE normalization_status = 'unmatched_pending';
CREATE INDEX idx_listing_price ON catalog_pharmacy_medicine_listing (price);
```

**Critical design note:** This pivot entity is the single most important table in the schema. Future `OrderItem` will reference `catalog_pharmacy_medicine_listing.id`, NOT `catalog_master_medicine.id`. This preserves order history even if a pharmacy changes a price or removes a listing later. The `master_medicine_id` + free-text fallback columns support the Scenario C hybrid catalog model defined in SRS Section 3.2.

#### Notify Subscription

```sql
CREATE TABLE notifications_notify_subscription (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES accounts_user(id) ON DELETE CASCADE,  -- NULL if anonymous
    email VARCHAR(254),
    phone VARCHAR(20),
    master_medicine_id UUID REFERENCES catalog_master_medicine(id) ON DELETE CASCADE,
    pharmacy_id UUID REFERENCES pharmacies_pharmacy(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 Entity Relationship Summary

```
accounts_user (role-based)
    │
    ├── pharmacies_pharmacy (owner_id) — 1:N — a user who is pharmacy_owner can have many pharmacies
    │       │
    │       └── catalog_pharmacy_medicine_listing (pharmacy_id) — 1:N
    │               │
    │               └── catalog_master_medicine (master_medicine_id) — N:1
    │
    └── notifications_notify_subscription (user_id) — 1:N
            │
            └── catalog_master_medicine (master_medicine_id) — N:1
            └── pharmacies_pharmacy (pharmacy_id) — N:1
```

### 4.3 Naming Conventions

- **Django models:** PascalCase (standard Django convention)
- **Database tables:** `{app}_{model}` lowercase with underscores (Django default)
- **API fields:** snake_case (DRF default)
- **JSON fields:** snake_case keys

---

## 5. API Contracts

### 5.1 API Base

- Base URL: `/api/v1/`
- Format: JSON
- Auth: JWT Bearer token for protected endpoints (returned via `/api/v1/auth/login/`)
- Pagination: Cursor-based for list endpoints (stable ordering as items are added)
- Error format: `{"error": {"code": "ERROR_CODE", "message": "Human-readable message", "details": {}}}`
- Success format: Standard DRF — JSON object or array with pagination metadata for lists

### 5.2 Authentication Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register/customer/` | None | Register a customer account (name, phone, password) |
| POST | `/api/v1/auth/register/pharmacy-owner/` | None | Register a pharmacy owner (name, phone, password, pharmacy info) |
| POST | `/api/v1/auth/login/` | None | Login with phone + password → returns JWT access + refresh |
| POST | `/api/v1/auth/token/refresh/` | None | Refresh JWT access token |
| GET | `/api/v1/auth/profile/` | JWT | Get current user's profile |
| PATCH | `/api/v1/auth/profile/` | JWT | Update profile (name, default location) |

### 5.3 Pharmacy Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/pharmacies/?lat={}&lng={}&radius={}` | None | List pharmacies within radius (km), sorted by distance. Paginated. |
| GET | `/api/v1/pharmacies/search/?q={}&lat={}&lng={}` | None | Search pharmacies by name, within radius |
| GET | `/api/v1/pharmacies/{id}/` | None | Public pharmacy storefront + medicine listings |
| POST | `/api/v1/pharmacies/` | JWT (owner) | Create pharmacy profile (during owner registration) |
| PATCH | `/api/v1/pharmacies/{id}/` | JWT (owner) | Update pharmacy profile |
| PATCH | `/api/v1/pharmacies/{id}/location/` | JWT (owner) | Update geolocation pin |
| GET | `/api/v1/pharmacies/{id}/listings/` | None | List all active medicine listings for a pharmacy |

**Request/Response shape for GET /api/v1/pharmacies/ (radius query):**
```json
// Request query params: lat=23.8103&lng=90.4125&radius=2&page[cursor]=...
// Response:
{
  "data": [
    {
      "id": "uuid",
      "name": "Example Pharmacy",
      "address_line": "123 Main Road",
      "city": "Dhaka",
      "distance_km": 0.8,
      "is_open": true,
      "operating_hours": { "mon": { "open": "09:00", "close": "21:00" }, ... },
      "phone": "01712345678",
      "listing_count": 142
    }
  ],
  "meta": {
    "next_cursor": "cursor-string",
    "previous_cursor": null,
    "total_within_radius": 12
  }
}
```

### 5.4 Medicine Catalog Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/medicines/search/?q={}&lat={}&lng={}&radius={}&sort=price` | None | Search medicines by name, returns price comparison across in-range pharmacies |
| GET | `/api/v1/medicines/{id}/` | None | Medicine detail with full price comparison table |
| GET | `/api/v1/medicines/{id}/pharmacies/?lat={}&lng={}&radius={}` | None | Get all pharmacies carrying this medicine within radius, sorted by price |
| GET | `/api/v1/medicines/master/` | JWT (admin) | List master catalog (paginated, searchable) |
| POST | `/api/v1/medicines/master/` | JWT (admin) | Add entry to master catalog |
| PATCH | `/api/v1/medicines/master/{id}/` | JWT (admin) | Update master catalog entry |

**Request/Response shape for GET /api/v1/medicines/search/:**
```json
// Request query params: q=napa&lat=23.8103&lng=90.4125&radius=2&page[cursor]=...
// Response:
{
  "data": [
    {
      "master_medicine_id": "uuid",
      "brand_name": "Napa Extra",
      "generic_name": "Paracetamol + Caffeine",
      "manufacturer": "Beximco Pharma",
      "strength": "500mg + 65mg",
      "dosage_form": "Tablet",
      "lowest_price": 15.00,
      "highest_price": 25.00,
      "pharmacy_count": 5,
      "pharmacies": [
        { "pharmacy_id": "uuid", "name": "Pharmacy A", "distance_km": 0.5, "price": 15.00 },
        { "pharmacy_id": "uuid", "name": "Pharmacy B", "distance_km": 1.2, "price": 18.00 },
        { "pharmacy_id": "uuid", "name": "Pharmacy C", "distance_km": 1.8, "price": 25.00 }
      ]
    }
  ]
}
```

### 5.5 Pharmacy Owner Listing Management

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/listings/` | JWT (owner) | Add a medicine listing to my pharmacy |
| PATCH | `/api/v1/listings/{id}/` | JWT (owner) | Update price or stock status |
| DELETE | `/api/v1/listings/{id}/` | JWT (owner) | Remove listing |
| POST | `/api/v1/listings/bulk-upload/` | JWT (owner) | Upload CSV of medicine listings |

### 5.6 Notifications Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/notifications/subscribe/` | None | Subscribe to "notify me when ordering launches" (email/phone + optional medicine reference) |

### 5.7 Admin Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/admin/pharmacies/` | JWT (admin) | List all pharmacies with status |
| PATCH | `/api/v1/admin/pharmacies/{id}/status/` | JWT (admin) | Suspend/activate pharmacy |
| GET | `/api/v1/admin/listings/unmatched/` | JWT (admin) | Get all unmatched free-text entries |
| POST | `/api/v1/admin/listings/{id}/normalize/` | JWT (admin) | Normalize: link to master entry or reject |
| GET | `/api/v1/admin/stats/` | JWT (admin) | Platform statistics (counts) |

### 5.8 Versioning Strategy

- URL-prefixed versioning: `/api/v1/`, `/api/v2/` in the future
- Breaking changes trigger a new major version
- Minor additions (new fields, new endpoints) do not require a version bump
- The Flutter app and web frontend are pinned to a specific API version via configuration

---

## 6. Tech Stack & Rationale

| Layer | Technology | Rationale |
|---|---|---|
| **Backend Framework** | Django 5.2 LTS | LTS support through 2029; mature ORM with PostGIS integration; built-in admin, auth, i18n; htmx ecosystem; team familiarity assumed |
| **API Layer** | Django REST Framework 3.15+ | Most mature Django API framework; serializer-based validation; browsable API for debugging; easy JWT integration |
| **Database** | PostgreSQL 16+ | Required by PostGIS; JSONB support for operating_hours; robust, well-understood |
| **Geospatial** | PostGIS 3.5+ | Industry standard for geospatial queries; direct Django integration via GeoDjango; `GEOGRAPHY` type for accurate sphere distance |
| **Cache** | Redis 7+ | Session caching, API response caching (future), Celery broker (future) |
| **Web Frontend** | Django templates + django-htmx 1.28+ + htmx 2.x | No separate SPA to maintain; shared Django project with the API; htmx provides modern interactivity (search-as-you-type, partial page updates, modal dialogs) without JavaScript framework overhead; well-suited to a discovery-focused app with moderate interactivity |
| **Mobile Frontend** | Flutter 3.x (Dart) | Single codebase for Android (and future iOS); fast development cycle; rich widget system for polished UI; no heavy on-device logic in Module 1 |
| **Auth (API)** | djangorestframework-simplejwt | Stateless JWT auth for Flutter app; token refresh flow; well-maintained |
| **Object Storage** | S3-compatible (MinIO for dev, DigitalOcean Spaces / AWS S3 for prod) | Pharmacy photos; CSV uploads; future proof-of-dispensing photos |
| **Task Queue** | Celery + Redis | Deferred to Module 2+ (email/sms notifications, future async tasks). Not installed in Module 1 — use Django's synchronous email for registration verification |
| **Reverse Proxy** | Nginx | Static file serving, reverse proxy to Gunicorn, SSL termination, rate limiting |
| **Application Server** | Gunicorn | WSGI server for Django; proven, well-documented |
| **Containerization** | Docker + Docker Compose (dev), Linux VPS or PaaS (prod) | Consistent dev environment; simple enough for lean team; PaaS option (e.g., DigitalOcean App Platform, Railway) if team wants to minimize ops |
| **CI/CD** | GitHub Actions | Simple, free for small teams; lint → test → build → deploy pipeline |

**Cost-conscious choices:**
- Django templates + htmx avoids a separate frontend server cost (no Node/Next.js hosting needed)
- PostgreSQL + PostGIS is free and open-source (no paid geocoding API for radius queries — the database does it)
- MinIO for local S3 emulation; DigitalOcean Spaces ($5/month) or self-hosted MinIO for production
- No third-party geocoding service needed initially — pharmacy owners pin their location on a map, which provides lat/lng directly

---

## 7. Non-Functional Requirements

### 7.1 Performance

| Requirement | Target | Mechanism |
|---|---|---|
| Radius pharmacy list | ≤ 2s for 100 pharmacies in range | PostGIS GIST index; paginated results; Redis cache for frequent queries |
| Medicine comparison view | ≤ 3s for 20 pharmacy listings | Database-side aggregation; paginated results |
| Search autocomplete | ≤ 500ms response | Database `ILIKE` + trigram index; debounced client-side (300ms) |
| Concurrent users | 1,000 simultaneous (Dhaka peak) | Gunicorn with reasonable worker count; Nginx connection buffering; connection pooling on database |
| Bulk CSV upload | ≤ 30s for 1,000 rows | Transaction-per-row with bulk_create; progress feedback via htmx polling |

### 7.2 Availability

- **Target:** 99.5% uptime (excluding planned maintenance)
- **Planned maintenance:** Weekly 15-minute window (announced 48h in advance via status page)
- **Database:** Single PostgreSQL instance for Module 1 (replication added in Module 2+ when transactions go live)
- **Graceful degradation:** If PostGIS is unavailable, fall back to listing pharmacies without distance sort

### 7.3 Security

| Measure | Implementation |
|---|---|
| Transport security | HTTPS only (TLS 1.2+ via Nginx) |
| Password storage | bcrypt (Django default) |
| API auth | JWT access tokens (15 min expiry) + refresh tokens (7 day expiry) |
| Web auth | Django session auth with `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SECURE` |
| CORS | Restricted to known origins (Flutter app, website domain) via `django-cors-headers` |
| Rate limiting | Nginx `limit_req` on search endpoints (60 req/min per IP, adopted as final per client approval within the 30–100 range); DRF `Throttling` for authenticated endpoints |
| Input validation | DRF serializer validation; file type/size validation on CSV upload |
| CSRF | Django CSRF middleware for web forms; htmx configured to pass CSRF token via `hx-headers` |

### 7.4 Internationalization

- **Backend:** Django's `gettext`/`trans` with locale files in `locale/en/` and `locale/bn/`
- **Web templates:** `{% trans %}` and `{% blocktranslate %}` tags throughout
- **Flutter app:** ARB localization files (`lib/l10n/app_en.arb`, `app_bn.arb`)
- **Module 1:** English strings only. Bengali files created with stub/no-op translations to validate the i18n pipeline. Bengali content is a fast-follow, not a blocker.

### 7.5 Monitoring & Observability

- **Application logging:** Django structlog or `logging` module → JSON to stdout (captured by container runtime)
- **Error tracking:** Sentry (free tier) for production error aggregation
- **Performance monitoring:** Django Debug Toolbar (dev only); New Relic / Datadog APM considered when budget allows
- **Business metrics:** Tracked via database queries (pharmacy count, listing count, search volume) exposed through admin dashboard (FR-34)

---

## 8. Integration Points

| Integration | Purpose | Fail Behavior |
|---|---|---|
| PostGIS | Geospatial radius queries | System falls back to listing pharmacies without distance sort; search continues to work without radius filter |
| SMS gateway | Pharmacy owner phone verification | Email fallback; verification can be retried |
| Object Storage (S3) | Pharmacy photo uploads, CSV templates | Upload forms show errors; existing content served from application server fallback |
| Redis | Caching | Cache misses degrade to database queries (no service outage) |

**No third-party APIs are required for Module 1.** Geocoding, mapping, and search are all handled by PostGIS and Django. This is intentional — it keeps Module 1 self-contained and free from third-party API dependencies and costs.

---

## 9. Deployment Topology

### 9.1 Environments

| Environment | Purpose | Infrastructure |
|---|---|---|
| **Development** | Local development | Docker Compose (Django, PostgreSQL+PostGIS, Redis, MinIO) |
| **Staging** | Pre-production validation | Single VPS (Django + PostgreSQL + Redis + MinIO) or PaaS |
| **Production** | Live | Primary VPS for Django + Redis; Managed PostgreSQL with PostGIS; S3-compatible object storage; Nginx reverse proxy with CDN (Cloudflare Free) |

### 9.2 Production Architecture (as Module 1 grows)

```
                         ┌──────────────┐
                         │  Cloudflare   │
                         │  (CDN, SSL)   │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │    Nginx      │
                         │  (reverse     │
                         │   proxy, SSL, │
                         │   rate limit) │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
     ┌────────▼───────┐ ┌──────▼───────┐ ┌────────▼───────┐
     │  Gunicorn x4   │ │   Static     │ │   Redis        │
     │  Django API +  │ │   Files      │ │   Cache        │
     │  Web Templates │ │   (S3 or     │ │                │
     │                │ │   local)     │ │                │
     └────────┬───────┘ └──────────────┘ └────────┬───────┘
              │                                    │
              └─────────────────┬──────────────────┘
                                │
                       ┌────────▼────────┐
                       │  PostgreSQL 16+  │
                       │  + PostGIS 3.5+  │
                       │  (Managed or     │
                       │   self-hosted)   │
                       └─────────────────┘
```

### 9.3 Platform-Specific Constraints

- **Android app:** Distributed via Google Play Store (or direct APK for early testing). Play Store review cycle is not a blocker for Module 1 since we can use internal testing track for initial rollout.
- **Web dashboards:** No app store constraints. Deployed alongside the Django project.
- **Flutter web is NOT used** for the website. The website uses Django templates + htmx, which is a separate codebase from the Flutter Android app. This avoids the performance and SEO pitfalls of Flutter web.
- **Multi-tenancy:** Module 1 uses a single-database, row-level isolation approach. All pharmacies share the same tables but are isolated by `pharmacy_id` foreign keys. No tenant schema isolation needed at this scale.

---

## 10. Key Architectural Decisions (ADR-style)

### ADR-001: Single User Model with Role Field

**Context:** Need to support three user types (Customer, Pharmacy Owner, Admin) with shared auth but different permissions.

**Decision:** Single `User` model with a `role` CharField using choices. Permissions enforced via DRF permission classes and Django decorators rather than separate models.

**Consequences:**
- + Simpler auth (one login endpoint, one token type)
- + Easier to add a new role (just add a choice)
- - Profile fields are shared across all roles (mitigated by using `null=True` on role-specific fields and adding profile extension models in future if needed)

**Alternatives considered:** Separate models for each role with a shared `AbstractUser` base. Rejected because it would require three separate login flows and token types, adding complexity without benefit for Module 1's scope.

### ADR-002: PostGIS GEOGRAPHY Over GEOMETRY

**Context:** Need to calculate accurate distances within the 2 km radius. Coordinates are in WGS84 (latitude/longitude).

**Decision:** Use PostGIS `GEOGRAPHY` type rather than `GEOMETRY` with a projected SRID.

**Consequences:**
- + `ST_DWithin` and `ST_Distance` return results in meters directly (no unit conversion)
- + Accurate great-circle distances on the sphere
- - Slightly more CPU per query than projected geometry (negligible at Module 1 scale)
- - GIST index on geography is slightly larger

**Alternatives considered:** `GEOMETRY` with a local projection (e.g., Bangladesh-specific UTM zone 46N). Rejected because it introduces projection management complexity and the geography penalty is negligible for the expected query volume.

### ADR-003: Django Templates + htmx Over SPA for Web

**Context:** Need three web surfaces (customer website, pharmacy owner dashboard, admin dashboard). Team is lean with no dedicated frontend specialist.

**Decision:** Use Django templates with htmx for all web surfaces, rather than building a separate SPA (React/Vue) alongside the Flutter app.

**Consequences:**
- + One codebase for both API and web (Django project)
- + No Node.js build step or separate frontend deployment
- + Django's template inheritance makes sharing components across the three surfaces straightforward
- + htmx provides modern interactivity (search-as-you-type, infinite scroll, partial updates)
- - Web UI is less dynamic than an SPA (acceptable for a discovery app — no real-time collaboration, drag-and-drop, or complex client state)
- - htmx requires a mindset shift for developers accustomed to SPA patterns

**Alternatives considered:** React SPA with Django REST Framework backend. Rejected because it adds a second frontend codebase, a Node.js build pipeline, and state management complexity that doesn't justify itself for a content-focused discovery app with moderate interactivity.

### ADR-004: Flutter Over Native Kotlin for Android

**Context:** Need an Android app for Module 1. Future iOS is likely but not confirmed.

**Decision:** Use Flutter for the Android app instead of native Kotlin.

**Consequences:**
- + Single codebase serves current Android and future iOS
- + Faster development iteration (hot reload)
- + Rich widget library for a polished discovery UI
- - Native platform features (camera, deep location integration) require plugin bridging (but Module 1 has minimal native plugin needs)
- - Slightly larger APK size than native Kotlin (acceptable for a discovery app)

**Alternatives considered:** Kotlin with Jetpack Compose. Rejected because it locks out future iOS expansion and would require a separate team/rewrite for an iOS version. Flutter's cross-platform capability outweighs the minor native performance advantage for a UI-focused, non-intensive app.

### ADR-005: Cursor-Based Pagination Over Page-Number

**Context:** List endpoints (pharmacy list, medicine search results) need pagination. Data changes between page loads could cause duplicates or missed items with page-number pagination.

**Decision:** Use cursor-based pagination for all list endpoints.

**Consequences:**
- + Stable ordering — items won't shift between pages as data changes
- + Better performance for large offset values (no `OFFSET` clause)
- - Cannot jump to a specific page number (acceptable — users search and scroll, they don't "go to page 47")
- - Slightly more complex client implementation in Flutter (cursor management)

**Alternatives considered:** Page-number pagination. Rejected due to instability when items are added/removed between page loads (a medicine listing could appear on two pages or be missed entirely).

### ADR-006: Price as Decimal, Not Integer

**Context:** Medicine prices in Bangladesh are in BDT with up to 2 decimal places (e.g., 15.00, 125.50).

**Decision:** Use `DECIMAL(10, 2)` for price fields rather than an integer representing poysha (paisa).

**Consequences:**
- + Directly readable in database and API without conversion
- + Django's `DecimalField` maps cleanly to Python `Decimal` (no integer arithmetic bugs)
- - Slightly larger storage than integer (negligible at expected scale)

**Alternatives considered:** Integer representing poysha (1 TK = 100 poysha). Rejected because it requires everywhere conversion and introduces a class of currency arithmetic bugs that `Decimal` handles natively.

### ADR-007: Django-Native i18n Architecture (Not a Custom Solution)

**Context:** SRS requires i18n-ready architecture from day one, with English strings only for Module 1 and Bengali stubs pre-created.

**Decision:** Use Django's built-in `gettext` framework for web templates and Flutter's native ARB localization for the Android app. No custom i18n service or third-party translation management tool for Module 1.

**Consequences:**
- + Django's i18n is mature and well-documented
- + No additional infrastructure or cost
- + Flutter ARB files follow the same structure as Django `.po` files for consistent translation workflow
- - Translation management is manual (extract → translate in editor → compile) — a translation management platform can be added when the app has more languages

---

## 11. Risks & Open Questions

### 11.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| PostGIS query performance degrades beyond 1,000 pharmacies within a 2 km radius in Dhaka | Low (Dhaka has ~30-50 pharmacies per km² in dense areas, so 2 km radius = ~120-200 max) | Medium | GIST index on geography column; paginated responses; Redis caching of popular queries; vertical scaling of PostgreSQL if needed |
| Flutter app size is too large for low-end Android devices common in Bangladesh | Medium | Medium | Use Flutter's `--split-debug-info` and `--obfuscate` flags; enable Android App Bundle (not APK); defer heavy dependencies to future modules |
| CSV bulk upload fails partially (some rows valid, some invalid) | Medium | Medium | Process rows in a transaction with per-row error reporting; return a results file showing which rows succeeded and which failed with reasons |

### 11.2 Open Questions — All Closed (Resolved by Client, Verified 21 Jul 2026)

The following were open questions during architecture drafting. **All are now closed** — final review confirmation by client on 21 Jul 2026. The Tech Lead should treat them as decided and build accordingly.

| # | Question | Decision | Rationale |
|---|---|---|---|
| O-01 | Settings module structure | **Settings package** (`settings/` with `base.py`, `dev.py`, `staging.py`, `production.py`). Standard Django practice — delegate fully to Tech Lead. | No product impact; purely an engineering convention. |
| O-02 | Search endpoint rate limits | **60 req/min per IP** (as stated in Section 7.3). This value is within the client-approved range of 30–100 req/min and does not require further review. **[Closed: confirmed by client in Setup Phase review, 21 Jul 2026.]** | Public discovery endpoint. Backend may adjust within the 30–100 range at their discretion if monitoring shows reason to. |
| O-03 | Bulk CSV template: pre-seed all 39 DGDA-authorized OTC medicines? | **Yes — pre-seed all 39 OTC medicines into the master catalog before Module 1 launch.** These are the only medicines we have an authoritative, legally-sourced list for (per `research.md` Section A.4). This directly satisfies SRS FR-14. The broader ~500-item catalog can follow the hybrid incremental approach: check for a public formulary source first, engage a pharmacist consultation only if needed. Not a development blocker. | Authoritative source exists; no domain-expert consultation needed for this subset. |
| O-04 | Admin normalization interface | **Extend Django's built-in admin** for Module 1. Use a custom `ModelAdmin` for `PharmacyMedicineListing` filtered to `normalization_status = 'unmatched_pending'`, plus custom admin actions for "link to master entry" / "create new master entry" / "reject." | Consistent with budget guidance. Django admin customization is dramatically cheaper than a bespoke UI. If normalization workload later justifies a dedicated UI, that's a cheap, isolated upgrade later. |
| O-05 | Flutter state management | **Riverpod.** Module 1's state needs are genuinely light — Riverpod provides better compile-time safety than Provider with less boilerplate than BLoC. This is a light steer: if the Frontend Specialist has strong existing Riverpod-vs-Provider experience, defer to them. The point is to avoid BLoC's overhead for this module's actual complexity level. | Actively maintained successor to Provider; Module 1 has minimal state management needs. |
| O-06 | Registration OTP channel | **SMS-only (phone) is the required OTP verification channel.** Email remains optional and is never used for OTP. Matches the schema (`phone` = UNIQUE NOT NULL, `email` = nullable) and the Bangladesh market context (mobile-first, phone-centric user base). Do not add email OTP as a parallel verification path in Module 1. | Phone is the primary unique identifier in this market. Email can be collected optionally for account recovery only. |
| O-07 | Operating hours storage | **Keep JSONB for Module 1.** FR-18 only requires computing an "is currently open" indicator at read time — this does not require relational querying (e.g., "find all pharmacies open on Friday after 6pm"). A normalized model can be migrated to later if a future module needs to filter by operating hours at scale. | Over-engineering now would have no current use case. Low-risk, isolated migration path later. |

---

## 12. Future Architecture Evolution (Informational)

This section describes how the architecture would grow as future modules are added. It is **not** part of the Module 1 build plan.

### Module 2 — Ordering & Cart
- New Django app: `orders` with models `Order`, `OrderItem` (references `PharmacyMedicineListing`)
- New endpoint group: `/api/v1/orders/`
- `stock_status` on listings becomes a gating condition
- Cart state managed client-side (Flutter) or via a lightweight server-side cart (Redis)

### Module 3 — Payment Integration
- New app: `payments` with models `Payment`, `Payout`
- Integration with SSLCommerz/bKash/Nagad via their SDKs
- Webhook endpoints for payment callbacks
- `Pharmacy` gains a `payout_config` JSON field

### Module 4 — Prescription Verification
- New app: `prescriptions` with model `Prescription`
- New endpoint group: `/api/v1/prescriptions/`
- `MasterMedicine.requires_prescription` gating comes into effect
- Image upload to S3
- Admin verification workflow

### Module 5 — Delivery
- New app: `delivery` or extend `orders`
- Pharmacy delivery radius, fees, estimated time
- Third-party logistics integration (if used)

### Extraction Path
If the product scales significantly, the most likely first extraction would be the `search` app becoming a standalone service (for independent scaling of search traffic). This is made easy by the read-only nature of `search` — it depends on data from other apps via API calls rather than direct database queries once extracted.

---

*This architecture document is final for Module 1. The Team Lead should use it to produce a phased implementation plan. Backend and Frontend teams should build against the component boundaries, data model, and API contracts defined here. Any questions about scope or design intent should be directed to the System Designer.*
