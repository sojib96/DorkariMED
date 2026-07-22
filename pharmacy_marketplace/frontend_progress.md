# Frontend Phase 1 Progress — Web Auth & Dashboard Shells

**Branch:** `phase-1-frontend-web-auth`  
**Date:** July 2026  
**Status:** Build complete, tests passing (70/70)

---

## F1-04: Customer Registration (Web)

- **Template:** `templates/customer/register.html`
  - Phone (with +88 prefix), Full Name, Password, Confirm Password
  - htmx POST → `partials/_otp_verify.html` on success
  - Validation errors re-render form with inline field errors
- **View:** `accounts/views/web.py` → `CustomerRegistrationView`
- **States:** Default, validation error, duplicate phone, success (OTP partial)
- **Test:** `WebCustomerRegistrationTests` — 7 tests, all passing

## F1-05: Customer Login (Web)

- **Template:** `templates/customer/login.html`
  - Phone + Password form
  - htmx POST → HX-Redirect on success
  - Generic error message (no field disclosure)
- **View:** `accounts/views/web.py` → `CustomerLoginView`
- **States:** Default, invalid credentials, inactive user
- **Test:** `WebCustomerLoginTests` — 4 tests, all passing

## F1-06: Owner Registration (Web)

- **Template:** `templates/owner/register.html`
  - 4-step multi-step form: Account → Pharmacy Details → Location → Review
  - Step indicator (progress bar)
  - htmx step transitions (partial page swap)
  - Step 2: Pharmacy name, address, city, division, phone, DGDA license, pharmacist info, operating hours builder
  - Step 3: Leaflet.js map picker with draggable marker + manual coordinate fallback
  - Step 4: Review summary + submit
  - Back navigation between steps
  - Session-based data storage between steps
- **Components:** `_step_indicator.html`, `_hours_builder.html` (Alpine.js), `_map_picker.html` (Leaflet.js)
- **View:** `accounts/views/web.py` → `OwnerRegistrationView`
- **States:** Default, validation errors (per step), duplicate phone, server error
- **Test:** `WebOwnerRegistrationTests` — 8 tests, all passing (step 1 only; GIS-dependent steps need PostGIS)

## F1-07: Owner Login & Dashboard Shell

### Owner Login
- **Template:** `templates/owner/login.html`
  - Violet accent (--color-owner-accent)
  - Phone + Password form
  - Role check (rejects non-pharmacy-owner)
- **View:** `accounts/views/web.py` → `OwnerLoginView`
- **States:** Default, invalid credentials, wrong role, inactive
- **Test:** `WebOwnerLoginTests` — 4 tests, all passing

### Owner Dashboard Shell
- **Template:** `templates/owner/dashboard.html`
  - Welcome card (first-login variant vs normal)
  - Summary cards grid (Total Medicines, Storefront Views, Account Status)
  - Quick Actions (Add Medicines Phase 2, Edit Profile, View Storefront)
  - Recent Activity (empty state)
- **Templates:** `templates/owner/base.html`, `templates/partials/owner_nav.html`
  - **Sidebar (desktop):** 240px fixed, logo, nav items (Dashboard active, Medicines disabled, Bulk Upload disabled, Profile, Storefront), user section with avatar + logout
  - **Bottom nav (mobile < 768px):** 5 items (Dashboard, Medicines disabled, Profile, Storefront, Logout)
  - **Header bar:** Violet, hamburger toggle (mobile), logo, user avatar
- **View:** `accounts/views/web.py` → `OwnerDashboardView` (LoginRequiredMixin)
- **States:** Loading (skeleton cards), first-login welcome, normal, suspended (banner), error (retry), no-pharmacy
- **Test:** `WebOwnerDashboardTests` — 3 tests, all passing

## F1-08: Integration Tests

All 29 web auth integration tests in `accounts/tests.py`:
- `WebCustomerRegistrationTests` (7)
- `WebCustomerLoginTests` (4)
- `WebOwnerRegistrationTests` (8) — step 1 without GIS dependency
- `WebOwnerLoginTests` (4)
- `WebOwnerDashboardTests` (3)
- `WebLogoutTests` (3)

Total accounts test suite: **70 tests, all passing** (incl. existing API tests)

## Shared Infrastructure

### Design System (`static/css/base.css`)
- Design tokens (colors, typography, spacing, breakpoints)
- Auth cards, form inputs, phone prefix, password toggle, OTP input group
- Buttons (primary, secondary, ghost, danger), badges, skeleton loaders
- Dashboard layout (sidebar + main), step indicator, alerts, map picker, hours builder
- Mobile bottom nav, responsive breakpoints (375/768/1024/1280)

### JavaScript (`static/js/base.js`)
- OTP digit auto-advance + paste handler
- Password show/hide toggle
- Alert auto-dismiss (4s)
- htmx: loading states, error handler, CSRF token, HTML5 validation

### URL Structure
- `/customer/login/`, `/customer/register/`
- `/owner/login/`, `/owner/register/`
- `/owner/dashboard/`, `/owner/profile/`
- `/logout/`
- All under `auth:*` and `owner:*` namespaces

### Auth Integration
- Session-based auth (no JWT on web)
- OTP verification via `partials/_otp_verify.html` (API fetch to `/api/v1/auth/otp/`)
- i18n-ready (`{% trans %}`, `{% blocktrans %}`)

## Known Limitations / Deferred
1. **Full owner registration (steps 2-4) tests** need PostGIS environment (GDAL). Step 1 tested without GIS.
2. **`owner:profile`** is a placeholder view — full editing in Phase 2.
3. **OTP flow** depends on backend OTP endpoints (assumed functional).
4. **GDAL not available** in local test env — Pharmacy imports wrapped in `try/except`.
5. **Flutter/Android** deferred to future cycle per plan.
