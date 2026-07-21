# Tech Lead — Phased Implementation Plan: Module 1

> **Status:** Draft — awaiting client review  
> **Date:** July 2026  
> **Author:** Tech Lead  
> **Reference documents:** `srs-module1.md` (final), `architect.md` (final)  
> **Document purpose:** Defines the phase breakdown, setup tasks, and sequencing rationale for building Module 1. This is a planning-only document — no application code is written yet. After this plan is approved, I execute the setup phase, then hand off to Backend and Frontend Specialists per the phased workflow.

---

## 1. Phase Overview & Dependency Map

### Phase Sequencing Rationale

```
Phase 1: Foundation ──────────────────────────────────► Phase 2: Medicine Catalog ──────────────────────────► Phase 3: Customer Discovery
  (Auth + Pharmacy Profiles)                              (Master Catalog + Listings)                            (Search + Comparison + Notifications)
        │                                                         │                                                         │
        │  accounts.User model                                    │  MasterMedicine model                                    │  search app (reads from catalog + pharmacies)
        │  JWT auth / registration                                │  PharmacyMedicineListing (THE PIVOT)                      │  geospatial radius queries
        │  Pharmacy model + storefront                            │  Listing CRUD + bulk CSV upload                           │  medicine + pharmacy search
        │  Flutter + web auth screens                             │  Admin Django admin normalization                         │  price comparison views
        └──────────────────────────                               │  Pharmacy owner catalog management UI                    │  notifications app ("notify me")
                                                                  └──────────────────────────                                 │  Flutter customer screens
                                                                                                                             │  Customer website (htmx)
                                                                                                                             │  Admin dashboard stats
                                                                                                                             └──────────────────────────
```

**Why this ordering:**

1. **Phase 1 must come first** because every other entity in the system depends on `accounts.User` (via `owner_id` foreign key on `Pharmacy`) and `Pharmacy` (via `pharmacy_id` foreign key on `PharmacyMedicineListing`). Without identities and pharmacy profiles, there is nothing to list medicines against and no one to list them.

2. **Phase 2 builds the `PharmacyMedicineListing` pivot entity** — the single most structurally important table in Module 1 (per the client's explicit instruction and `architect.md` Section 4.1's emphasized design note). It cannot be built in Phase 1 because it depends on `Pharmacy` (completed in Phase 1) and `MasterMedicine` (defined in Phase 2). Phase 2 is early in the sequence — it is the second of three phases — and it is purpose-built around getting the pivot correct, since every Phase 3 feature (search, price comparison, storefront display) depends on quality listing data.

3. **Phase 3 delivers all customer-facing value** — search, discovery, price comparison, and the "notify me" feature. This is deliberately last because it consumes the data structures built in Phases 1 and 2. If we attempted Phase 3 before Phase 2, there would be no medicine listings to search or compare.

### Phase Size & Reviewability

Each phase is designed to produce a coherent, independently testable capability:

- **Phase 1:** "I can register as a pharmacy owner and see my storefront." ≈ 7–10 days for Backend + 5–7 days for Frontend
- **Phase 2:** "I can list medicines in my storefront and admin can normalize entries." ≈ 5–7 days for Backend + 5–7 days for Frontend  
- **Phase 3:** "A customer can find nearby pharmacies and compare medicine prices." ≈ 5–7 days for Backend + 7–10 days for Frontend

All estimates are planning ranges — the review process will refine them. If any phase grows beyond ~10 working days of specialist effort, it should be split further during execution.

---

## 2. Setup Phase (Tech Lead — executes solo)

**Before Phase 1 begins, I personally scaffold the entire project** and push it to `main`. No feature code — just infrastructure, configuration, and empty app shells.

### Backend Scaffold Tasks

