# Frontend Phase 1 Progress — Web Auth & Dashboard Shells

**Branch:** `phase-1-design-revision`  
**Date:** July 2026  
**Status:** Build complete, tests passing (70/70)

---

## Phase 1 Design Revision — Color & Motion Re-skin

**Branch:** `phase-1-design-revision`  
**Date:** July 2026  
**Status:** Applied, tests passing (70/70)

### Token Replacement Summary

Complete replacement of the blue-led palette with a green-led, warm-neutral palette per `design.md` Section 2.1:

| Old Token | New Token | Old Value | New Value |
|---|---|---|---|
| `--color-primary` | `--color-primary` | `#2563eb` (blue) | `#059669` (emerald-600) |
| `--color-primary-dark` | `--color-primary-dark` | `#1d4ed8` | `#047857` (emerald-700) |
| — | `--color-primary-darker` *(new)* | — | `#065f46` (emerald-800) |
| `--color-primary-light` | `--color-primary-light` | `#dbeafe` | `#d1fae5` (emerald-100) |
| — | `--color-secondary` *(new)* | — | `#0d9488` (teal-600) |
| — | `--color-secondary-dark` *(new)* | — | `#0f766e` (teal-700) |
| — | `--color-secondary-light` *(new)* | — | `#ccfbf1` (teal-100) |
| `--color-gray-50` | `--color-surface` | `#f9fafb` | `#faf8f5` (warm) |
| `--color-gray-200` | `--color-border` | `#e5e7eb` | `#e8e4de` (warm) |
| `--color-gray-400` | `--color-muted` | `#9ca3af` | `#a8a29e` (warm) |
| `--color-gray-600` | `--color-secondary-text` | `#4b5563` | `#57534e` (warm) |
| `--color-gray-800` | `--color-heading` | `#1f2937` | `#292524` (warm) |
| `--color-gray-900` | `--color-strong-text` | `#111827` | `#1c1917` (warm) |
| `--color-owner-accent` | `--color-owner-accent` | `#7c3aed` (violet) | `#4f46e5` (indigo-600) |
| — | `--color-owner-accent-dark` *(new)* | — | `#4338ca` (indigo-700) |
| `--color-info-light` | *(removed)* use `--color-primary-light` | `#dbeafe` | `#d1fae5` |

### Motion Tokens Added (Section 2.7)

- `--transition-fast`: 100ms — button press, hover
- `--transition-base`: 200ms — validation, card hover
- `--transition-slow`: 300ms — step transitions, alert entrance
- `--easing-out`, `--easing-in`, `--easing-standard`, `--easing-bounce`
- Performance rule: only `transform`, `opacity`, `box-shadow`, `background-color`, `border-color`

### Component Changes Applied

| Component | Changes |
|---|---|
| **Button** | `.btn-primary` default → `--color-primary-dark`, hover → `--color-primary-darker`; motion tokens on transitions; active scale 0.97; disabled uses `--color-border`/`--color-muted` |
| **Card** | Transition timing → `var(--transition-base) var(--easing-standard)` |
| **Badge** | `.badge-price` variant added (`--color-secondary-light` bg, `--color-secondary-dark` text); `.badge-info` uses `--color-primary-light` |
| **Alert** | `.alert-info` uses `--color-primary-light` bg, `--color-primary-dark` text |
| **Input** | Focus ring uses `--color-primary-dark` (rgba(4,120,87,0.15)) |
| **Step Indicator** | Colors updated; current step ring → `rgba(4,120,87,0.2)`; completed → `--color-primary-dark` |
| **Sidebar** | Active/hover colors updated; transition `background-color` 100ms |
| **Header** | Customer header → `--color-primary-dark` (green) background with white text |
| **Stat Cards** | Hover shadow elevation added; icon colors updated |
| **Quick Action Cards** | Hover shadow transition added |
| **OTP** | Focus/filled border uses `--color-primary-dark`; focus ring updated |
| **Skeleton** | Background → `--color-border` |

### Accessibility — Reduced Motion

`prefers-reduced-motion: reduce` media query added per Appendix A:
- All transitions/animation durations → 0ms
- Skeleton pulse stops (static 0.4 opacity)
- OTP shake animation removed
- Button active transforms disabled

### Owner Surface Changes

- Welcome card gradient: violet `#6d28d9` → `--color-owner-accent-dark` (`#4338ca` indigo)
- Summary card icon `.primary` → `--color-primary-dark`
- All `--color-gray-*` references replaced in `owner.css`
- Card/quick-action hover transitions added

### Files Modified

- `static/css/base.css` — token replacement + motion + component updates
- `static/css/owner.css` — token references + transitions + gradient
- `static/css/customer.css` — token references
- `templates/404.html` — inline color tokens updated
- `templates/customer/login.html`, `register.html` — inline color tokens updated
- `templates/owner/login.html`, `register.html`, `dashboard.html` — inline color tokens updated
- `templates/partials/_otp_verify.html` — inline color token updated

### Test Results

**70/70 tests passing** (accounts test suite). No functional regressions — this is a pure CSS/visual change. Run with:
```
python manage.py test accounts --settings=pharmacy_marketplace.settings.test
```

### Tech Lead Cleanup Note — Hover-Elevation DRY

The same `transition: box-shadow var(--transition-base) var(--easing-standard)` + `:hover { box-shadow: var(--shadow-md); }` pattern is repeated 5× across `base.css` and `owner.css` (`.card`, `.stat-card`, `.quick-action-card`, `.summary-card`, and the second `.quick-action-card`). Extract into a reusable utility class (e.g., `.elevate-on-hover`) early in Phase 2 to avoid further duplication as new card-like components are added. Also consider re-consolidating `.site-header`/`.owner-header`/`.admin-header` layout props (padding, height, display, align-items) which were duplicated when the shared selector was split.

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
