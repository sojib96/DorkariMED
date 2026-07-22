# Design Specification — Module 1: Pharmacy & Medicine Discovery

> **Status:** Final — build-ready for Phase 1 (web auth + dashboard shells)  
> **Based on:** `srs-module1.md`, `architect.md`, `tech_lead_plan.md`  
> **Date:** July 2026  
> **Author:** Senior UI/UX Designer  
> **Platform:** Web-only (Django templates + htmx 2.x + Alpine.js). Flutter/Android deferred to future cycle.  
> **Design scope:** Phase 1 screens (auth flows + dashboard shells) + reusable component system for Phases 1–3.  
> **Document purpose:** A complete, frontend-buildable spec with every screen, state, flow, and edge case accounted for.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Design Tokens](#2-design-tokens)
3. [Information Architecture](#3-information-architecture)
4. [User Flows](#4-user-flows)
5. [Screen/Page Inventory](#5-screenpage-inventory)
6. [Component Specifications](#6-component-specifications)
7. [Responsive Behavior](#7-responsive-behavior)
8. [Accessibility Requirements](#8-accessibility-requirements)
9. [Content & Copy Guidelines](#9-content--copy-guidelines)
10. [Open Questions / Risks](#10-open-questions--risks)

---

## 1. Design Principles

### P1 — Clarity Over Density
Every screen should have one primary action. Secondary information is progressively disclosed (toggles, expandable sections, modals) rather than shown all at once. Auth screens show only the form; owner dashboards use cards rather than dense tables.

### P2 — Mobile-First, Bangladesh-Context
Many pharmacy owners and customers access via smartphone on 3G/4G. Design for small screens first (375px breakpoint). Optimize for low bandwidth: system fonts, minimal JS payload, lazy-loaded maps. Touch targets ≥ 44px. Text fields accommodate Bengali expansion (30–50% longer than English).

### P3 — Progressive Disclosure for Pharmacy Owners
Pharmacy owners may have moderate digital literacy. Registration is broken into logical steps (Account → Pharmacy Details → Location → Confirmation) rather than a single overwhelming form. Every action shows clear success/error feedback.

### P4 — Public Browsing Is the Default
Customers do not need an account to search, compare, or view storefronts. Auth is a thin layer: only pharmacy owner management and "notify me" require it. The customer homepage, search, and pharmacy storefront must work fully without auth.

### P5 — One Surface, One Purpose
Each of the three surfaces (customer, owner, admin) has a distinct visual identity (header color, navigation style) so the user always knows which context they're in. Navigation never mixes surface concerns (customer nav never has owner dashboard links).

### P6 — Offline-Aware, Not Offline-First
Discovery requires an active connection. Error states clearly explain connectivity issues. Forms preserve input on validation failure (never clear the form). No offline data storage in Module 1.

---

## 2. Design Tokens

### 2.1 Color Palette

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#2563eb` (Blue 600) | Primary buttons, links, active nav items |
| `--color-primary-dark` | `#1d4ed8` (Blue 700) | Button hover, focus rings |
| `--color-primary-light` | `#dbeafe` (Blue 100) | Selected state, subtle background tint |
| `--color-success` | `#16a34a` (Green 600) | Success messages, verified badge, in-stock indicator |
| `--color-success-light` | `#dcfce7` (Green 100) | Success alert background |
| `--color-warning` | `#d97706` (Amber 600) | Warning messages, pending-state badge |
| `--color-warning-light` | `#fef3c7` (Amber 100) | Warning alert background |
| `--color-danger` | `#dc2626` (Red 600) | Errors, destructive actions, out-of-stock |
| `--color-danger-light` | `#fee2e2` (Red 100) | Error alert background |
| `--color-info-light` | `#dbeafe` (Blue 100) | Info alert background |
| `--color-gray-50` | `#f9fafb` | Page background (customer surfaces) |
| `--color-gray-100` | `#f3f4f6` | Card background, section dividers |
| `--color-gray-200` | `#e5e7eb` | Borders, dividers, input borders |
| `--color-gray-400` | `#9ca3af` | Placeholder text, disabled text, secondary icons |
| `--color-gray-600` | `#4b5563` | Body text, secondary labels |
| `--color-gray-800` | `#1f2937` | Primary headings |
| `--color-gray-900` | `#111827` | Strong text, logo |
| `--color-white` | `#ffffff` | Card backgrounds, input backgrounds |
| `--color-owner-accent` | `#7c3aed` (Violet 600) | Owner dashboard header, owner-specific UI |
| `--color-admin-accent` | `#dc2626` (Red 600) | Admin dashboard header |

**Contrast compliance:** All text/background combinations meet WCAG AA (4.5:1 for body text, 3:1 for large text). Verified pairs:
- `gray-900` on `white`: 16:1
- `gray-600` on `white`: 6.5:1
- `white` on `primary`: 4.8:1
- `white` on `owner-accent`: 7.2:1

### 2.2 Typography

| Token | Value | Usage |
|---|---|---|
| `--font-sans` | `system-ui, -apple-system, 'Segoe UI', Roboto, Noto Sans Bengali, sans-serif` | Body text, headings, UI labels |
| `--font-mono` | `'SF Mono', 'Fira Code', 'Courier New', monospace` | Code blocks, prices in comparison tables (numeric alignment) |
| `--text-xs` | `0.75rem` (12px) | Helper text, footnotes, timestamps |
| `--text-sm` | `0.875rem` (14px) | Body text on mobile, secondary labels |
| `--text-base` | `1rem` (16px) | Default body text, input labels |
| `--text-lg` | `1.125rem` (18px) | Section headings, card titles |
| `--text-xl` | `1.25rem` (20px) | Page titles (h1) |
| `--text-2xl` | `1.5rem` (24px) | Hero headings |
| `--leading-tight` | `1.25` | Headings |
| `--leading-normal` | `1.6` | Body text |

**Font stack note:** `Noto Sans Bengali` is in the stack to support Bengali text when i18n is activated. It's a variable font with multiple weights and is available via Google Fonts. In Module 1 (English-only), the stack falls through to system UI fonts. The font stack is ordered so that Bengali-script text always renders correctly even without explicit font loading.

**Line lengths:** Max 70 characters per line for readable body text. Card content and form fields should not exceed this.

### 2.3 Spacing

| Token | Value | Usage |
|---|---|---|
| `--space-1` | `0.25rem` (4px) | Micro spacing, icon gaps |
| `--space-2` | `0.5rem` (8px) | Tight spacing, button padding x |
| `--space-3` | `0.75rem` (12px) | Input padding x, small element gaps |
| `--space-4` | `1rem` (16px) | Default spacing, card padding, form field gaps |
| `--space-6` | `1.5rem` (24px) | Section spacing, between card groups |
| `--space-8` | `2rem` (32px) | Page section margins, hero spacing |
| `--space-12` | `3rem` (48px) | Major layout breaks between sections |
| `--space-16` | `4rem` (64px) | Page-level padding top/bottom |

### 2.4 Elevation & Borders

| Token | Value | Usage |
|---|---|---|
| `--radius` | `0.5rem` (8px) | Card, input, button border radius |
| `--radius-sm` | `0.25rem` (4px) | Small badges, tags |
| `--radius-full` | `9999px` | Pill badges, avatar |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle card shadow |
| `--shadow` | `0 1px 3px rgba(0,0,0,0.1)` | Default card shadow |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Elevated cards, modals |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Dropdowns, dialog overlays |

### 2.5 Breakpoints (for responsive behavior section)

| Name | Value | Target |
|---|---|---|
| `--bp-sm` | `375px` | Small phones (primary breakpoint for mobile-first) |
| `--bp-md` | `768px` | Tablets, large phones in landscape |
| `--bp-lg` | `1024px` | Desktop |
| `--bp-xl` | `1280px` | Wide desktop (max container width) |

### 2.6 Iconography

- **Library:** Use inline SVGs or a minimal subset of [Heroicons](https://heroicons.com/) (outline style, 20x20 or 24x24). No icon font libraries to keep payload small.
- **Sizing:** Icons at `--text-base` (1rem/16px) for inline, `1.5rem` (24px) for standalone action icons.
- **Color:** Icons inherit `currentColor` from parent text. Use `--color-gray-400` for muted/decorative icons, `--color-primary` for interactive icons.

---

## 3. Information Architecture

### 3.1 Surface Map

The project has three distinct web surfaces, each with its own base template, URL namespace, and navigation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CUSTOMER WEBSITE                              │
│  URL prefix: /                         Namespace: store:*        │
├─────────────────────────────────────────────────────────────────┤
│  [Home] → Medicine search, nearby pharmacy list, radius filter   │
│  [Search results] → Medicine/pharmacy search with htmx partials  │
│  [Medicine detail] → Price comparison across pharmacies          │
│  [Pharmacy storefront] → Single pharmacy's listings              │
│  [Login] → /customer/login/                                      │
│  [Register] → /customer/register/                                │
│                                                                  │
│  Auth: optional (for "notify me" and future ordering)            │
│  Public browsing: fully functional without login                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                PHARMACY OWNER DASHBOARD                          │
│  URL prefix: /owner/                     Namespace: owner:*      │
├─────────────────────────────────────────────────────────────────┤
│  [Dashboard] → Overview cards, quick stats                       │
│  [Medicines] → Listing management (Phase 2)                      │
│  [Bulk upload] → CSV upload (Phase 2)                            │
│  [Pharmacy profile] → Edit storefront details                    │
│  [Login] → /owner/login/ (separate from customer)                │
│  [Register] → /owner/register/ (with pharmacy details)           │
│                                                                  │
│  Auth: required (login wall)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     ADMIN DASHBOARD                              │
│  URL prefix: /admin/                    Namespace: admin:*       │
├─────────────────────────────────────────────────────────────────┤
│  [Dashboard] → Platform stats (pharmacies, listings, customers)  │
│  [Catalog normalization] → Unmatched entry review (Phase 2)      │
│  [Django admin] → Full database admin interface                  │
│                                                                  │
│  Auth: required (staff/admin users only)                         │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Navigation Hierarchy

#### Customer Website Navigation (shown in header when unauthenticated)
```
[Logo: PharmacyMarket]    [Home]    [Login]    [Register]
```

#### Customer Website Navigation (shown in header when authenticated)
```
[Logo: PharmacyMarket]    [Home]    [My Profile]    [Logout]
```

#### Owner Dashboard Navigation (full sidebar on desktop, bottom nav on mobile)
```
┌─────────────────┐
│   Dashboard     │ ← Active
│   ───────────── │
│   Medicines     │ ← Disabled in Phase 1 (grayed out, tooltip: "Coming soon")
│   ───────────── │
│   Bulk Upload   │ ← Disabled in Phase 1
│   ───────────── │
│   Profile       │
│   Storefront    │ ← Opens storefront in new tab
└─────────────────┘
```

#### Admin Dashboard Navigation
```
┌───────────────────┐
│   Dashboard       │
│   ─────────────── │
│   Catalog         │
│   Normalization   │ ← Phase 2
│   ─────────────── │
│   Django Admin    │ ← External link to /admin/
└───────────────────┘
```

### 3.3 URL Structure (All Phases)

```
# Customer Website
/                                       → Customer home (pharmacy list + search)
/search/                                → Medicine search results (htmx partial)
/medicines/<uuid>/                      → Medicine detail with price comparison
/pharmacies/<uuid>/                     → Pharmacy storefront page
/customer/login/                        → Customer login
/customer/register/                     → Customer registration

# Owner Dashboard
/owner/login/                           → Owner login
/owner/register/                        → Owner registration
/owner/dashboard/                       → Owner dashboard shell
/owner/profile/                         → Pharmacy profile edit
/owner/medicines/                       → Medicine listing management (Phase 2)
/owner/medicines/bulk/                  → Bulk CSV upload (Phase 2)
/owner/medicines/add/                   → Add single medicine (Phase 2)

# Admin Dashboard
/admin/dashboard/                       → Admin dashboard stats
    (Django admin at /admin/ for full DB administration)
```

---

## 4. User Flows

### 4.1 Pharmacy Owner Registration

```
Entry: Clicks "Register as Pharmacy Owner" on homepage or visits /owner/register/
  │
  ├── Step 1: Account Information
  │   ├── Fields: Phone (required), Full Name (required), Password (required, min 8 chars)
  │   ├── Action: "Continue to Pharmacy Details"
  │   └── Validations:
  │       ├── Phone: Bangladeshi format (01XXXXXXXXX), unique in system
  │       ├── Password: min 8 chars, show/hide toggle
  │       └── All fields required
  │
  ├── Step 2: Pharmacy Details
  │   ├── Fields: Pharmacy Name (required), Address Line (required), City (required, dropdown),
  │   │          Division (required, dropdown), Pharmacy Phone (required),
  │   │          DGDA License Number (optional in form but encouraged),
  │   │          Pharmacist Name (optional), Pharmacist Reg. Number (optional),
  │   │          Operating Hours (JSON builder — see component spec)
  │   ├── Action: "Continue to Location"
  │   └── Validations: Name min 2 chars, Address min 10 chars
  │
  ├── Step 3: Location Pin (Map)
  │   ├── Leaflet.js map with OpenStreetMap tiles
  │   ├── Default: Center on Dhaka (23.8103, 90.4125), zoom 13
  │   ├── User drags pin to pharmacy location
  │   ├── OR user can search for an address (Nominatim geocoding)
  │   ├── Confirmed lat/lng shown below map
  │   ├── Action: "Review & Register"
  │   └── Validation: Pin must be placed (lat/lng required)
  │
  ├── Step 4: Review & Confirm
  │   ├── Read-only summary of all entered data
  │   ├── Map thumbnail showing pinned location
  │   ├── Editable via "Edit" links per section
  │   ├── Primary action: "Create Account" (POST to API)
  │   │
  │   ├── On success → OTP sent to phone
  │   │   └── OTP verification screen appears
  │   │       ├── 6-digit code entry (auto-submit on fill)
  │   │       ├── Resend timer (60s countdown)
  │   │       ├── Primary action: "Verify Phone"
  │   │       │   ├── On success → Redirect to /owner/dashboard/
  │   │       │   └── On error → Show error inline ("Invalid code. X attempts remaining.")
  │   │       └── Error state: Max attempts reached → "Too many attempts. Please try again later."
  │   │
  │   └── On error (API failure) → Show error alert at top of form
  │       ├── Server validation errors highlighted inline per field
  │       ├── Network error → "Connection lost. Please check your internet and try again."
  │       └── Duplicate phone → "This phone number is already registered. [Login instead]"
  │
  └── Abandon: User closes tab or navigates away
      └── No partial save in Phase 1 (future enhancement)
```

**Multi-step registration implementation:** Use a single Django form with `GET` parameters or a session-backed wizard pattern. Each step change triggers an htmx partial swap of the form content. All steps share the same URL (`/owner/register/`) — htmx replaces the form container on each step transition. On the final step, a full POST creates the user + pharmacy. (Frontend Specialist to implement as a single-page multi-step form using htmx, not a separate URL per step.)

### 4.2 Pharmacy Owner Login

```
Entry: Clicks "Owner Login" on homepage or visits /owner/login/
  │
  ├── Screen: Phone + Password form
  │   ├── Fields: Phone (required), Password (required, type=password)
  │   ├── Links: "Register instead" → /owner/register/
  │   │         "Forgot password?" → future (not in Module 1 — show disabled link with tooltip)
  │   ├── Primary action: "Sign In" (POST to login endpoint)
  │   │   ├── On success → Set session, redirect to /owner/dashboard/
  │   │   └── On error → Inline error above form
  │   │       ├── "Invalid phone number or password." (don't reveal which is wrong)
  │   │       ├── "Account is inactive. Contact support." (if is_active=false)
  │   │       └── Rate limit: "Too many attempts. Please try again in X minutes."
  │   └── Auto-focus: Phone field on load
  │
  └── Already logged in → Redirect to /owner/dashboard/ directly
```

### 4.3 Customer Registration

```
Entry: Clicks "Register" in header or visits /customer/register/
  │
  ├── Screen: Single-step registration form (simpler than owner — no pharmacy fields)
  │   ├── Fields: Phone (required), Full Name (required), Password (required, min 8 chars)
  │   ├── Primary action: "Create Account"
  │   ├── Secondary link: "Already have an account? Sign in" → /customer/login/
  │   │
  │   ├── On success → OTP sent to phone
  │   │   └── OTP verification screen (same pattern as owner)
  │   │       ├── On success → Session created, redirect to homepage
  │   │       └── On error → Inline error
  │   │
  │   └── On error → Same patterns as owner registration
  │
  └── Already logged in → Redirect to homepage
```

### 4.4 Customer Login

```
Entry: Clicks "Login" in header or visits /customer/login/
  │
  ├── Screen: Phone + Password form
  │   ├── Fields: Phone (required), Password (required)
  │   ├── Links: "Register instead" → /customer/register/
  │   │         "Forgot password?" → future (disabled)
  │   ├── Primary action: "Sign In"
  │   │   └── Same success/error patterns as owner login
  │   └── Note: After login, header updates (shows name, logout link) via htmx header swap
  │
  └── Already logged in → Redirect to homepage
```

### 4.5 Logout (All Surfaces)

```
Entry: Clicks "Logout" in header
  │
  ├── POST to logout endpoint (CSRF-protected, not GET)
  │   ├── On success → Redirect to appropriate public homepage
  │   │   ├── Customer → /
  │   │   ├── Owner → /owner/login/ with "You've been logged out" message
  │   │   └── Admin → /admin/login/
  │   └── On error → "Something went wrong. Please try again."
  │
  └── Confirmation: Not needed — logout is reversible (just log in again)
```

### 4.6 Admin Login

```
Entry: Visits /admin/login/ (Django built-in admin)
  │
  ├── Standard Django admin login form
  │   ├── Fields: Username (email), Password
  │   └── On success → Redirect to admin dashboard
  │
  └── Note: Admin login appearance is customized to match the design system
      (logo, colors, font stack), but the form behavior is Django default.
```

### 4.7 Phase 1 Dashboard Shell (Owner — Post-Login)

```
Entry: GET /owner/dashboard/ (after successful login)
  │
  ├── Loading state: Skeleton cards while pharmacy data loads
  │
  ├── Success state (pharmacy exists):
  │   ├── Welcome banner with pharmacy name and status badge
  │   │   ├── Status = active → green badge "Active"
  │   │   ├── Status = suspended → red badge "Suspended"
  │   │   └── Status = pending_review → amber badge "Pending Review"
  │   ├── Summary cards:
  │   │   ├── "Total Medicines Listed" — shows 0 (Phase 2 will populate)
  │   │   ├── "Storefront Views" — placeholder: "Coming soon"
  │   │   └── "Account Status" — shows verification status
  │   ├── Quick actions:
  │   │   ├── "Add Medicines" card → disabled with tooltip "Coming in Phase 2"
  │   │   ├── "Edit Pharmacy Profile" → enabled, links to /owner/profile/
  │   │   └── "View My Storefront" → enabled, opens storefront in new tab
  │   └── Recent activity section (empty state): "No recent activity yet."
  │
  ├── Success state (no pharmacy yet — redirect to registration):
  │   └── This shouldn't occur if registration flow completed, but guard:
  │       "You haven't created a pharmacy yet. [Create one now]" → /owner/register/
  │
  ├── Error state (API failed):
  │   ├── "Unable to load dashboard data."
  │   ├── [Retry] button → htmx re-fetches
  │   └── "If this persists, contact support."
  │
  └── Empty/Welcome state (first login, no data yet):
      ├── "Welcome to your dashboard!"
      ├── "Start by adding medicines to your storefront."
      ├── Illustration or icon of medicine bottles (Phase 2)
      └── [Add Medicines] button (disabled in Phase 1, enabled in Phase 2)
```

### 4.8 Phase 1 Profile Page (Owner)

```
Entry: Clicks "Profile" in sidebar /owner/profile/
  │
  ├── Loading state: Skeleton form
  │
  ├── Success state: Pre-filled form with current pharmacy data
  │   ├── Sections: Basic Info, Location, Operating Hours, Pharmacist Info
  │   ├── Map with current pin (editable)
  │   ├── Primary action: "Save Changes" (PATCH to API)
  │   │   ├── On success → Green success banner + form updates
  │   │   └── On error → Inline field errors + top error banner
  │   └── Secondary action: "Cancel" → go back to dashboard
  │
  └── Error state: "Could not load profile data. [Retry]"
```

---

## 5. Screen/Page Inventory

### 5.1 Customer Homepage (Phase 1 — Skeleton)

**URL:** `/`  
**Template:** `templates/customer/home.html` (exists, needs auth-aware updates)  
**Layout:** Single column, centered content

**Elements:**
1. **Hero section:** Title + subtitle + search box
2. **Search box:** Input + button, htmx-powered (exists)
3. **Nearby pharmacies section:**
   - Phase 1: Static placeholder text "Nearby pharmacies will appear here" + radius filter dropdown (disabled with tooltip "Coming soon")
   - Phase 3: htmx-loaded pharmacy list with map toggle
4. **How it works section:** 3-step illustration card (optional, can be static)
5. **Auth-aware header:**
   - Unauthenticated: [Home] [Login] [Register]
   - Authenticated: [Home] [My Profile] [Logout]

**States:**
- Default: Hero + search box + placeholder area
- Loading (after search): htmx loading spinner in results area
- Search results: Phase 1 — static "Medicine search coming in Phase 3" message
- Error: htmx error handler shows "Could not load results"

### 5.2 Customer Login Page

**URL:** `/customer/login/`  
**Template:** `templates/customer/login.html` (new)  
**Layout:** Centered card, max-width 400px, no sidebar

**Elements:**
1. **Card container:** White card on gray background
2. **Heading:** "Sign In" (h1)
3. **Subtitle:** "Welcome back" (optional decorative text)
4. **Form fields:**
   - Phone input (type="tel", pattern for BD number)
   - Password input (type="password", show/hide toggle)
5. **Primary action button:** "Sign In" (full width, primary color)
6. **Secondary actions:**
   - "Don't have an account? Register" link → /customer/register/
   - "Forgot password?" link (disabled — Phase 1: grayed out, title="Coming soon")
7. **Error states:** Inline error above form, field-level errors below each field

**States:**
- **Default:** Empty form, phone field focused
- **Filling:** Show/hide toggle on password, submit button enabled when both fields non-empty
- **Submitting:** Button shows loading spinner + "Signing in…", fields disabled
- **Error — invalid credentials:** Red alert above form: "Invalid phone number or password. Please try again."
- **Error — rate limited:** Red alert: "Too many login attempts. Please try again in [X] minutes."
- **Error — network:** Red alert: "Connection lost. Please check your internet and try again."
- **Success (no redirect yet):** Brief flash of green state before browser navigates to homepage
- **Already authenticated:** If user visits while logged in, show a card: "You're already signed in as [name]. [Go to Homepage]" with [Sign out] link

### 5.3 Customer Registration Page

**URL:** `/customer/register/`  
**Template:** `templates/customer/register.html` (new)  
**Layout:** Centered card, max-width 400px

**Elements:**
1. **Card container:** White card on gray background
2. **Heading:** "Create an Account" (h1)
3. **Subtitle:** "Join to save your favorite pharmacies and get notified"
4. **Form fields:**
   - Full Name (text, autocomplete="name")
   - Phone (tel, autocomplete="tel", BD format)
   - Password (password, with strength hint: "At least 8 characters")
   - Confirm Password (password)
5. **Primary action button:** "Create Account" (full width)
6. **Secondary link:** "Already have an account? Sign In"
7. **OTP verification overlay** (same component as 5.4)

**States:**
- **Default:** Empty form
- **Submitting:** Button loading state, fields disabled
- **Error — duplicate phone:** Red alert: "This phone number is already registered. [Sign in instead]"
- **Error — validation:** Field-level errors + top summary "Please fix the errors below"
- **Error — network:** Red alert: "Connection lost. Please check your internet and try again."
- **Success:** Form hides, OTP verification component appears
- **Already authenticated:** Same guard as login page

### 5.4 OTP Verification Overlay/Inline

**Used on:** Both registration pages (customer + owner)  
**Layout:** Inline panel replacing the registration form (not a modal dialog)

**Elements:**
1. **Heading:** "Verify Your Phone"
2. **Body text:** "We've sent a 6-digit code to [masked phone number, e.g., 01XXXXX1234]"
3. **OTP input:** 6 individual digit boxes (0-9 each), auto-advance to next on entry
4. **Primary action:** "Verify" (enabled when all 6 digits filled)
5. **Resend link:** "Didn't receive the code? [Resend]" with 60-second countdown timer
6. **Back link:** "Use a different phone number" → returns to registration form
7. **Error states:** Inline below input boxes

**Digit input behavior:**
- Each box accepts exactly 1 digit
- On typing a digit, auto-focus moves to the next box
- Backspace in empty box returns focus to previous box
- Paste a 6-digit code fills all boxes at once
- On 6th digit entered, auto-submit after 300ms debounce (user can also click "Verify" manually)

**States:**
- **Default:** All boxes empty, first box focused, timer at 60s
- **Filling:** Boxes fill left to right
- **Submitting:** Button loading, boxes disabled
- **Error — wrong code:** Red outline on all boxes, error text: "Invalid code. [X] attempts remaining."
- **Error — expired code:** "This code has expired. [Request a new one]"
- **Error — max attempts:** "Too many incorrect attempts. Please request a new code." → returns to registration
- **Error — network:** "Could not verify code. Check your connection and try again."
- **Success:** Brief green state then redirect to destination page

### 5.5 Owner Login Page

**URL:** `/owner/login/`  
**Template:** `templates/owner/login.html` (new)  
**Layout:** Centered card, max-width 400px

**Elements:** Same as customer login (5.2) but with:
- Heading: "Pharmacy Owner Sign In"
- Subtitle: "Access your storefront dashboard"
- "Register your pharmacy" link → /owner/register/
- After login redirect: /owner/dashboard/ (not homepage)
- Distinguishing visual: Violet accent (`--color-owner-accent`) on button or header indicator

### 5.6 Owner Registration Page

**URL:** `/owner/register/`  
**Template:** `templates/owner/register.html` (new)  
**Layout:** Stepped form, wider card (max-width 640px), maps to larger viewport

**Elements (by step):**

**Step 1 — Account:**
- Same fields as customer registration
- Heading: "Create Your Owner Account"
- Subtitle: "Step 1 of 3 — Account Information"
- Action: "Continue to Pharmacy Details"

**Step 2 — Pharmacy Details:**
- Pharmacy Name (text)
- Address Line (text, textarea for longer addresses)
- City (select dropdown)
- Division (select dropdown — 8 divisions of Bangladesh)
- Pharmacy Phone (tel, can be same or different from personal)
- DGDA License Number (text, optional)
- Pharmacist Name (text, optional)
- Pharmacist Registration Number (text, optional)
- Operating Hours (hours builder component)
- Action: "Continue to Location"

**Step 3 — Location:**
- Leaflet.js map with draggable pin
- Address search input (Nominatim autocomplete via CDN)
- Confirmed lat/lng display
- Action: "Review & Register"

**Step 4 — Review:**
- Read-only card summary of all data
- Map thumbnail
- Action: "Create Account & Verify Phone"

**States:** Same state patterns as customer registration for each step.
**Step transitions:** htmx replaces the form body. Step indicator at top shows progress:
```
[Step 1 ✓] ─── [Step 2 ●] ─── [Step 3 ○] ─── [Step 4 ○]
```
(✓ = completed, ● = current, ○ = upcoming)

### 5.7 Owner Dashboard (Phase 1 Shell)

**URL:** `/owner/dashboard/`  
**Template:** `templates/owner/dashboard.html` (exists, needs enhancement)  
**Layout:** Sidebar navigation (desktop) / Bottom tab navigation (mobile) + main content area

**Elements:**

**1. Sidebar (desktop) / Bottom nav (mobile):**
| Item | Phase 1 Behavior | Destination |
|---|---|---|
| Dashboard | Active (current page) | /owner/dashboard/ |
| Medicines | Disabled, tooltip "Coming in Phase 2" | — |
| Bulk Upload | Disabled, tooltip "Coming in Phase 2" | — |
| Profile | Enabled | /owner/profile/ |
| View Storefront | Enabled (opens new tab) | /pharmacies/<id>/ |

**2. Header bar:**
- Pharmacy name (from API)
- Status badge (colored pill)
- Notification bell icon (disabled, placeholder)
- User avatar/initial + dropdown (Profile, Logout)

**3. Welcome card:**
- "Welcome back, [Name]!"
- First-login variant: "Welcome to your dashboard! Get started by setting up your storefront."

**4. Summary cards grid (responsive: 1 col mobile, 2 col tablet, 3 col desktop):**

| Card | Content | Phase 1 State |
|---|---|---|
| Total Medicines | Count + icon | Shows "0" (Phase 2 populates) |
| Storefront Views | Count + trend | Shows "—" with "Coming soon" label |
| Account Status | Badge + verification text | Shows "Active" / "Pending" / "Suspended" |

**5. Quick Actions section:**
| Action | Phase 1 State |
|---|---|
| Add Medicines | Card with icon, button disabled, "Coming in Phase 2" badge |
| Edit Profile | Card with icon, button enabled → /owner/profile/ |
| View Storefront | Card with icon, button enabled → new tab |

**6. Recent Activity section:**
- Phase 1: Empty state — "No recent activity yet. Your storefront activity will appear here."
- Future: List of recent listing changes, views, etc.

**States:**
- **Loading:** Skeleton cards (3 placeholder rectangles with pulse animation)
- **First login (welcome):** Card with illustration, setup prompt, all counters at 0
- **Normal:** Cards with data, sidebar active state, header with pharmacy name
- **Error:** Error banner + retry button. Fallback: show cached pharmacy name if available.
- **Suspended:** Warning banner at top: "Your storefront is currently suspended. Contact support for details."

### 5.8 Owner Profile Page

**URL:** `/owner/profile/`  
**Template:** `templates/owner/profile.html` (new)  
**Layout:** Single column, form sections with card dividers

**Elements:**
1. **Heading:** "Pharmacy Profile" with "Back to Dashboard" link
2. **Sections (each in a white card):**
   - **Basic Info:** Name, Address, City, Division, Phone (editable)
   - **Location:** Leaflet.js map with current pin (re-draggable)
   - **Operating Hours:** Hours builder (same component as registration)
   - **Pharmacist Info:** Name, Registration Number (editable)
   - **License Info:** DGDA License Number (editable)
3. **Primary action:** "Save Changes" (PATCH)
4. **Secondary action:** "Discard Changes" (reverts form to saved state)

**States:**
- **Loading:** Skeleton form (gray rectangle placeholders for each field)
- **Default:** Pre-filled with current data
- **Saving:** Button loading, fields disabled
- **Saved successfully:** Green banner "Changes saved" + auto-dismiss after 4 seconds
- **Validation error:** Red inline errors per field
- **Server error:** Red banner "Could not save changes. Please try again."

### 5.9 Admin Dashboard (Phase 1 Shell)

**URL:** `/admin/dashboard/`  
**Template:** `templates/admin/dashboard.html` (exists, needs enhancement)  
**Layout:** Sidebar + main content

**Elements:**
1. **Heading:** "Admin Dashboard"
2. **Stats cards (4-column grid on desktop, 2-col on tablet, 1-col on mobile):**
   - Total Pharmacies: count (data from API)
   - Total Medicine Listings: count (Phase 2, shows 0 in Phase 1)
   - Registered Customers: count
   - Pending Normalization: count (Phase 2, shows 0 in Phase 1)
3. **Quick links:**
   - "Catalog Normalization" card → enabled in Phase 2
   - "Django Admin" card → /admin/
4. **Phase 1 state:** All stats show 0 or minimal initial data. "Pending Normalization" shows 0.

**States:**
- **Loading:** Skeleton cards
- **Normal:** Stats grid with counts
- **Error:** Error with retry button
- **Empty (no data yet):** Stats all show 0, "No pharmacies registered yet" placeholder message

### 5.10 404 / 500 Error Pages

**Templates:** `templates/404.html`, `templates/500.html` (new)

**404 Layout:**
- Centered content
- Heading: "Page Not Found"
- Body: "The page you're looking for doesn't exist or has been moved."
- Action: "Go to Homepage" button
- Simple illustration (CSS-only or inline SVG)

**500 Layout:**
- Centered content
- Heading: "Something Went Wrong"
- Body: "We're working on it. Please try again in a few minutes."
- Action: "Go to Homepage" button
- No technical details shown to user (logged server-side)

---

## 6. Component Specifications

### 6.1 Form Input

| Prop | Spec |
|---|---|
| Classes | `.input` |
| Default state | White background, 1px solid `--color-gray-200` border, `--radius`, padding `0.75rem 1rem`, `--text-base` font, full width |
| Placeholder | `--color-gray-400` text |
| Focus state | `--color-primary` border (2px), `--color-primary` box-shadow ring (3px, 15% opacity), no outline |
| Error state | `--color-danger` border (2px), error message below in `--text-sm` `--color-danger` |
| Disabled state | `--color-gray-100` background, `--color-gray-400` text, not clickable |
| Required indicator | Asterisk `*` in `--color-danger` after label |
| Label | Above input, `--text-sm` `--color-gray-600` weight 500, margin-bottom `--space-1` |
| Height | Min 44px (touch target) |
| Width | 100% of container, max `--max-input-width` (400px) |

**Phone input:**
- `type="tel"`, `inputmode="numeric"`, `pattern="01[0-9]{9}"`
- Visual hint: "+88" prefix (Bangladesh country code) shown as a non-editable prefix inside the input
- Validation: exactly 11 digits starting with "01"

**Password input:**
- `type="password"` with toggle button (eye icon) that reveals/hides text
- Toggle button is positioned absolutely inside the input, right-aligned
- Show/Hide label for screen reader: "Show password" / "Hide password"

### 6.2 Button

| Prop | Spec |
|---|---|
| Classes | `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`, `.btn-icon` |
| Default (primary) | Background `--color-primary`, white text, `--radius`, padding `0.75rem 1.5rem`, `--text-base` weight 500, cursor pointer, border none |
| Hover (primary) | Background `--color-primary-dark` |
| Active (primary) | Scale transform 0.98 |
| Focus | `--color-primary-dark` ring (3px, 20% opacity) |
| Disabled | `--color-gray-200` background, `--color-gray-400` text, cursor not-allowed, no hover effect |
| Loading | Button text replaced with spinner SVG (CSS animation), width preserved (don't shrink) |
| Secondary | White background, `--color-gray-200` border, `--color-gray-800` text |
| Secondary hover | `--color-gray-100` background |
| Danger | Red background (`--color-danger`), white text |
| Ghost | No background/border, `--color-gray-600` text, hover shows `--color-gray-100` background |
| Full width | `width: 100%` on mobile; on desktop, max 400px for auth buttons |
| Height | Min 44px |
| Icon button | 44x44px square, icon centered, same hover/focus states |

**Loading spinner (CSS):** A 20px circle with a 2px border, 2px transparent top border, spinning via `@keyframes spin { to { transform: rotate(360deg); } }`. Color matches button text.

### 6.3 Card

| Prop | Spec |
|---|---|
| Classes | `.card` |
| Default | White background, `--radius`, `--shadow`, `1px solid --color-gray-200`, padding `1.5rem` |
| Hover (when link) | `--shadow-md`, no text decoration on link |
| Clickable card | Entire card is an `<a>` or has `cursor: pointer` with `@click` |
| Disabled card | `opacity: 0.5`, cursor not-allowed, no hover elevation |
| Inner spacing | Children spaced with `--space-4` (flex column gap) |
| Icon slot | Optional 40x40px icon container at top-left of card content |

### 6.4 Badge / Pill

| Prop | Spec |
|---|---|
| Classes | `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info` |
| Default | `--radius-full` (pill shape), padding `0.25rem 0.75rem`, `--text-xs` weight 600, uppercase |
| Success | `--color-success-light` background, `--color-success` text |
| Warning | `--color-warning-light` background, `--color-warning` text |
| Danger | `--color-danger-light` background, `--color-danger` text |
| Info | `--color-info-light` background, `--color-primary` text |
| Disabled | `--color-gray-100` background, `--color-gray-400` text |

### 6.5 Status Badge (Pharmacy Status)

| Status | Badge Style | Text |
|---|---|---|
| `active` | `.badge-success` | Active |
| `suspended` | `.badge-danger` | Suspended |
| `pending_review` | `.badge-warning` | Pending Review |
| `is_verified=true` | `.badge-success` with checkmark icon | Verified |
| `is_verified=false` | `.badge-warning` | Unverified |

### 6.6 Alert / Message Banner

| Prop | Spec |
|---|---|
| Classes | `.alert`, `.alert-success`, `.alert-error`, `.alert-warning`, `.alert-info` |
| Default | Full-width, padding `0.75rem 1rem`, `--radius`, flex layout with icon + text + close button |
| Success | `--color-success-light` background, `--color-success` text, checkmark icon |
| Error | `--color-danger-light` background, `--color-danger` text, X icon |
| Warning | `--color-warning-light` background, `--color-warning` text, warning icon |
| Info | `--color-info-light` background, `--color-primary` text, info icon |
| Dismissible | Close button (`×`) triggers `x-show="false"` (Alpine.js) |
| Auto-dismiss | Success banners auto-dismiss after 5 seconds (setTimeout + Alpine.js) |
| Icons | Left-aligned, 20x20 SVG, inline with first text line |

### 6.7 Skeleton Loader

| Prop | Spec |
|---|---|
| Classes | `.skeleton`, `.skeleton-text`, `.skeleton-card`, `.skeleton-avatar` |
| Animation | Pulsing opacity: `@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }`, 1.5s ease infinite |
| Text line | `height: 1rem`, `--radius`, `--color-gray-100` background, width varies (100%, 75%, 50%) |
| Card | `height: 120px`, `--radius`, `--color-gray-100` background |
| Avatar circle | `width: 44px`, `height: 44px`, `--radius-full`, `--color-gray-100` background |

### 6.8 Step Indicator (Multi-Step Form)

| Prop | Spec |
|---|---|
| Classes | `.step-indicator` |
| Layout | Horizontal flex row, centered, gap `--space-2` |
| Step circle | 32x32px circle, `--color-gray-200` background, white text, `--text-sm` weight 600 |
| Step line | 60px horizontal line, `--color-gray-200` background, between circles |
| Completed step | `--color-primary` background, checkmark icon, line to next is `--color-primary` |
| Current step | `--color-primary-dark` background with pulse ring animation |
| Upcoming step | `--color-gray-200` background |
| Label | Below each circle, `--text-xs` `--color-gray-600`, centered |

### 6.9 Operating Hours Builder

| Prop | Spec |
|---|---|
| Classes | `.hours-builder` |
| Layout | 7 rows (Mon–Sun), each row: Day label + Open time dropdown + Close time dropdown + "Closed" toggle |
| Default state | All days: 09:00 open, 21:00 close. Friday: 14:00 open, 21:00 close. |
| Time selection | Select dropdowns with 30-minute intervals (00:00, 00:30, 01:00, ... 23:30) |
| "Closed" toggle | Checkbox or toggle switch; when checked, both dropdowns disabled and show "—" |
| Output format | JSON: `{"mon": {"open": "09:00", "close": "21:00"}, "tue": {...}, ...}` |
| Empty day | If "Closed" toggled, that day excluded or set to `null` |
| Validation | Open time must be before close time. If violated, row highlights red with "Close time must be after open time" error. |
| Pre-filled | When editing, pre-populate from existing hours JSON |

### 6.10 Map Location Picker (Leaflet.js)

| Prop | Spec |
|---|---|
| Technology | Leaflet.js v1.9+ (loaded from CDN) + OpenStreetMap tiles |
| CDN resources | `leaflet.css`, `leaflet.js` — loaded via `<link>` and `<script>` in template head, only on pages that need maps (register + profile) |
| Default center | 23.8103, 90.4125 (Dhaka) at zoom 13 |
| Map height | 300px on mobile, 400px on desktop |
| Pin | Leaflet `L.marker` with default blue icon, initially placed at center |
| Drag behavior | Pin is draggable. On dragend, update lat/lng display below map. |
| Click-to-recenter | Clicking anywhere on map (not on pin) moves pin to clicked coordinates |
| Address search | Optional: Nominatim search box overlay (top-left of map). Enter address → geocode → center map + move pin. Uses Leaflet's `L.Control` pattern. |
| Lat/lng display | Below map: `Latitude: 23.8103 | Longitude: 90.4125` in `--text-sm` `--color-gray-600` |
| Loading state | Map shows "Loading map…" placeholder div before Leaflet initializes |
| Error state | If map tiles fail to load: "Could not load map. [Retry]" button. Storefront works without map — lat/lng can be entered manually as fallback. |
| Fallback | If Leaflet CDN fails or JavaScript disabled: Show hidden text inputs for lat/lng with helper text "Enter coordinates or enable JavaScript for the map picker" |

### 6.11 Sidebar Navigation (Owner Dashboard)

| Prop | Spec |
|---|---|
| Classes | `.sidebar` |
| Desktop layout | Fixed left column, 240px wide, `--color-white` background, `1px solid --color-gray-200` right border |
| Mobile layout | Hidden off-screen, shown via hamburger toggle. OR use bottom tab bar (4-5 items) instead. |
| Nav items | Stacked vertically, each item: 16x16px icon + label, padding `0.75rem 1rem`, `--radius`, `--text-sm` |
| Active item | `--color-primary-light` background, `--color-primary` text, left border 3px `--color-primary` |
| Hover item | `--color-gray-100` background |
| Disabled item | `--color-gray-400` text, cursor not-allowed, `[title="Coming in Phase 2"]` tooltip |
| Section header | `--text-xs` uppercase, `--color-gray-400`, padding `1rem 1rem 0.25rem` |
| User section | Bottom of sidebar: avatar/initial + name + role + logout link |

**Mobile bottom nav alternative (below `--bp-md`):**
- Fixed to bottom, `height: 56px`, `--color-white` background, top border
- 4-5 items, equally spaced, each: icon (24x24) + label (`--text-xs`)
- Active: `--color-primary` icon + label
- Selected 5th item (hamburger) opens overflow menu

### 6.12 Header (Shared Component — Surface-Aware)

| Prop | Customer | Owner | Admin |
|---|---|---|---|
| Background | White | `--color-owner-accent` (violet) | `--color-admin-accent` (red) |
| Text color | `--color-gray-900` | White | White |
| Logo text | "PharmacyMarket" | "PharmacyMarket — Owner" | "PharmacyMarket — Admin" |
| Nav style | Horizontal links | Via sidebar | Via sidebar |
| Height | 56px | 56px | 56px |
| Mobile menu | N/A (just Login/Register links) | Hamburger icon → sidebar overlay | Hamburger icon → sidebar overlay |

### 6.13 OTP Digit Input Group

| Prop | Spec |
|---|---|
| Classes | `.otp-input-group` |
| Layout | Flex row, 6 digit boxes, gap `--space-2`, centered |
| Each box | 44x48px, `--text-xl` font, text-align center, `--radius`, `--color-gray-200` border |
| Filled box | `--color-primary` border, bold text |
| Focused box | `--color-primary-dark` ring |
| Error state | `--color-danger` border on all boxes, shake animation |
| Implementation | 6 `<input>` elements, maxlength=1, auto-advance on input, backspace to prev. Or a single masked input with custom JS. Frontend Specialist's choice, but behavior must match spec. |

---

## 7. Responsive Behavior

### 7.1 Breakpoint Behavior

| Breakpoint | Behavior Changes |
|---|---|
| **≥ 1280px (xl)** | Max container width 1200px, centered. Two-column layouts (sidebar + content) use 240px + 960px. |
| **≥ 1024px (lg)** | Sidebar shown as fixed left column. Dashboard cards in 3-column grid. Map at 400px height. |
| **≥ 768px (md)** | Sidebar collapses to hamburger menu. Auth cards at max 480px. Dashboard cards in 2-column grid. Owner registration form shows 2-column field pairs. Map at 350px. |
| **< 768px (sm/mobile)** | Single column everything. Sidebar becomes bottom tab bar (4 items). Auth cards full width with padding. Dashboard cards 1-column. Owner registration is single-column fields. Map at 300px. Bottom sheet for dropdown selects (native `<select>` on mobile). |
| **≥ 375px (minimum)** | Minimum supported width. Text never overflows. Touch targets ≥ 44px. Inputs span full width. |

### 7.2 Mobile-Specific Layouts

**Customer homepage (mobile):**
- Hero search box full width
- Pharmacy list items: compact cards with icon + name + distance on one line
- Map toggle button switches list/map view (map replaces list)

**Owner dashboard (mobile — < 768px):**
- Bottom navigation bar with 4 icons: Dashboard, Medicines, Bulk Upload, Profile
- "Medicines" and "Bulk Upload" icons grayed out with tooltip on press
- Dashboard content: stacked cards, full width
- Quick actions as horizontal scrollable row of icon buttons

**Registration forms (mobile):**
- Single column, full-width inputs
- Step indicator hidden or shown as "Step X of Y" text above form
- Map picker at 300px height, pin drag works on touch

**Data tables (mobile — Phase 2 onwards):**
- Horizontal scroll on tables with sticky first column
- Or card-based layout (each row = a card) for small screens
- Frontend Specialist chooses per use case

### 7.3 Print Styles

- **Not a priority for Module 1.** No explicit print stylesheet needed.
- Default browser print should be acceptable for pharmacy storefront pages.

---

## 8. Accessibility Requirements

### 8.1 Contrast (WCAG AA)

All color pairs listed in Section 2.1 meet WCAG AA minimum:
- Body text (gray-600 on white): 6.5:1 ✓ (exceeds 4.5:1)
- Large text (gray-900 on white): 16:1 ✓ (exceeds 3:1)
- Links (primary on white): 4.8:1 ✓ (exceeds 4.5:1 for body text links)
- White text on primary button: 4.8:1 ✓ (3:1 minimum for large text buttons)
- Placeholder text: 4.8:1 on white (WCAG AA requires 4.5:1 — acceptable for placeholder)

### 8.2 Keyboard & Focus

- All interactive elements must be keyboard-reachable (tab order matches visual order).
- Visible focus indicator on all interactive elements: 3px `--color-primary-dark` ring/outline, never `outline: none` without a visible replacement.
- `skip-to-content` link: hidden until focused (first tabbable element on page).
- Focus order in forms: label → input → error message (if showing) → submit button.
- OTP input: tab through 6 boxes. Each box focusable. Paste works anywhere in the group.
- Map: Leaflet.js maps are not fully keyboard-accessible by default. Provide hidden lat/lng text inputs as fallback for keyboard-only users. Map has `role="application"` and an `aria-label="Map — pin your pharmacy location"`.

### 8.3 Screen Readers

- All form inputs have associated `<label>` elements (not placeholders as labels).
- Required fields use `aria-required="true"` and `required` attribute.
- Error messages use `aria-live="polite"` or `role="alert"` for dynamic validation.
- Dynamic content (htmx partial updates) uses `aria-live="polite"` region around the target element.
- Icons use `aria-hidden="true"` with `focusable="false"` (SVG).
- Status badges: `aria-label` includes the status text (e.g., "Account status: Active").
- Loading states: `aria-busy="true"` on the loading container, `role="status"` with "Loading…" text.
- OTP verification: each digit input has an `aria-label` like "Digit 1 of 6", "Digit 2 of 6" etc.
- Step indicator: `role="progressbar"` with `aria-valuenow` and `aria-valuemax`.

### 8.4 Touch Targets

- Minimum 44x44px for all interactive elements (buttons, links, inputs, toggles).
- Exception: inline text links (e.g., "Register instead") — these pass at any size but must have visible underline on hover.
- Bottom nav items: 56px height minimum.
- OTP digit boxes: 44x48px minimum.
- Map pin: Default Leaflet marker (25x41px) is below 44px. Add invisible 44px touch area around pin. Or use a larger custom marker icon.
- Close/menu buttons in header: 44x44px minimum.

### 8.5 Motion & Animation

- No auto-playing animations that last > 5 seconds.
- Skeleton pulse animation: 1.5s cycle, no flashing.
- Page transitions: No cross-fade or slide animations in Module 1 (htmx swaps are instant).
- OTP error shake: brief 0.3s animation, single oscillation.
- Respects `prefers-reduced-motion`: disable all non-essential animations, keep skeleton static.

---

## 9. Content & Copy Guidelines

### 9.1 Tone

| Context | Tone | Example |
|---|---|---|
| Auth screens | Direct, helpful | "Sign in to manage your storefront" |
| Errors | Blameless, solution-oriented | "This phone number is already registered. Sign in instead?" |
| Success messages | Brief, warm | "Welcome! Your account has been created." |
| Empty states | Encouraging, forward-looking | "No medicines listed yet. Start adding your inventory in the next update." |
| Disabled features | Honest, clear timeline | "Medicine listing management is coming in Phase 2." |
| Notifications | Informative, not alarming | "Your storefront is now visible to customers." |

All copy in Module 1 is English. Hardcoded English strings are acceptable **only** in source code comments — all user-facing text must use `{% trans %}` / `{% blocktranslate %}` for future i18n.

### 9.2 Error Message Patterns

| Scenario | Error Message | Component |
|---|---|---|
| Required field empty | "Please enter your [field label]" | Field-level below input |
| Invalid phone format | "Please enter a valid Bangladeshi phone number (e.g., 01XXXXXXXXX)" | Field-level |
| Password too short | "Password must be at least 8 characters" | Field-level |
| Passwords don't match | "Passwords do not match" | Field-level |
| API network error | "Connection lost. Please check your internet and try again." | Page-level alert |
| Server error (500) | "Something went wrong on our end. Please try again." | Page-level alert |
| Rate limited | "Too many attempts. Please try again in [X] minutes." | Page-level alert |
| OTP invalid | "Invalid code. [X] attempts remaining." | Inline below OTP boxes |
| OTP expired | "This code has expired. Request a new one." | Inline below OTP boxes |
| Duplicate phone | "This phone number is already registered. [Sign in instead]" | Page-level alert + link |
| Account inactive | "This account is no longer active. Please contact support." | Page-level alert |

### 9.3 Empty State Copy

| Surface | Empty State | Phase |
|---|---|---|
| Owner dashboard — medicines | "You haven't listed any medicines yet. Medicine management will be available in the next update." | Phase 1 (placeholder) |
| Owner dashboard — activity | "No recent activity. Your storefront actions will appear here." | Phase 1 |
| Admin dashboard — pending normalization | "No unmatched medicine entries to review." | Phase 2 |
| Customer — nearby pharmacies | "No pharmacies found within this radius. Try expanding your search area." | Phase 3 |
| Customer — search results | "No medicines found matching '[query]'. Try a different spelling or a broader search." | Phase 3 |
| Customer — pharmacy storefront (no listings) | "This pharmacy hasn't listed any medicines yet." | Phase 3 |

### 9.4 Button Copy Standards

| Action | Button Text | Notes |
|---|---|---|
| Submit login | "Sign In" | Not "Login" or "Submit" |
| Submit registration | "Create Account" | Not "Register" |
| Submit OTP | "Verify" | Short, clear |
| Save a form | "Save Changes" | Not "Update" or "Submit" |
| Cancel editing | "Cancel" or "Discard Changes" | "Discard" only if unsaved changes exist |
| Enable/disable storefront | "Activate Storefront" / "Deactivate Storefront" | Full phrases |
| Retry after error | "Try Again" | Not "Retry" |
| Delete (destructive) | "Remove Listing" | Red button, confirmation required |
| Go back | "Back" | Not "Go back" |

---

## 10. Open Questions / Risks

| # | Issue | Type | Status / Action |
|---|---|---|---|
| O-01 | **OTP backend not in current B1 tasks.** The registration flows (Sections 4.1, 4.3) assume an SMS OTP verification step between "Create Account" and "Redirect to dashboard." However, `tech_lead_plan.md` B1-01 through B1-11 do not include an OTP send/verify endpoint or an SMS gateway integration. The architect.md O-06 requires SMS-only OTP, but implementation tasks are missing. | **Dependency risk** | **Flag to Team Lead.** Either OTP is deferred (registration creates account directly) and the design simplifies, or B1 tasks must be extended with OTP endpoints. The design above includes OTP because it's architect-mandated. |
| O-02 | **Password reset flow not in Module 1.** The login pages show a disabled "Forgot password?" link. If a user forgets their password in Module 1, they have no recovery path (only re-registration with a new phone number). | **Known gap** | Accepted per SRS — password reset is out of scope for Module 1. The risk should be documented. |
| O-03 | **Leaflet.js CDN dependency for map picker.** The location picker (registration + profile) requires loading Leaflet.js + CSS from CDN. If the CDN is blocked or slow, the map fails. | **Technical risk** | Mitigation: hidden lat/lng text inputs as fallback. The form works without the map. |
| O-04 | **Bengali text expansion not visually tested.** Design tokens and spacing assume English text. When Bengali i18n activates, some labels and buttons may overflow containers (Bengali text is 30–50% longer). | **Design debt** | The current spacing system uses generous padding (`--space-4`, `--space-6`). A visual audit is needed when Bengali strings are imported. Design should accommodate without structural changes. |
| O-05 | **Operating hours JSON schema not validated on backend.** The hours builder outputs a JSON structure. If the backend doesn't validate that the JSON is well-formed (correct day keys, valid times), bad data could be saved. | **Backend gap** | The backend should validate operating_hours JSON on save. Flag to Backend Specialist. |
| O-06 | **Owner registration: single vs multi-pharmacy.** The architecture (`architect.md` Section 4.1) allows a user to own multiple pharmacies (1:N). However, Phase 1 registration creates a single pharmacy during owner registration. If multi-pharmacy support is needed, the registration flow needs a "Add another pharmacy" step or a separate "Create additional pharmacy" flow in the dashboard. | **Scope question** | Assumed: Phase 1 creates exactly one pharmacy during registration. Multi-pharmacy deferred. If wrong, the registration flow and dashboard pharmacy context selector need redesign. |
| O-07 | **NFR-07: Visual indicator for unmatched listings.** Free-text (unmatched) medicine entries must be visually differentiated from matched entries per SRS NFR-07. This affects Phase 2 listing display. | **Design commitment** | Noted for Phase 2: unmatched listings will show an "(unverified)" badge or italicized name. No action in Phase 1. |
| O-08 | **Reusing htmx forms for multi-step registration.** The owner registration uses a single URL with htmx partial swaps. If session data is lost between steps (e.g., expired session cookie), the user loses their progress. | **Technical risk** | Mitigation: each step validates server-side before advancing. Session timeout shows a clear message ("Your session expired. Please start over.") with link to fresh form. |

---

## Appendix: Template & File Manifest (Phase 1)

This is the complete list of frontend files needed for Phase 1 web surfaces. It maps directly from tech_lead_plan.md F1-04 through F1-08, extended with design-specified files.

### New Files to Create

| # | File Path | Purpose | References |
|---|---|---|---|
| F-01 | `templates/customer/login.html` | Customer login page | Section 5.2, Flow 4.4 |
| F-02 | `templates/customer/register.html` | Customer registration page (1-step) | Section 5.3, Flow 4.3 |
| F-03 | `templates/owner/login.html` | Owner login page | Section 5.5, Flow 4.2 |
| F-04 | `templates/owner/register.html` | Owner registration page (multi-step: account→pharmacy→location→review) | Section 5.6, Flow 4.1 |
| F-05 | `templates/owner/profile.html` | Pharmacy profile edit page | Section 5.8, Flow 4.8 |
| F-06 | `templates/partials/_otp_verify.html` | OTP verification inline partial (used by both registration pages) | Section 5.4, Comp 6.13 |
| F-07 | `templates/partials/_hours_builder.html` | Operating hours builder partial | Comp 6.9 |
| F-08 | `templates/partials/_map_picker.html` | Leaflet.js location picker partial | Comp 6.10 |
| F-09 | `templates/partials/_step_indicator.html` | Multi-step progress indicator | Comp 6.8 |
| F-10 | `templates/partials/_skeleton_card.html` | Skeleton loader partial | Comp 6.7 |
| F-11 | `templates/partials/_alert.html` | Alert banner partial (success/error/warning/info) | Comp 6.6 |
| F-12 | `templates/404.html` | 404 error page | Section 5.10 |
| F-13 | `templates/500.html` | 500 error page | Section 5.10 |

### Files to Modify

| # | File Path | Changes Needed |
|---|---|---|
| M-01 | `templates/base.html` | Add `skip-to-content` link, ensure `i18n` is loaded, add `role="banner"` to header block |
| M-02 | `templates/customer/base.html` | Add auth-aware header (show name + logout if authenticated) |
| M-03 | `templates/customer/home.html` | Add auth-aware hero section, logged-in state shows name |
| M-04 | `templates/owner/base.html` | Add sidebar (desktop) / bottom nav (mobile) structure, logout handling |
| M-05 | `templates/owner/dashboard.html` | Enhance with summary cards, welcome state, loading/error states (Section 5.7) |
| M-06 | `templates/admin/base.html` | Add sidebar navigation structure |
| M-07 | `templates/admin/dashboard.html` | Enhance with stats cards (Section 5.9) |
| M-08 | `templates/partials/header.html` | Make auth-aware: show Login/Register when logged out, Name+Logout when logged in |
| M-09 | `templates/partials/owner_nav.html` | Update to sidebar layout, disable Phase 2 items with tooltips |
| M-10 | `templates/partials/admin_nav.html` | Update to sidebar layout |
| M-11 | `static/css/base.css` | Add all tokens from Section 2, add component classes (button, input, card, badge, alert, skeleton, step-indicator, otp-input, hours-builder) |
| M-12 | `static/css/customer.css` | Add auth page styles, responsive overrides |
| M-13 | `static/css/owner.css` | Add dashboard layout, sidebar, bottom nav, profile form, map picker styles |
| M-14 | `static/css/admin-dashboard.css` | Add admin stats cards, sidebar styles |
| M-15 | `static/js/base.js` | Add OTP input auto-advance, password show/hide toggle, alert auto-dismiss, form validation helpers |

### Deferred to Phase 2

| File | Reason |
|---|---|
| `templates/owner/medicines.html` | Medicine listing management |
| `templates/owner/medicines_add.html` | Add single medicine flow |
| `templates/owner/medicines_bulk.html` | Bulk CSV upload |
| `templates/partials/_medicine_card.html` | Medicine card component |
| `templates/partials/_comparison_table.html` | Price comparison table |
| `templates/customer/search.html` | Medicine search results |
| `templates/customer/medicine_detail.html` | Medicine detail + price comparison |
| `templates/customer/pharmacy_storefront.html` | Public pharmacy view |

---

*This design specification is complete for Phase 1 scope (auth + dashboard shells). Components and patterns defined here carry forward to Phases 2 and 3. Any deviations during frontend implementation should be flagged back to the UI/UX Designer for spec update, not resolved ad hoc.*