| # | Task | Deliverable | References |
|---|---|---|---|
| S-01 | Create Django project `pharmacy_marketplace` with settings package structure: `settings/base.py`, `settings/dev.py`, `settings/staging.py`, `settings/production.py`. | Working Django project with environment-aware settings | `architect.md` Section 6, O-01 resolution |
| S-02 | Create the 6 Django apps as empty packages: `accounts`, `pharmacies`, `catalog`, `search`, `notifications`, `core`. Register all in `INSTALLED_APPS`. Use app configuration classes with proper `verbose_name`. | 6 app directories with `apps.py`, empty `models.py`, empty `urls.py` | `architect.md` Section 3.1 |
| S-03 | Configure `core` app with: shared `BaseModel` abstract class (UUID PK + `created_at`/`updated_at` timestamps), shared pagination classes (cursor-based — `CursorPagination` subclass with `ordering = '-created_at'`), shared DRF exception handler for the `{"error": {"code", "message", "details"}}` envelope format (per Section 5.1), shared i18n helper configuration (locale paths, default language English). | `core` package with reusable base classes | `architect.md` Sections 3.1.6, 5.1, 7.4 |
| S-04 | Configure `djangorestframework` globally in settings: `DEFAULT_PAGINATION_CLASS` pointing to the cursor-based page class, `DEFAULT_AUTHENTICATION_CLASSES` (JWT for API, session for web), `EXCEPTION_HANDLER` pointing to the custom handler. | DRF config in `settings/base.py` | `architect.md` Sections 5.1, 5.8 |
| S-05 | Configure `django-cors-headers` with allowed origins set from environment variable. | CORS configuration | `architect.md` Section 7.3 |
| S-06 | Configure database router for PostgreSQL with PostGIS engine in `settings/base.py` (actual connection details from environment). | Database config | `architect.md` Section 7.1 |
| S-07 | Create `requirements.txt` (or `pyproject.toml` with `setuptools`) with all dependencies: Django 5.2 LTS, djangorestframework, djangorestframework-simplejwt, django-cors-headers, psycopg2-binary, django-htmx, gunicorn, sentry-sdk. Pin versions. | Dependency file | `architect.md` Section 6 |
| S-08 | Create linter/formatter config: `ruff.toml`, `.pre-commit-config.yaml` with ruff + trailing-whitespace + end-of-file-fixer. | Linting config | Standard engineering practice |
| S-09 | Create `docker-compose.yml` with services: `django` (build from Dockerfile), `postgres` (postgis/postgis:16-3.5 image), `redis` (redis:7-alpine), `minio` (minio/minio for S3-compatible storage). Use volumes for data persistence. | Docker Compose for local dev | `architect.md` Section 9.1 |
| S-10 | Create `Dockerfile` for Django: Python 3.12-slim base, install system deps for PostGIS (GDAL, GEOS, PROJ), install Python deps, copy project, run with gunicorn. | Working Docker image | Standard Django Dockerfile pattern |
| S-11 | Create `.env.example` with all required environment variables (DB connection, Redis URL, MinIO/S3 keys, Django secret key, allowed hosts, CORS origins). Document each variable in comments. | Environment template | Standard practice |
| S-12 | Create GitHub Actions CI workflow (`.github/workflows/ci.yml`): trigger on push/PR to `main`, jobs for lint (ruff), test (pytest with PostgreSQL+PostGIS service container), build (Docker image). | CI pipeline | `architect.md` Section 6 |
| S-13 | Create initial migration infrastructure. `python manage.py makemigrations core && python manage.py migrate` should work with Docker Compose. | Working migration pipeline | Smoke test of the scaffold |

### Frontend Scaffold Tasks

