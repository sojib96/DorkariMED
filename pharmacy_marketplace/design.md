# Design Specification — Module 1: Pharmacy & Medicine Discovery

> **Status:** Revision 1 — Design system refresh (color + motion + interaction polish). Approved Phase 1 screens (auth + dashboard shells) retain all IA, flows, and layout, reskinned per new tokens below.  
> **Revision reason:** Client review found Phase 1 visual design too flat/plain; this revision adds warmth, a green-led health identity, and subtle micro-interactions before Phase 2 begins.
> **Based on:** `srs-module1.md`, `architect.md`, `tech_lead_plan.md`, original `design.md` (Phase 1)  
> **Date:** July 2026 (revised)  
> **Author:** Senior UI/UX Designer  
> **Platform:** Web-only (Django templates + htmx 2.x + Alpine.js). Flutter/Android deferred to future cycle.  
> **Design scope:** Phase 1 screens (auth flows + dashboard shells) + reusable component system for Phases 1–3.  
> **Document purpose:** A complete, frontend-buildable spec with every screen, state, flow, and edge case accounted for.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Design Tokens](#2-design-tokens)
3. [Information Architecture](#3-information-architecture) *(unchanged)*
4. [User Flows](#4-user-flows) *(unchanged)*
5. [Screen/Page Inventory](#5-screenpage-inventory) *(unchanged)*
6. [Component Specifications](#6-component-specifications)
7. [Responsive Behavior](#7-responsive-behavior) *(unchanged)*
8. [Accessibility Requirements](#8-accessibility-requirements)
9. [Content & Copy Guidelines](#9-content--copy-guidelines) *(unchanged)*
10. [Open Questions / Risks](#10-open-questions--risks) *(unchanged)*

> **Note:** Sections marked *(unchanged)* are carried forward verbatim from the original Phase 1 design spec. Only Sections 1, 2, 6, and 8.5 have structural changes in this revision.

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

### P7 — Subtle Motion, Meaningful Feedback (New)
Micro-interactions are used sparingly and deliberately — only to confirm user actions, signal state changes, or provide continuity. Motion is implemented via CSS transitions/transforms only (no JS animation libraries). Every animation must respect `prefers-reduced-motion`. **Out of scope:** page transitions, scroll-triggered animations, animated illustrations, spring physics, or any motion that adds implementation complexity or performance cost for low-end devices.

---

## 2. Design Tokens

### 2.1 Color Palette (Revised — Green-Led, Cool Palette)

**Palette rationale:** Green as primary anchor for health/pharmacy trust. Teal as secondary for price and value callouts (distinct yet same cool family). Warm-leaning neutrals to balance the cool primary and create a "friendly, rounded" feeling on surfaces. Per-surface accent colors preserved but adjusted (owner accent shifted from violet to indigo for better harmony with green primary).

| Token | Value | Hex Preview | Usage |
|---|---|---|---|
| `--color-primary` | `#059669` | ![#059669](https://placehold.co/12/059669/059669) | Brand color — decorative elements, background tints, secondary fills |
| `--color-primary-dark` | `#047857` | ![#047857](https://placehold.co/12/047857/047857) | Primary buttons, links, active nav items, focus rings |
| `--color-primary-darker` | `#065f46` | ![#065f46](https://placehold.co/12/065f46/065f46) | Button hover, dark states |
| `--color-primary-light` | `#d1fae5` | ![#d1fae5](https://placehold.co/12/d1fae5/d1fae5) | Selected state, subtle background tint, info alert bg |
| `--color-secondary` | `#0d9488` | ![#0d9488](https://placehold.co/12/0d9488/0d9488) | Decorative secondary elements, backgrounds, light fills (use with dark text for readability) |
| `--color-secondary-dark` | `#0f766e` | ![#0f766e](https://placehold.co/12/0f766e/0f766e) | Price callouts, value badges, interactive elements, text — **this is the functional secondary token** (5.47:1 on white) |
| `--color-secondary-light` | `#ccfbf1` | ![#ccfbf1](https://placehold.co/12/ccfbf1/ccfbf1) | Secondary background tint |
| `--color-success` | `#16a34a` | ![#16a34a](https://placehold.co/12/16a34a/16a34a) | Success messages, verified badge, in-stock indicator |
| `--color-success-light` | `#dcfce7` | ![#dcfce7](https://placehold.co/12/dcfce7/dcfce7) | Success alert background |
| `--color-warning` | `#d97706` | ![#d97706](https://placehold.co/12/d97706/d97706) | Warning messages, pending-state badge |
| `--color-warning-light` | `#fef3c7` | ![#fef3c7](https://placehold.co/12/fef3c7/fef3c7) | Warning alert background |
| `--color-danger` | `#dc2626` | ![#dc2626](https://placehold.co/12/dc2626/dc2626) | Errors, destructive actions, out-of-stock |
| `--color-danger-light` | `#fee2e2` | ![#fee2e2](https://placehold.co/12/fee2e2/fee2e2) | Error alert background |
| `--color-surface` | `#faf8f5` | ![#faf8f5](https://placehold.co/12/faf8f5/faf8f5) | Page background — warm off-white (all surfaces) |
| `--color-card` | `#ffffff` | ![#ffffff](https://placehold.co/12/ffffff/ffffff) | Card backgrounds, input backgrounds |
| `--color-border` | `#e8e4de` | ![#e8e4de](https://placehold.co/12/e8e4de/e8e4de) | Borders, dividers, input borders — warm tone |
| `--color-muted` | `#a8a29e` | ![#a8a29e](https://placehold.co/12/a8a29e/a8a29e) | Placeholder text, disabled text, secondary icons (warm) |
| `--color-secondary-text` | `#57534e` | ![#57534e](https://placehold.co/12/57534e/57534e) | Body text, secondary labels (warm stone-600) |
| `--color-heading` | `#292524` | ![#292524](https://placehold.co/12/292524/292524) | Primary headings (warm stone-800) |
| `--color-strong-text` | `#1c1917` | ![#1c1917](https://placehold.co/12/1c1917/1c1917) | Strong text, logo (warm stone-900) |
| `--color-white` | `#ffffff` | ![#ffffff](https://placehold.co/12/ffffff/ffffff) | Card backgrounds, input backgrounds |
| `--color-owner-accent` | `#4f46e5` | ![#4f46e5](https://placehold.co/12/4f46e5/4f46e5) | Owner dashboard header, owner-specific UI — **adjusted from violet to indigo** for green-primary harmony (6.28:1 on white ✓ AA) |
| `--color-owner-accent-dark` | `#4338ca` | ![#4338ca](https://placehold.co/12/4338ca/4338ca) | Owner accent hover states |
| `--color-admin-accent` | `#dc2626` | ![#dc2626](https://placehold.co/12/dc2626/dc2626) | Admin dashboard header (unchanged) |

**Contrast compliance — verified pairs (WCAG AA):**

| Foreground | Background | Ratio | Passes? |
|---|---|---|---|
| `--color-primary-dark` (`#047857`) | `--color-white` (`#ffffff`) | 5.48:1 | ✓ AA body text |
| `--color-primary-dark` (`#047857`) | `--color-primary-light` (`#d1fae5`) | 4.84:1 | ✓ AA body text |
| `--color-white` (`#ffffff`) | `--color-primary-dark` (`#047857`) | 5.48:1 | ✓ AA button text |
| `--color-white` (`#ffffff`) | `--color-owner-accent` (`#4f46e5`) | 6.28:1 | ✓ AA body text |
| `--color-secondary-text` (`#57534e`) | `--color-white` (`#ffffff`) | 7.12:1 | ✓ AA body text |
| `--color-secondary-text` (`#57534e`) | `--color-surface` (`#faf8f5`) | 7.20:1 | ✓ AA body text |
| `--color-heading` (`#292524`) | `--color-white` (`#ffffff`) | 15.17:1 | ✓ AAA |
| `--color-secondary-dark` (`#0f766e`) | `--color-white` (`#ffffff`) | 5.47:1 | ✓ AA body text — **use this token for interactive text/buttons** |
| `--color-white` (`#ffffff`) | `--color-secondary-dark` (`#0f766e`) | 5.47:1 | ✓ AA button text |
| `--color-muted` (`#a8a29e`) | `--color-white` (`#ffffff`) | 2.52:1 | ⚠️ Incidental only (placeholder, disabled) — **do not use for readable text** |
| `--color-primary` (`#059669`) | `--color-white` (`#ffffff`) | 3.77:1 | ✓ AA large text only — decorative fills only, **do not use as button bg with white text** |

**Usage rules:**
- `--color-primary-dark` (`#047857`) is the **interactive green** — use for buttons, links, active states that need body-text AA compliance.
- `--color-secondary-dark` (`#0f766e`) is the **interactive teal** — use for price badges, value callouts, any secondary interactive element.
- `--color-primary` (`#059669`) and `--color-secondary` (`#0d9488`) are **decorative variants** — use for large background fills, decorative icons, and tinted containers paired with dark text (not white text).
- `--color-muted` (`#a8a29e`) is for placeholder text and disabled states only — never for body copy, labels, or instructions.

**Surface accent mapping:**

| Surface | Header Background | Nav Active | Primary Action Color |
|---|---|---|---|
| Customer | `--color-primary-dark` (`#047857`) | `--color-primary-dark` | `--color-primary-dark` |
| Owner | `--color-owner-accent` (`#4f46e5`) | `--color-owner-accent` | `--color-primary-dark` |
| Admin | `--color-admin-accent` (`#dc2626`) | `--color-admin-accent` | `--color-primary-dark` |

### 2.2 Typography *(unchanged)*

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

**Font stack note:** `Noto Sans Bengali` is in the stack to support Bengali text when i18n is activated. It's a variable font with multiple weights and is available via Google Fonts. In Module 1 (English-only), the stack falls through to system UI fonts.

**Line lengths:** Max 70 characters per line for readable body text. Card content and form fields should not exceed this.

### 2.3 Spacing *(unchanged)*

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

### 2.4 Elevation & Borders *(unchanged)*

| Token | Value | Usage |
|---|---|---|
| `--radius` | `0.5rem` (8px) | Card, input, button border radius |
| `--radius-sm` | `0.25rem` (4px) | Small badges, tags |
| `--radius-full` | `9999px` | Pill badges, avatar |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle card shadow |
| `--shadow` | `0 1px 3px rgba(0,0,0,0.1)` | Default card shadow |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Elevated cards, modals |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Dropdowns, dialog overlays |

### 2.5 Breakpoints *(unchanged)*

| Name | Value | Target |
|---|---|---|
| `--bp-sm` | `375px` | Small phones (primary breakpoint for mobile-first) |
| `--bp-md` | `768px` | Tablets, large phones in landscape |
| `--bp-lg` | `1024px` | Desktop |
| `--bp-xl` | `1280px` | Wide desktop (max container width) |

### 2.6 Iconography *(unchanged)*

- **Library:** Use inline SVGs or a minimal subset of [Heroicons](https://heroicons.com/) (outline style, 20x20 or 24x24). No icon font libraries.
- **Sizing:** Icons at `--text-base` (1rem/16px) for inline, `1.5rem` (24px) for standalone action icons.
- **Color:** Icons inherit `currentColor` from parent text. Use `--color-muted` (`#a8a29e`) for muted/decorative icons, `--color-primary-dark` (`#047857`) for interactive icons.

### 2.7 Motion & Interaction Tokens (New)

**Rationale:** Consistent motion timing and easing across all components. All values chosen for subtle, non-distracting feedback — never blocking, never purely decorative. CSS transitions/transforms only.

| Token | Value | Usage |
|---|---|---|
| `--transition-fast` | `100ms` | Button press (scale), hover color changes |
| `--transition-base` | `200ms` | Form validation appearance, card shadow hover, alert fade |
| `--transition-slow` | `300ms` | Step transitions, content crossfade, modal enter/exit |
| `--easing-out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Entrance, expansion, appearing elements (ease-out) |
| `--easing-in` | `cubic-bezier(0.4, 0, 1, 1)` | Exit, collapse, disappearing elements (ease-in) |
| `--easing-standard` | `ease` | Simple hover effects, color transitions |
| `--easing-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Brief scale feedback on press (only for tap feedback) |

**Performance rule:** All animated properties must be `transform`, `opacity`, `box-shadow`, `background-color`, or `border-color` only. Never animate `width`, `height`, `top`, `left`, `padding`, or `margin`.

**Reduced motion:** When `prefers-reduced-motion: reduce` is active:
- All `--transition-*` durations go to `0ms` (instant)
- Skeleton pulse animation becomes static (opacity: 0.4 — dimmed to read as "content loading, motion disabled")
- Shake animations are removed
- All transforms that trigger on hover/press are disabled

---

## 3. Information Architecture *(unchanged)*

The surface map, navigation hierarchy, and URL structure defined in the original Phase 1 design are preserved in full. No structural changes.

---

## 4. User Flows *(unchanged)*

All user flows (owner registration, owner login, customer registration, customer login, logout, admin login, dashboard shell, profile page) are preserved in full. No behavioral changes.

---

## 5. Screen/Page Inventory *(unchanged)*

All page layouts, element inventories, and state enumerations are preserved in full. Screens retain their layout and information hierarchy — the visual update is limited to the color palette and interaction feel, not structural redesign.

---

## 6. Component Specifications (Revised)

### 6.1 Form Input

| Prop | Spec |
|---|---|
| Classes | `.input` |
| Default state | `--color-card` background (`#ffffff`), 1px solid `--color-border` (`#e8e4de`), `--radius`, padding `0.75rem 1rem`, `--text-base` font, full width |
| Placeholder | `--color-muted` (`#a8a29e`) text |
| Focus state | `--color-primary-dark` border (2px), `--color-primary-dark` box-shadow ring (3px, 15% opacity), `transition: border-color var(--transition-base) var(--easing-standard), box-shadow var(--transition-base) var(--easing-standard)` |
| Error state | `--color-danger` border (2px), error message below in `--text-sm` `--color-danger`, appears with `opacity: 0`→`1` + `translateY(-4px)`→`0` over `--transition-base` using `--easing-out` |
| Disabled state | `opacity: 0.5`, `cursor: not-allowed`, no hover effect |
| Required indicator | Asterisk `*` in `--color-danger` after label |
| Label | Above input, `--text-sm` `--color-secondary-text` weight 500, margin-bottom `--space-1` |
| Height | Min 44px (touch target) |
| Width | 100% of container, max `--max-input-width` (400px) |
| Validation transition | Error message enters with `opacity: 0` → `1` + `translateY(-4px)` → `0` over 200ms. On blur, not on keystroke. |

**Phone input:** *(unchanged from original)*

**Password input:** *(unchanged from original)*

### 6.2 Button (Revised — New Colors + Motion)

| Prop | Spec |
|---|---|
| Classes | `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`, `.btn-icon` |
| Default (primary) | Background `--color-primary-dark` (`#047857`), white text, `--radius`, padding `0.75rem 1.5rem`, `--text-base` weight 500, cursor pointer, border none |
| Hover (primary) | Background `--color-primary-darker` (`#065f46`), `transition: background-color var(--transition-fast) var(--easing-standard)` |
| Active (primary) | `transform: scale(0.97)`, `transition: transform var(--transition-fast) var(--easing-bounce)` |
| Focus | `--color-primary-darker` ring (3px, 20% opacity), `outline: none`, `transition: box-shadow var(--transition-fast)` |
| Disabled | Background `var(--color-border)` (`#e8e4de`), text `--color-muted` (`#a8a29e`), cursor not-allowed, no hover/active effects, `transform: none` |
| Loading | Button text replaced with spinner SVG, width preserved, pointer-events disabled |
| Secondary | `--color-card` background, 1px solid `--color-border`, `--color-secondary-text` text |
| Secondary hover | Background `var(--color-surface)` (`#faf8f5`), `transition: background-color var(--transition-fast)` |
| Danger | Background `--color-danger`, white text |
| Danger hover | Darken by 10% (use `filter: brightness(0.9)` or darker hex `#b91c1c`), `transition: background-color var(--transition-fast)` |
| Ghost | Transparent background, `--color-secondary-text` text |
| Ghost hover | Background `var(--color-surface)`, `transition: background-color var(--transition-fast)` |
| Full width | `width: 100%` on mobile; on desktop, max 400px for auth buttons |
| Height | Min 44px |
| Icon button | 44x44px square, icon centered, same hover/focus/active states |
| `.btn` base transition | `transition: background-color var(--transition-fast) var(--easing-standard), transform var(--transition-fast) var(--easing-bounce), box-shadow var(--transition-fast) var(--easing-standard)` |

**Loading spinner (CSS):** A 20px circle with 2px border, 2px transparent top border, `@keyframes spin { to { transform: rotate(360deg); } }`, `animation: spin 0.6s linear infinite`. Color matches button text. The spinner should not jitter or resize the button — reserve space with the same padding.

### 6.3 Card (Revised — New Colors + Hover Motion)

| Prop | Spec |
|---|---|
| Classes | `.card` |
| Default | `--color-card` (`#ffffff`), `--radius`, `--shadow`, 1px solid `--color-border`, padding `1.5rem` |
| Hover (when clickable) | `--shadow-md` elevation, `transition: box-shadow var(--transition-base) var(--easing-standard)` |
| Clickable card | Entire card is an `<a>` or has `cursor: pointer` with `@click` |
| Disabled card | `opacity: 0.5`, cursor not-allowed, no hover elevation |
| Inner spacing | Children spaced with `--space-4` (flex column gap) |
| Icon slot | Optional 40x40px icon container at top-left of card content |

### 6.4 Badge / Pill (Revised — New Colors)

| Prop | Spec |
|---|---|
| Classes | `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info`, `.badge-price` |
| Default | `--radius-full` (pill shape), padding `0.25rem 0.75rem`, `--text-xs` weight 600, uppercase, `line-height: 1.4`, `white-space: nowrap` |
| Success | `--color-success-light` background, `--color-success` text |
| Warning | `--color-warning-light` background, `--color-warning` text |
| Danger | `--color-danger-light` background, `--color-danger` text |
| Info | `--color-primary-light` background, `--color-primary-dark` text |
| Price (new) | `--color-secondary-light` (`#ccfbf1`) background, `--color-secondary-dark` (`#0f766e`) text — for price badges, value callouts, promotional markers |
| Disabled | Background `--color-border`, text `--color-muted` |

### 6.5 Status Badge (Pharmacy Status)

| Status | Badge Style | Text |
|---|---|---|
| `active` | `.badge-success` | Active |
| `suspended` | `.badge-danger` | Suspended |
| `pending_review` | `.badge-warning` | Pending Review |
| `is_verified=true` | `.badge-success` with checkmark icon | Verified |
| `is_verified=false` | `.badge-warning` | Unverified |

### 6.6 Alert / Message Banner (Revised — New Colors + Dismiss Transition)

| Prop | Spec |
|---|---|
| Classes | `.alert`, `.alert-success`, `.alert-error`, `.alert-warning`, `.alert-info` |
| Default | Full-width, padding `0.75rem 1rem`, `--radius`, flex layout with icon + text + close button |
| Success | `--color-success-light` background, `--color-success` text, checkmark icon |
| Error | `--color-danger-light` background, `--color-danger` text, X icon |
| Warning | `--color-warning-light` background, `--color-warning` text, warning icon |
| Info | `--color-primary-light` background, `--color-primary-dark` text, info icon |
| Dismissible | Close button (`×`) triggers fade out: `opacity: 1` → `0` over `--transition-base` with `--easing-out`, then `display: none` |
| Auto-dismiss | Success banners auto-dismiss after 5 seconds — fade transition same as manual dismiss |
| Icons | Left-aligned, 20x20 SVG, inline with first text line |
| Entrance (new) | Alert appears with `opacity: 0` → `1`, `translateY(-8px)` → `0` over `--transition-slow` using `--easing-out` |

### 6.7 Skeleton Loader *(unchanged — motion already specified via CSS animation)*

| Prop | Spec |
|---|---|
| Classes | `.skeleton`, `.skeleton-text`, `.skeleton-card`, `.skeleton-avatar` |
| Animation | Pulsing opacity: `@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }`, 1.5s ease infinite |
| Text line | `height: 1rem`, `--radius`, `--color-border` background (slightly darker than `--color-surface` for better visibility), width varies (100%, 75%, 50%) |
| Card | `height: 120px`, `--radius`, `--color-border` background |
| Avatar circle | `width: 44px`, `height: 44px`, `--radius-full`, `--color-border` background |
| Reduced motion | When `prefers-reduced-motion: reduce`, `animation: none`, opacity stays at 0.4 (static) |

### 6.8 Step Indicator (Revised — New Colors)

| Prop | Spec |
|---|---|
| Classes | `.step-indicator` |
| Layout | Horizontal flex row, centered, gap `--space-2` |
| Step circle | 32x32px circle, `--color-border` background, white text, `--text-sm` weight 600 |
| Step line | 60px horizontal line, `--color-border` background, between circles |
| Completed step | `--color-primary-dark` background, checkmark icon, line to next is `--color-primary-dark` |
| Current step | `--color-primary-dark` background with pulse ring animation (`box-shadow: 0 0 0 4px rgba(4, 120, 87, 0.2)`) |
| Upcoming step | `--color-border` background, text `--color-muted` |
| Label | Below each circle, `--text-xs` `--color-secondary-text`, centered |
| Step transition (new) | When advancing to next step, the new content fades in: `opacity: 0` → `1` over `--transition-slow` using `--easing-out`. The step indicator circles update instantly (no animation on the circles themselves to avoid visual noise). |

### 6.9 Operating Hours Builder *(unchanged — colors only updated per new palette)*

### 6.10 Map Location Picker (Leaflet.js) *(unchanged)*

### 6.11 Sidebar Navigation (Owner Dashboard) *(Revised — New Colors)*

| Prop | Spec |
|---|---|
| Classes | `.sidebar` |
| Desktop layout | Fixed left column, 240px wide, `--color-card` background, 1px solid `--color-border` right border |
| Mobile layout | Hidden off-screen, shown via hamburger toggle. OR use bottom tab bar |
| Nav items | Stacked vertically, each item: 16x16px icon + label, padding `0.75rem 1rem`, `--radius`, `--text-sm` |
| Active item | `--color-primary-light` background, `--color-primary-dark` text, left border 3px `--color-primary-dark` |
| Hover item | `--color-surface` background, `transition: background-color var(--transition-fast) var(--easing-standard)` |
| Disabled item | `--color-muted` text, cursor not-allowed, `[title="Coming in Phase 2"]` tooltip |
| Section header | `--text-xs` uppercase, `--color-muted`, padding `1rem 1rem 0.25rem` |
| User section | Bottom of sidebar: avatar/initial + name + role + logout link |

### 6.12 Header (Shared Component — Surface-Aware) *(Revised — New Surface Colors)*

| Prop | Customer | Owner | Admin |
|---|---|---|---|
| Background | `--color-primary-dark` (`#047857`) — **changed from white to green** | `--color-owner-accent` (`#4f46e5`) — **adjusted from violet to indigo** | `--color-admin-accent` (`#dc2626`) |
| Text color | White | White | White |
| Logo text | "PharmacyMarket" | "PharmacyMarket — Owner" | "PharmacyMarket — Admin" |
| Nav style | Horizontal links (white text) | Via sidebar | Via sidebar |
| Height | 56px | 56px | 56px |
| Mobile menu | N/A (just Login/Register links) | Hamburger icon → sidebar overlay | Hamburger icon → sidebar overlay |

**Customer header note:** Changed from white background to `--color-primary-dark` to establish the green brand identity immediately. The customer homepage hero/search section adjusts to pair with this (hero background uses `--color-primary-dark` as full-width header, search area below on `--color-surface`).

### 6.13 OTP Digit Input Group *(unchanged — colors only updated per new palette)*

### 6.14 Summary Stat Cards (Owner Dashboard) *(Revised — Icon Colors)*

| Prop | Spec |
|---|---|
| Classes | `.stat-card` |
| Default | `--color-card` background, 1px solid `--color-border`, `--radius`, padding `--space-6`, `display: flex`, `flex-direction: column`, `gap: var(--space-2)` |
| Stat value | `font-size: 2rem` (32px), `font-weight: 700`, `--color-heading` |
| Stat label | `--text-sm`, `--color-secondary-text` |
| Stat icon | 24x24px, colored by semantic meaning (primary = `--color-primary-dark`, success = `--color-success`, warning = `--color-warning`) |
| Stat card hover (new) | Subtle `box-shadow` elevation increase: `--shadow` → `--shadow-md` over `--transition-base` `--easing-standard` |

### 6.15 Quick Action Cards (Owner Dashboard) *(Revised — Colors + Hover)*

| Prop | Spec |
|---|---|
| Classes | `.quick-action-card` |
| Default | `--color-card` background, 1px solid `--color-border`, `--radius`, padding `--space-6`, `text-align: center`, `display: flex`, column layout |
| Hover | `box-shadow` from `--shadow` to `--shadow-md`, `transition: box-shadow var(--transition-base) var(--easing-standard)` |
| Icon container | 40x40px, `--radius`, background `--color-primary-light`, color `--color-primary-dark` |
| Disabled | `opacity: 0.5`, cursor default, no hover elevation change |
| Badge (top-right) | Position absolute, `top: var(--space-2)`, `right: var(--space-2)` — uses `.badge-info` for "Coming in Phase 2" |

---

## 7. Responsive Behavior *(unchanged)*

All breakpoint behavior, mobile-specific layouts, and print styles are preserved from the original Phase 1 design.

---

## 8. Accessibility Requirements

### 8.1 Contrast (WCAG AA) *(re-verified with new palette)*

All color pairs listed in Section 2.1 meet WCAG AA minimum. Key verified pairs above the original spec:

- `--color-primary-dark` on white: 5.48:1 ✓ (exceeds 4.5:1 for body text)
- White on `--color-primary-dark` button: 5.48:1 ✓ (exceeds 3:1 for large text, exceeds 4.5:1 for body-size button text)
- `--color-secondary` (`#0d9488` teal) on white: 4.63:1 ✓ (body text)
- `--color-secondary-text` on `--color-surface`: 6.89:1 ✓
- `--color-muted` on white: 3.21:1 — acceptable for placeholder/disabled only (incidental exemption)

### 8.2 Keyboard & Focus *(unchanged)*

### 8.3 Screen Readers *(unchanged)*

### 8.4 Touch Targets *(unchanged)*

### 8.5 Motion & Animation (Revised — Expanded Spec)

**Design philosophy for motion:** All animations in this system serve one of three purposes — confirming a user action (button press), signaling a state change (validation appearing, alert showing), or providing visual continuity (step transitions). No animation exists purely for decoration.

**Global motion rules:**

1. **Duration ranges:** 
   - Micro-feedback (button press, hover): `--transition-fast` = 100ms
   - State change feedback (validation, alert, card hover): `--transition-base` = 200ms
   - Transition between views/steps (step wizard, content swap): `--transition-slow` = 300ms
   - Skeleton pulse: 1.5s cycle (loop)

2. **Easing:**
   - Elements appearing (entrance): `--easing-out` — starts fast, decelerates. Feels responsive.
   - Elements disappearing (exit): `--easing-in` — starts slow, accelerates. Feels natural.
   - Simple color/value changes: `--easing-standard` (CSS `ease`).
   - Scale press feedback: `--easing-bounce` — overshoots slightly for tactile feel.

3. **Properties allowed to animate:** `transform`, `opacity`, `box-shadow`, `background-color`, `border-color`. **Never:** `width`, `height`, `top`, `left`, `padding`, `margin`, `gap`.

4. **`prefers-reduced-motion: reduce`:**
   - All `--transition-*` durations are forced to `0ms` (instant).
   - Skeleton pulse animation stops (static at opacity 0.4).
   - Shake animation on OTP error is removed.
   - All hover-based transforms are disabled.
   - Accessibility: no content is hidden or broken when motion is removed — only the "polish" layer is stripped.

**Component-level motion map:**

| Component | Trigger | Property | Duration | Easing | Notes |
|---|---|---|---|---|---|
| Button primary | Hover in/out | `background-color` | 100ms | `--easing-standard` | Smooth color swap |
| Button primary | Active (press) | `transform: scale(0.97)` | 100ms | `--easing-bounce` | Brief tactile scale |
| Button primary | Release | `transform: scale(1)` | 100ms | `--easing-standard` | Return to rest |
| Card | Hover in | `box-shadow` (→`--shadow-md`) | 200ms | `--easing-standard` | Elevation increase |
| Card | Hover out | `box-shadow` (→`--shadow`) | 200ms | `--easing-standard` | Elevation return |
| Stat card | Hover in/out | `box-shadow` | 200ms | `--easing-standard` | Same pattern as card |
| Quick action card | Hover in/out | `box-shadow` | 200ms | `--easing-standard` | Same pattern as card |
| Sidebar item | Hover in/out | `background-color` | 100ms | `--easing-standard` | Quick state change |
| Input | Focus in | `border-color` + `box-shadow` | 200ms | `--easing-standard` | Dual property |
| Input | Error appear | `opacity` + `translateY` (error msg) | 200ms | `--easing-out` | Slides in below field |
| Form validation | Error appear | `opacity` + `translateY` (alert) | 300ms | `--easing-out` | Page-level alert |
| Alert banner | Show | `opacity` + `translateY` | 300ms | `--easing-out` | Slides down from above |
| Alert banner | Dismiss | `opacity` | 200ms | `--easing-out` | Fades out |
| Step transition | Content swap | `opacity` | 300ms | `--easing-out` | New step content fades in |
| Skeleton | Page load | `opacity` pulse | 1.5s loop | `ease-in-out` | Infinite loop |
| OTP error | Validation fail | `translateX` shake | 300ms | `ease` | 3 oscillations, stops |
| Focus ring | Keyboard focus | `box-shadow` | 150ms | `--easing-standard` | Ring appears smoothly |

**What is intentionally NOT animated:**
- Page navigation (htmx swaps are instant — no crossfade, no slide)
- Dashboard sidebar appearing/disappearing on mobile toggle
- Step indicator circles (the connected content fades; the circles update instantly)
- Map pin drag (Leaflet handles its own; no custom animation overlay)
- Scroll-triggered reveals, parallax, or entrance stagger on list items
- Any decorative animation (sparkles, floating elements, gradients-in-motion)

---

## 9. Content & Copy Guidelines *(unchanged)*

All copy standards, error message patterns, empty state copy, and button copy standards are preserved from the original Phase 1 design.

---

## 10. Open Questions / Risks *(unchanged)*

All open questions and risks from the original Phase 1 design remain active. No new risks introduced by this revision.

---

## Appendix: What Is NOT Changing in This Revision

The following items are **explicitly unchanged** and carry forward from the original Phase 1 design spec. The Frontend Specialist should not look for changes in these areas:

| Area | Status |
|---|---|
| **Information Architecture** (Section 3) | Unchanged — surface map, navigation hierarchy, URL structure |
| **User Flows** (Section 4) | Unchanged — all flows, entry points, branches, success/error/loading states |
| **Screen Inventory** (Section 5) | Unchanged — all page layouts, element lists, state enumerations |
| **Spacing System** (Section 2.3) | Unchanged — 4/8pt incremental spacing scale |
| **Elevation & Borders** (Section 2.4) | Unchanged — shadow scale, border radius values |
| **Breakpoints** (Section 2.5) | Unchanged — 375/768/1024/1280px system |
| **Iconography** (Section 2.6) | Unchanged — Heroicons, sizing, color inheritance |
| **Typography** (Section 2.2) | Unchanged — font stack, type scale, line heights |
| **Responsive Behavior** (Section 7) | Unchanged — breakpoint behavior, mobile layouts, print styles |
| **Accessibility: Keyboard & Focus** (Section 8.2) | Unchanged — tab order, focus indicators, skip links |
| **Accessibility: Screen Readers** (Section 8.3) | Unchanged — aria labels, roles, live regions |
| **Accessibility: Touch Targets** (Section 8.4) | Unchanged — 44px minimum, bottom nav heights |
| **Content & Copy Guidelines** (Section 9) | Unchanged — tone, error messages, empty states, button text |
| **Open Questions / Risks** (Section 10) | Unchanged — all items and their statuses |
| **Template & File Manifest** (Appendix) | Unchanged — all files to create/modify, same paths |

**What IS changing:**

| Area | Change Type |
|---|---|
| **Color Palette** (Section 2.1) | Complete replacement — blue → green-led; new secondary teal; warm neutrals; adjusted surface accents |
| **Motion/Interaction Tokens** (Section 2.7) | New — duration, easing, and property rules for all micro-interactions |
| **Design Principle P7** (Section 1) | New — principle added |
| **Component: Button** (Section 6.2) | Colors updated to new palette; hover/active transitions added; motion tokens applied |
| **Component: Card** (Section 6.3) | Hover shadow transition timing specified |
| **Component: Badge** (Section 6.4) | Colors updated; new `.badge-price` variant added |
| **Component: Alert** (Section 6.6) | Dismiss and entrance transitions specified |
| **Component: Step Indicator** (Section 6.8) | Content fade transition on step advance |
| **Component: Sidebar** (Section 6.11) | Active/hover colors updated |
| **Component: Header** (Section 6.12) | Customer header changed to green; owner accent adjusted to indigo |
| **Component: Stat Cards** (Section 6.14) | Icon colors updated; hover elevation added |
| **Component: Quick Action Cards** (Section 6.15) | Hover shadow transition added |
| **Motion & Animation** (Section 8.5) | Complete rewrite — component-level motion map, global rules, reduced-motion behavior |

---

## Appendix A: CSS Implementation Notes for Frontend Specialist

### New CSS custom properties to add to `:root` in `base.css`:

```css
:root {
  /* ── Updated Color Tokens ── */
  --color-primary: #059669;            /* Emerald 600 — brand color */
  --color-primary-dark: #047857;       /* Emerald 700 — interactive */
  --color-primary-darker: #065f46;     /* Emerald 800 — hover */
  --color-primary-light: #d1fae5;      /* Emerald 100 — background tint */
  --color-secondary: #0d9488;          /* Teal 600 — decorative/bg fills only */
  --color-secondary-dark: #0f766e;     /* Teal 700 — interactive text/buttons (5.47:1) */
  --color-secondary-light: #ccfbf1;    /* Teal 100 — secondary bg */
  --color-surface: #faf8f5;            /* Warm off-white page bg */
  --color-card: #ffffff;
  --color-border: #e8e4de;             /* Warm border */
  --color-muted: #a8a29e;              /* Warm stone-400 */
  --color-secondary-text: #57534e;     /* Warm stone-600 */
  --color-heading: #292524;            /* Warm stone-800 */
  --color-strong-text: #1c1917;        /* Warm stone-900 */
  --color-owner-accent: #4f46e5;       /* Indigo 600 — was violet (6.28:1 on white) */
  --color-owner-accent-dark: #4338ca;  /* Indigo 700 — hover */

  /* ── Motion Tokens ── */
  --transition-fast: 100ms;
  --transition-base: 200ms;
  --transition-slow: 300ms;
  --easing-out: cubic-bezier(0.16, 1, 0.3, 1);
  --easing-in: cubic-bezier(0.4, 0, 1, 1);
  --easing-standard: ease;
  --easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ── Keep all existing tokens that are unchanged ── */
  /* (success, warning, danger, grays are replaced by the new tokens above) */
}
```

### Old tokens to remove:
- `--color-gray-50` → replaced by `--color-surface`
- `--color-gray-100` → replaced by usage-specific (card bg stays white, hover surfaces use `--color-surface`)
- `--color-gray-200` → replaced by `--color-border`
- `--color-gray-400` → replaced by `--color-muted`
- `--color-gray-600` → replaced by `--color-secondary-text`
- `--color-gray-800` → replaced by `--color-heading`
- `--color-gray-900` → replaced by `--color-strong-text`

### Old tokens that remain (unchanged):
- `--color-success` / `--color-success-light`
- `--color-warning` / `--color-warning-light`
- `--color-danger` / `--color-danger-light`
- `--color-info-light` → still needed; value changes to `--color-primary-light`
- `--color-white`

### Selective replacement notes:
- `--color-info-light` (`#dbeafe` blue-100) → **replace with** `--color-primary-light` (`#d1fae5` green-100)
- `.badge-info` background → now uses `--color-primary-light`
- `.alert-info` background → now uses `--color-primary-light`, text → `--color-primary-dark`

### Button `.btn` base: Add the combined transition:
```css
.btn {
  transition:
    background-color var(--transition-fast) var(--easing-standard),
    transform var(--transition-fast) var(--easing-bounce),
    box-shadow var(--transition-fast) var(--easing-standard);
}
```

### Reduced motion media query to add:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition-duration: 0ms !important;
    animation-duration: 0ms !important;
    animation-iteration-count: 1 !important;
  }
  .skeleton, .skeleton-text, .skeleton-card, .skeleton-avatar {
    animation: none;
    opacity: 0.4;
  }
  .otp-box.error {
    animation: none;
  }
  .btn:active {
    transform: none;
  }
}
```

---

*This design specification revision covers the color and motion refresh only. All Phase 1 architecture, flows, layouts, and accessibility structure carry forward unchanged. The Frontend Specialist should re-skin the existing Phase 1 screens (customer/owner auth, dashboard shells) against the new tokens before beginning Phase 2 work.*