| # | Task | Deliverable | References |
|---|---|---|---|
| S-14 | Create Flutter project `customer_app` with: folder structure (`lib/screens/`, `lib/widgets/`, `lib/services/`, `lib/providers/`, `lib/l10n/`), HTTP client package (`dio` or `http`), state management (`riverpod` — per O-05 resolution), routing (`go_router` or similar), location services (`geolocator`). | Working Flutter project skeleton | `architect.md` Section 3.2 |
| S-15 | Create Flutter i18n scaffolding: `lib/l10n/app_en.arb` (English strings), `lib/l10n/app_bn.arb` (Bengali — stub with English strings as placeholders for now). Configure `flutter_localizations` in `pubspec.yaml`. | i18n-ready Flutter project with English + Bengali stubs | `architect.md` Sections 3.2, 7.4 |
| S-16 | Create Django template base structure for the three web surfaces: `templates/customer/base.html`, `templates/owner/base.html`, `templates/admin/base.html` — each extending a shared `templates/base.html` that includes htmx (via `django-htmx`'s `{% htmx_script %}`), Alpine.js (loaded from CDN), CSRF header config for htmx. | Template hierarchy with htmx + Alpine.js | `architect.md` Section 3.3 |
| S-17 | Create Django template partials directory: `templates/partials/` with a `_medicine_card.html` placeholder, `_pharmacy_card.html` placeholder, `_pagination.html` placeholder. | Partial templates for reuse across surfaces | `architect.md` Section 3.3 |
| S-18 | Configure Django URL patterns with namespaced includes for the three web surfaces (separate `urls_customer.py`, `urls_owner.py`, `urls_admin.py` in the main project `urls.py`). Set up session auth login/logout views for web surfaces. | URL routing for all three web surfaces | `architect.md` Section 3.3 |
| S-19 | Create CSS/static file structure: `static/css/` with a base stylesheet, `static/js/` with Alpine.js init code if needed. | Static file scaffold | Standard practice |
| S-20 | Verify: `docker-compose up` brings all services online; Django runs with PostGIS connection; Flutter `flutter run` compiles and shows an empty app shell with navigation. | End-to-end scaffold verification | Smoke test |

### Setup Phase Completion Criteria

Everything listed above is done, reviewed by me (Tech Lead), and pushed to `main`. The project is in a state where:
- A developer can run `docker-compose up` and have a working Django dev environment with database, cache, and S3-compatible storage
- A developer can run `flutter run` and see a working app shell
- A developer can visit `http://localhost:8000/` and see a working Django site
- CI pipeline passes on `main`
- No feature code has been written yet (empty models, empty views, empty screens)

---

## 3. Phase 1: Foundation — Auth + Pharmacy Profiles

### Phase Goal

At the end of this phase, a pharmacy owner can register, log in, create their storefront with location pin, and view it. A customer can register and log in. An admin account exists for future use. No medicines or catalog exist yet.

### Dependencies

- Setup Phase completed and on `main`

### Backend Sub-section

**Branch:** `phase-1-backend-foundation`

| Task | Details | Files/Models | FR Mapping |
|---|---|---|---|
| B1-01 | Implement `accounts` models: single `User` model extending `AbstractBaseUser` with `phone` as the unique identifier, `role` CharField (choices: `customer`, `pharmacy_owner`, `admin`), `full_name`, `email` (nullable), `default_latitude`/`default_longitude` (nullable), `is_active`, `is_staff` (for admin access to Django admin). Use phone-based authentication backend. | `accounts/models.py` | FR-01, FR-03 |
| B1-02 | Implement `accounts` serializers: `CustomerRegistrationSerializer` (phone, full_name, password), `PharmacyOwnerRegistrationSerializer` (phone, full_name, password + nested pharmacy data), `LoginSerializer`, `UserProfileSerializer`. | `accounts/serializers.py` | FR-01, FR-03 |
| B1-03 | Implement `accounts` views: `CustomerRegistrationView`, `PharmacyOwnerRegistrationView`, `LoginView` (returns JWT access + refresh), `TokenRefreshView`, `UserProfileView`. All use DRF generic views or ViewSets. | `accounts/views.py` | FR-01, FR-03 |
| B1-04 | Implement `accounts` URLs: register under `/api/v1/auth/` as specified in architect.md Section 5.2. | `accounts/urls.py` | |
| B1-05 | Configure `djangorestframework-simplejwt`: access token 15min, refresh token 7 days, token obtained from login view. | `settings/base.py` | architect.md Section 5.2 |
| B1-06 | Implement `pharmacies` models: `Pharmacy` with fields per architect.md Section 4.1 (`name`, `owner_id` FK to User, `address_line`, `city`, `division`, `location` as `PointField` from GeoDjango, `dgda_license_number`, `pharmacist_name`, `pharmacist_registration_number`, `operating_hours` as JSONField, `phone`, `status` CharField, `is_verified` boolean (default False)). Create PostGIS GIST index on `location`. | `pharmacies/models.py` | FR-01, FR-02, FR-06 |
| B1-07 | Implement `pharmacies` serializers: `PharmacyRegistrationSerializer` (used nested in owner registration), `PharmacyDetailSerializer` (public view — no sensitive fields), `PharmacyUpdateSerializer`, `PharmacyLocationSerializer`. Validate that required pharmacist fields are present. | `pharmacies/serializers.py` | FR-01, FR-02 |
| B1-08 | Implement `pharmacies` views: `PharmacyCreateView` (POST, JWT-owner), `PharmacyDetailView` (GET, public — returns storefront data), `PharmacyUpdateView` (PATCH, JWT-owner), `PharmacyLocationUpdateView` (PATCH, JWT-owner — updates `location` PointField), `PharmacyDeactivateView` (PATCH, JWT-owner — sets status to `suspended`). | `pharmacies/views.py` | FR-04, FR-05, FR-06 |
| B1-09 | Implement `pharmacies` URLs: register under `/api/v1/pharmacies/` per architect.md Section 5.3. | `pharmacies/urls.py` | |
| B1-10 | Create `accounts` and `pharmacies` database migrations. Write unit tests for: user registration (customer + pharmacy owner), login + token refresh, pharmacy creation with location, pharmacy profile update, deactivation. Minimum 80% coverage on these two apps. | Migration files + test files | |
| B1-11 | Create initial admin user seed management command or data migration: one superuser admin account. | `accounts/management/commands/` | |

### Frontend Sub-section

**Branch:** `phase-1-frontend-auth`

| Task | Details | Files | FR Mapping |
|---|---|---|---|
| F1-01 | **Flutter:** Implement auth screens: `LoginScreen` (phone + password), `CustomerRegistrationScreen` (phone, full_name, password), `PharmacyOwnerRegistrationScreen` (phone, full_name, password, pharmacy_name, pharmacy_address, location map picker, license fields). Wire to `accounts` API endpoints. | `lib/screens/auth/` | FR-01, FR-03 |
| F1-02 | **Flutter:** Implement `AuthService` (login, register, token storage in `flutter_secure_storage`, auto-refresh interceptor on `Dio`). | `lib/services/auth_service.dart` | |
| F1-03 | **Flutter:** Implement navigation shell with guarded routes: unauthenticated → auth screens, authenticated → main app shell. `PharmacyOwnerRegistrationScreen` includes a map picker widget (using `flutter_map` with OpenStreetMap) for pinning location. | `lib/app.dart`, `lib/router.dart` | FR-02 |
| F1-04 | **Web (Django+htmx):** Create pharmacy owner registration page at `/owner/register/` with Django form + htmx (form submission replaces inline with a success message or validation errors). Include OpenStreetMap-based location picker (Leaflet.js via CDN). | `templates/owner/register.html` | FR-01, FR-02 |
| F1-05 | **Web (Django+htmx):** Create pharmacy owner login page at `/owner/login/` using Django's built-in `LoginView` with custom template. | `templates/owner/login.html` | |
| F1-06 | **Web (Django+htmx):** Create pharmacy owner dashboard shell at `/owner/dashboard/` with: sidebar navigation (Storefront, Medicines — disabled, grayed out for now), header with pharmacy name and status, main content area. This is a view-only placeholder — the actual storefront management comes in Phase 2. | `templates/owner/dashboard.html`, `templates/owner/base_dashboard.html` | FR-04 |
| F1-07 | **Web (Django+htmx):** Create customer registration and login pages (same pattern as owner but simpler — no pharmacy fields). | `templates/customer/register.html`, `templates/customer/login.html` | FR-01, FR-03 |
| F1-08 | **Flutter + Web:** Write integration tests for the full auth flow: register → login → token refresh → view protected endpoint. | Test files | |

### Review & Fix Sub-section (Tech Lead)

| Task | Details |
|---|---|
| R1-01 | Review Backend branch: verify User model uses phone as the unique identifier, JWT works end-to-end, Pharmacy model has the PostGIS PointField with correct GIST index, all API responses match the `{"error": {"code", "message", "details"}}` envelope format, no hardcoded strings. |
| R1-02 | Review Frontend branch (Flutter): verify Riverpod setup, token storage is secure, navigation guards work, auth service uses the correct API endpoints. |
| R1-03 | Review Frontend branch (Web): verify Django template auth works, session cookies are HTTPOnly + Secure, htmx CSRF header is correctly configured, map picker saves lat/lng correctly. |
| R1-04 | Fix any issues found in review. Re-review until clean. Merge to `main`. |

---

## 4. Phase 2: Medicine Catalog — The Pivot Phase

### Phase Goal

At the end of this phase, pharmacy owners can add, update, and bulk-upload medicine listings to their storefront. An admin can normalize unmatched entries via Django admin. The `PharmacyMedicineListing` pivot entity is fully operational with correct referential integrity. The 39 DGDA-authorized OTC medicines are seeded into the master catalog.

### Dependencies

- Phase 1 complete and on `main` (Pharmacy model + accounts exist)

### Backend Sub-section

**Branch:** `phase-2-backend-catalog`

| Task | Details | Files/Models | FR Mapping |
|---|---|---|---|
| B2-01 | Implement `catalog` models: `MasterMedicine` (brand_name, generic_name, manufacturer, dosage_form, strength, description, category, requires_prescription default False, is_active default True, UNIQUE constraint on brand_name+manufacturer+strength+dosage_form per architect.md Section 4.1), `PharmacyMedicineListing` (pharmacy_id FK to Pharmacy, master_medicine_id FK to MasterMedicine nullable, 5 unmatched_* free-text fallback fields, price Decimal(10,2), stock_status choices, is_active, normalization_status choices with default 'matched', partial index on normalization_status = 'unmatched_pending' per architect.md Section 4.1). | `catalog/models.py` | FR-07, FR-08, FR-09, FR-11, FR-12 |
| B2-02 | Implement `catalog` serializers: `MasterMedicineSerializer` (admin CRUD), `PharmacyMedicineListingSerializer` (create — accepts master_medicine_id OR 5 unmatched_* fields, validates that exactly one source is provided), `ListingUpdateSerializer` (price, stock_status — no change to which medicine it is), `ListingBulkUploadSerializer`. | `catalog/serializers.py` | FR-08, FR-09, FR-11 |
| B2-03 | Implement `catalog` views: `MasterMedicineListView` (GET, admin-only, paginated, searchable by brand_name/generic_name), `MasterMedicineCreateView` (POST, admin-only), `MasterMedicineUpdateView` (PATCH, admin-only), `ListingCreateView` (POST, JWT-owner — automatically sets pharmacy_id from authenticated user's pharmacy), `ListingUpdateView` (PATCH, JWT-owner), `ListingDeleteView` (DELETE, JWT-owner — soft delete via is_active=False), `ListingListView` (GET, public — lists active listings for a pharmacy), `ListingBulkUploadView` (POST, JWT-owner, accepts CSV file, processes per-row with error reporting). | `catalog/views.py` | FR-08, FR-09, FR-11, FR-12, FR-13 |
| B2-04 | Implement `catalog` URLs: register under `/api/v1/medicines/master/` and `/api/v1/listings/` per architect.md Sections 5.4, 5.5. | `catalog/urls.py` | |
| B2-05 | **Critical: Implement the bulk upload CSV endpoint.** Accept a CSV with columns: brand_name, generic_name, manufacturer, dosage_form, strength, price. For each row: attempt match against MasterMedicine (by brand_name+manufacturer+strength+dosage_form). If matched → create a listing with master_medicine_id. If not matched → create a listing with the 5 unmatched_* fields populated and normalization_status='unmatched_pending'. Return a results JSON with counts (matched, unmatched, errors) and per-row error details for failed rows. Validate total row count against a sane ceiling (e.g., 5000 rows max, file size 10MB max) with a clear error response if exceeded. | `catalog/views.py`, `catalog/utils/bulk_upload.py` | FR-13 |
| B2-06 | Extend Django Admin for catalog normalization: Register `MasterMedicine` admin with search_fields on brand_name, generic_name, manufacturer. Register `PharmacyMedicineListing` admin with a list filter for `normalization_status`. Create custom admin actions for normalization: "Link to master entry" (prompts to select MasterMedicine via popup), "Create new master entry from unmatched data", "Reject listing". Display all 5 unmatched_* fields in the list view for pending entries. | `catalog/admin.py` | FR-10, FR-37, FR-38 |
| B2-07 | Create data migration or management command to seed the 39 DGDA-authorized OTC medicines (from research.md Section A.4) into `MasterMedicine`. Set `requires_prescription=False` for all 39. Set `category='OTC'`. | Data migration in `catalog` | FR-14 (partial — OTC subset) |
| B2-08 | Create database migrations for `catalog` models. Write unit tests for: creating a listing with master_medicine_id, creating a listing with unmatched fields, updating price, deleting (soft), bulk upload CSV processing (valid rows, invalid rows, mixed), normalization via admin, the UNIQUE constraint on MasterMedicine, the partial index on normalization_status. | Migration files + test files | |

### Frontend Sub-section

**Branch:** `phase-2-frontend-catalog`

| Task | Details | Files | FR Mapping |
|---|---|---|---|
| F2-01 | **Web (Django+htmx):** Pharmacy owner — Medicine listing management page at `/owner/medicines/`. Table view of all active listings for their pharmacy with columns: Medicine Name, Price, Status, Actions (Edit, Remove). htmx-powered inline edit for price (click → becomes input field, save sends PATCH → row updates). | `templates/owner/medicines.html` | FR-08, FR-11 |
| F2-02 | **Web (Django+htmx):** Add medicine search/add form: typeahead input searches MasterMedicine via a dedicated search endpoint, htmx replaces a results dropdown. Selecting a master entry fills in the form with its data. If not found, a "Can't find it? Add manually" toggle reveals the 5 unmatched_* fields. Submit creates listing. | `templates/owner/medicines_add.html` | FR-08, FR-09 |
| F2-03 | **Web (Django+htmx):** Bulk upload page at `/owner/medicines/bulk/`. File upload form with a downloadable CSV template button. On submit, htmx streams progress updates and final results (matched X, unmatched Y, errors in N rows). Display errors inline with row numbers. | `templates/owner/medicines_bulk.html` | FR-13 |
| F2-04 | **Web (Django+htmx):** Admin normalization dashboard. Extend or create an admin-friendly view at `/admin/catalog/pharmacymedicinelisting/` using Django's built-in admin with the customizations from B2-06. Add a custom admin dashboard card showing "Pending normalization: {count}" with a direct link to filtered list view. | Django admin customization | FR-10, FR-34, FR-37 |
| F2-05 | **Web (Django+htmx):** Admin master catalog management view via Django admin at `/admin/catalog/mastermedicine/` with search, filter, and inline add/edit. | Django admin (built-in) | FR-38 |
| F2-06 | **Flutter:** Pharmacy owner screen (future — not needed in Module 1 since owners use the web dashboard. This can be a simple "Please use the web dashboard" message if accessed from mobile). | Placeholder only | |

### Review & Fix Sub-section (Tech Lead)

| Task | Details |
|---|---|
| R2-01 | Review Backend branch: The MOST IMPORTANT review in this module. Verify `PharmacyMedicineListing` model matches architect.md Section 4.1 exactly (nullable master_medicine_id + 5 unmatched_* fields, correct FK to Pharmacy with CASCADE, correct FK to MasterMedicine with SET NULL, Decimal(10,2) for price, normalization_status choices, partial index on 'unmatched_pending'). Verify the bulk upload endpoint correctly handles the match-or-fallback logic. Verify the UNIQUE constraint on MasterMedicine is enforced at DB level. Verify `requires_prescription` is present but has no business logic gating on it yet. |
| R2-02 | Review Frontend branch (Web): verify the add-medicine flow works end-to-end: typeahead → select from master → price → submit creates correct listing. Verify the unmatched fallback flow: "Can't find it?" → free text → submit creates listing with normalization_status='unmatched_pending'. Verify bulk upload CSV template download works, upload with progress feedback works, error reporting is clear. Verify Django admin customizations work for normalization. |
| R2-03 | Fix any issues found. Re-review. THIS IS THE PHASE WHERE GETTING THE PIVOT WRONG IS MOST EXPENSIVE — do not rush this review. Verify edge cases: what happens when a MasterMedicine entry is deleted (listings should have master_medicine_id set to NULL, not fail), what happens when a pharmacy is deleted (listings cascade), what happens when a listing with unmatched data is normalized (normalization_status changes to 'normalized_by_admin'). |
| R2-04 | Merge to `main` only after pivot correctness is confirmed. |

---

## 5. Phase 3: Customer Discovery — Search, Comparison & Notifications

### Phase Goal

At the end of this phase, a customer can open the app or website, see nearby pharmacies on a map/list, search for a medicine by name, see a price comparison table across in-range pharmacies, view a pharmacy's storefront, and subscribe for "notify me when ordering launches." This is the complete Module 1 experience.

### Dependencies

- Phase 2 complete and on `main` (listings exist to search against)

### Backend Sub-section

**Branch:** `phase-3-backend-discovery`

| Task | Details | Files/Models | FR Mapping |
|---|---|---|---|
| B3-01 | Implement `search` app views: `PharmacyRadiusListView` — GET `/api/v1/pharmacies/?lat={}&lng={}&radius={}` uses PostGIS `ST_DWithin` on `Pharmacy.location` to return pharmacies within radius, sorted by `ST_Distance`. Returns paginated response with `distance_km` computed on each result. | `search/views.py` | FR-15, FR-17, FR-18 |
| B3-02 | Implement `PharmacySearchView` — GET `/api/v1/pharmacies/search/?q={}&lat={}&lng={}` — text search on pharmacy name (using `icontains` or `SearchVector`/`SearchQuery` for full-text) filtered by radius. | `search/views.py` | FR-28, FR-29, FR-30 |
| B3-03 | Implement `MedicineSearchView` — GET `/api/v1/medicines/search/?q={}&lat={}&lng={}&radius={}` — THE CORE DIFFERENTIATOR. Searches `MasterMedicine` by brand_name or generic_name (using `icontains` or trigram similarity), joins through `PharmacyMedicineListing` to `Pharmacy`, filters by `ST_DWithin` on pharmacy location. Groups results by master_medicine_id, returns `lowest_price`, `highest_price`, `pharmacy_count`, and a sorted `pharmacies` array with name, distance, price (per architect.md Section 5.4 response shape). | `search/views.py` | FR-20, FR-21, FR-22 |
| B3-04 | Implement `MedicineDetailView` — GET `/api/v1/medicines/{id}/?lat={}&lng={}&radius={}` — returns the full comparison table: medicine info + all in-range pharmacies carrying it sorted by price (lowest first), per architect.md Section 5.4. | `search/views.py` | FR-23, FR-24 |
| B3-05 | Implement `PharmacyStorefrontView` — GET `/api/v1/pharmacies/{id}/` — returns pharmacy info + all active listings with prices, sortable by price or name (as querystring parameters). Reuses data from `catalog` app's listing queries. | `search/views.py` (or extend `pharmacies` views) | FR-31, FR-32, FR-33 |
| B3-06 | Add `PharmacyOpenNowFilter` — for FR-30: a query parameter `open_now=true` that filters pharmacies by whether `operating_hours` JSONB contains the current day+time. Implement as a DRF `BaseFilterBackend` on applicable views. | `search/filters.py` | FR-30 |
| B3-07 | Implement `search` URLs: register under `/api/v1/` per architect.md Sections 5.3, 5.4. | `search/urls.py` | |
| B3-08 | Add trigram index on `MasterMedicine.brand_name` and `MasterMedicine.generic_name` for performant fuzzy search. Create a database migration. | Migration file in `catalog` | NFR autocomplete target |
| B3-09 | Implement `notifications` models: `NotifySubscription` with `user_id` (nullable FK to User), `email` (nullable), `phone` (nullable), `master_medicine_id` (nullable FK), `pharmacy_id` (nullable FK), `created_at`. | `notifications/models.py` | FR-27 |
| B3-10 | Implement `notifications` serializers + views: `NotifySubscriptionCreateView` — POST `/api/v1/notifications/subscribe/` — accepts email or phone, optional medicine_id. If user is authenticated, auto-populate user_id and preferred contact. If unauthenticated, capture email or phone from request body. | `notifications/views.py` | FR-27 |
| B3-11 | Implement `notifications` URLs and register under `/api/v1/notifications/` per architect.md Section 5.6. | `notifications/urls.py` | |
| B3-12 | Implement admin dashboard stats endpoint: `AdminStatsView` — GET `/api/v1/admin/stats/` — returns counts of registered pharmacies, active listings, total customers, pending unmatched entries. JWT-admin only. | Endpoint (in admin-related views) | FR-34 |
| B3-13 | Write unit tests for: radius pharmacy search (verify pharmacies inside 2km returned, outside excluded), medicine search (verify results are grouped by master medicine, sorted correctly, within radius), medicine detail (verify comparison table is sorted by price), pharmacy search by name, open_now filter, notify subscription creation, admin stats endpoint. | Test files in `search`, `notifications` | |

### Frontend Sub-section

**Branch:** `phase-3-frontend-discovery`

| Task | Details | Files | FR Mapping |
|---|---|---|---|
| F3-01 | **Flutter:** Implement `LocationService` — requests location permission, gets current lat/lng, provides fallback for denied permission (manual text entry for location). | `lib/services/location_service.dart` | FR-15, FR-16 |
| F3-02 | **Flutter:** Implement `PharmacyListView` — default screen showing pharmacy cards within 2 km radius. Cards show name, distance, operating hours, open/closed indicator. Pull-to-refresh. Radius filter selector (presets 1/2/5/10 km). Toggle between list and map view (using `flutter_map` with OpenStreetMap tiles). | `lib/screens/pharmacy_list.dart` | FR-15, FR-17, FR-18, FR-19 |
| F3-03 | **Flutter:** Implement `MedicineSearchScreen` — search bar, debounced API calls (300ms), results grouped by medicine with lowest price, pharmacy count. Tap result → `MedicineDetailScreen`. | `lib/screens/medicine_search.dart` | FR-20, FR-21, FR-22 |
| F3-04 | **Flutter:** Implement `MedicineDetailScreen` — medicine info header, comparison table (pharmacy name, distance, price columns), sorted by price. "View Pharmacy" button → pharmacy storefront. "Notify me when ordering available" button → triggers subscription flow. | `lib/screens/medicine_detail.dart` | FR-23, FR-24, FR-27 |
| F3-05 | **Flutter:** Implement `PharmacyStorefrontScreen` — pharmacy info header, searchable list of medicines with prices, sortable by price/name. | `lib/screens/pharmacy_storefront.dart` | FR-31, FR-32, FR-33 |
| F3-06 | **Flutter:** Implement `PharmacySearchScreen` — search bar for pharmacy name, results with distance + address, tap → pharmacy storefront. Filter by open now. | `lib/screens/pharmacy_search.dart` | FR-28, FR-29, FR-30 |
| F3-07 | **Flutter:** Implement `NotifySubscriptionWidget` — inline in MedicineDetailScreen. If no user logged in → show email/phone input fields + submit button. If logged in → show "Notify me" button that uses registered contact. Show success confirmation after submission. | `lib/widgets/notify_subscription.dart` | FR-27 |
| F3-08 | **Web (Django+htmx):** Customer website homepage — auto-detect location via browser Geolocation API, default view: list of pharmacies within 2 km. Map toggle. Radius filter. Use Django template + htmx partial updates for filtering and radius change (no full page reloads). | `templates/customer/home.html`, `templates/partials/_pharmacy_list.html` | FR-15, FR-17, FR-18, FR-19 |
| F3-09 | **Web (Django+htmx):** Medicine search page — search input with htmx `hx-get` to search endpoint, results replace a `_search_results.html` partial on each keystroke (debounced). Each result card shows lowest price, pharmacy count. | `templates/customer/search.html`, `templates/partials/_search_results.html` | FR-20, FR-21, FR-22 |
| F3-10 | **Web (Django+htmx):** Medicine detail page — comparison table with pharmacy rows, "View Pharmacy" links, "Notify me" form (POST to notify endpoint via htmx, replace form with success message). | `templates/customer/medicine_detail.html`, `templates/partials/_comparison_table.html`, `templates/partials/_notify_form.html` | FR-23, FR-24, FR-27 |
| F3-11 | **Web (Django+htmx):** Pharmacy storefront page — same layout as Flutter, server-rendered with htmx sorting/searching within the storefront's medicine list. | `templates/customer/pharmacy_storefront.html` | FR-31, FR-32, FR-33 |
| F3-12 | **Web (Django+htmx):** Pharmacy search page — search input + results with distance and open_now filter. | `templates/customer/pharmacy_search.html` | FR-28, FR-29, FR-30 |
| F3-13 | **Web (Django+htmx):** Admin dashboard — basic stats page at `/admin/dashboard/` with total pharmacies, total listings, total customers, pending unmatched entries (data from B3-12). Auto-refresh via htmx polling (every 60 seconds). | `templates/admin/dashboard.html` | FR-34 |
| F3-14 | **Flutter + Web:** Write end-to-end integration tests: customer opens app → sees nearby pharmacies → searches medicine → views comparison → subscribes for notification. | Test files | |

### Review & Fix Sub-section (Tech Lead)

| Task | Details |
|---|---|
| R3-01 | Review Backend branch: verify PostGIS queries are correct (`ST_DWithin` with `GEOGRAPHY`, not `GEOMETRY`), medicine search results match the required API shape from architect.md Section 5.4 exactly, pagination is cursor-based on all list endpoints, open_now filter logic handles timezone correctly (BDT — Asia/Dhaka). Verify `notifications` app is minimal and has no business logic beyond storing the subscription. |
| R3-02 | Review Frontend branch (Flutter): verify location permission handling works (granted + denied paths), map view renders pharmacy pins correctly, comparison table is sorted by price, radius filter changes trigger a new API call, "notify me" flow works for both authenticated and unauthenticated users. |
| R3-03 | Review Frontend branch (Web): verify htmx-powered search is debounced and doesn't fire on every keystroke, partial updates replace the correct DOM elements, open_now filter works, the admin dashboard stats load correctly. Verify no hardcoded strings anywhere — all text goes through `{% trans %}` or the Flutter ARB files. |
| R3-04 | Fix issues found. Merge to `main`. Verify the complete Module 1 end-to-end flow: pharmacy registers → adds medicines → customer opens app → sees pharmacy in radius → searches medicine → compares prices → subscribes for notification. |

---

## 6. Post-Phase Tasks

After all three phases are merged to `main`:

| Task | Owner | Details |
|---|---|---|
| PT-01 | Tech Lead | Run full test suite: `pytest` for backend, `flutter test` for Android app, manual walkthrough of the web surfaces. Verify no regressions. |
| PT-02 | Tech Lead | Update `development_progress.md` with the final state of all three phases, consolidating from `backend_progress.md` and `frontend_progress.md`. |
| PT-03 | Tech Lead | Produce `progress-report.md` for the full Module 1 cycle (per the Senior Software Engineer — Team Lead's role definition): phase status, review cycle counts per phase, any unresolved issues, and a factual summary for PM go/no-go decision. |

---

## 7. Open Questions (Blockers to Planning)

| # | Question | How It Was Handled |
|---|---|---|
| Q-01 | No open questions block this plan. All decisions from the SRS Review (Cycle 1+2) and Architecture Review (Cycle 1) are incorporated. The client resolved O-01 through O-07 explicitly (architect.md Section 11.2). The rate-limit inconsistency between Section 7.3 and O-02 was resolved in the architecture document (settled at 60 req/min, within the client's approved 30–100 range). | No action needed. |

---

## 8. Phase Ordering Rationale (Summary)

The three phases are ordered to satisfy two constraints simultaneously:

1. **Dependency ordering:** `accounts` → `pharmacies` → `catalog` (pivot) → `search`/`notifications`. The app dependency chain in architect.md Section 2 (`search → catalog → pharmacies → accounts`) dictates that each phase builds the layer that the next phase depends on. Skipping or reordering would create a phase that references models that don't exist yet.

2. **Risk mitigation:** The `PharmacyMedicineListing` pivot entity is the highest-risk deliverable in Module 1. If its schema is wrong (nullable FK design, missing fields, incorrect constraint), every downstream feature (search, comparison, storefront display, future ordering) inherits that error. Placing it in Phase 2 ensures:
   - Phase 1 establishes the `Pharmacy` model it depends on
   - Phase 2 is early enough that any schema corrections can be made before Phase 3 consumes the data
   - Phase 3 developers read listing data through the pivot and will discover any structural issues immediately during integration testing

The pivot is not placed in Phase 1 because Phase 1's scope (auth + pharmacy profiles) is already the largest phase by model count (User + Pharmacy) and adding catalog models would make it un-reviewably large. Phase 2 is dedicated specifically to getting the pivot right — the entire phase is organized around that goal.

---

*This plan is ready for client review. Once approved, I execute the Setup Phase tasks and push to `main`, then the Backend and Frontend Specialists begin Phase 1 work on their respective branches.*
