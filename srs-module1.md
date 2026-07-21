# Software Requirements Specification — Module 1
## Pharmacy & Medicine Discovery (Discovery & Price Comparison)

> **Status:** Draft for System Designer and UI/UX Designer  
> **Based on:** Research Document (`research.md`) and Client Decisions (Discovery Review — Cycle 1)  
> **Date:** July 2026  
> **Author:** Product Manager  
> **Document purpose:** This SRS defines Module 1 only — a complete, demoable vertical slice for medicine discovery and price comparison across nearby pharmacies. It does not include ordering, payment, or prescription handling. Those are explicitly deferred to future modules, but the data model anticipates them.

---

## 1. Introduction

### 1.1 Product Vision (Long-term)

A two-sided pharmacy marketplace for Bangladesh where:
- Pharmacy owners create digital storefronts and list their available medicines with prices
- Customers discover nearby pharmacies, compare medicine prices across them, and order directly
- An admin oversees platform compliance and quality

### 1.2 Module 1 Purpose

Module 1 validates the core value proposition — **helping customers find the cheapest nearby medicine across independent pharmacies** — while deferring all transaction-related features (ordering, payment, prescription handling, delivery) until the unresolved regulatory questions about marketplace licensing (see `research.md` Section E.2 #1) can be answered by legal counsel.

Module 1 builds the foundational data model (pharmacy profiles, medicine catalog, geospatial data) that every future module depends on, so nothing built here gets thrown away.

### 1.3 Module 1 Scope — "Discovery & Price Comparison"

**In scope:**
- Pharmacy owner registration and storefront creation
- Medicine catalog entry by pharmacy owners (hybrid model: curated master catalog + free-text fallback)
- Customer app with location-based default view (2 km straight-line radius)
- Medicine detail view with price comparison across in-range pharmacies
- Search: by pharmacy name, by medicine name (with price comparison)
- Admin dashboard with basic visibility into onboarded pharmacies and catalog entries

**Explicitly out of scope:**
- Ordering / cart / checkout
- Prescription upload and pharmacist verification
- Payment integration (bKash, Nagad, SSLCommerz)
- Photo-proof-of-dispensing on order confirmation
- Delivery coordination
- User reviews / ratings
- Push notifications (except basic account emails if needed for registration)
- Full admin moderation and DGDA license verification tooling
- Bengali language UI (i18n architecture required; English-only for Module 1)
- iOS app (Android + responsive website only)

### 1.4 Definitions

| Term | Definition |
|---|---|
| **Customer** | End-user (patient/general user) who browses pharmacies and medicines |
| **Pharmacy Owner** | Registered pharmacy operator who creates a digital storefront |
| **Admin** | Platform operator with oversight of onboarded pharmacies and catalog |
| **Master Medicine Catalog** | System-curated, standardized list of medicines with uniform names/attributes |
| **Pharmacy Listing** | A specific medicine as sold by a specific pharmacy, with its price |
| **2 km Radius** | Straight-line (Euclidean) distance from the customer's current location |
| **i18n** | Internationalization — architecture that supports multiple languages without code changes |
| **DGDA** | Directorate General of Drug Administration (Bangladesh drug regulatory authority) |

---

## 2. User Roles & Permissions (Module 1 Only)

### 2.1 Customer

**Can do in Module 1:**
- Register and log in (email/phone + OTP)
- View a map or list of pharmacies within 2 km of current location, sorted by distance
- Search for a pharmacy by name
- Search for a medicine by name (brand or generic)
- View a medicine's detail page showing its price at every in-range pharmacy that lists it
- View a pharmacy's storefront page showing all medicines they list with prices
- Update profile (name, phone, default address/location)
- Browse pharmacies and medicine prices without logging in (public browsing — no account required for discovery)
- Register (email/phone) and subscribe for "Notify me when ordering launches" updates from the medicine detail page

**Cannot do in Module 1 (future modules):**
- Place an order, add to cart, or checkout
- Upload a prescription
- Make a payment
- Rate or review a pharmacy

### 2.2 Pharmacy Owner

**Can do in Module 1:**
- Register as a pharmacy owner (provide business info, location, license number, pharmacist details)
- Create and edit their pharmacy storefront (name, description, address, operating hours, phone, photos)
- Add medicines to their catalog:
  - Search and select from the master medicine catalog, then set their price
  - OR type in a free-text medicine name if it's not in the master catalog (flagged for admin normalization)
- Update prices and remove listings
- View their own storefront as customers will see it
- Update password and contact information

**Cannot do in Module 1 (future modules):**
- Accept or process orders
- Upload proof-of-dispensing photos
- Manage delivery
- View sales analytics or revenue reports

**Registration requirements (captured but not verified in Module 1):**
- Pharmacy name
- Physical address (with map pin for geolocation)
- Owner name
- Drug license number (DGDA license — text field, not verified against DGDA in this module)
- Pharmacist name and registration number (for compliance with Section 45)
- Phone number / email
- Operating hours

> **Note:** License verification against DGDA records is deferred to a future admin module. In Module 1, the license number is stored as provided. The risk register should list "unverified pharmacy licenses" as an accepted risk for the discovery phase.

### 2.3 Admin

**Can do in Module 1:**
- View a list of all registered pharmacies with their status and basic info
- View all medicine catalog entries (master catalog items and free-text additions)
- See which free-text entries are pending normalization
- Manually normalize free-text entries (link them to a master catalog entry or create a new master entry)
- Suspend/activate a pharmacy's visibility on the platform (if abuse is reported)
- View basic platform statistics (number of pharmacies, number of medicine listings, number of customers)

**Cannot do in Module 1 (future modules):**
- Verify DGDA licenses against a government database
- Moderate orders or disputes
- Manage commission rates or billing
- Generate revenue reports

---

## 3. Functional Requirements

### 3.1 Pharmacy Owner Registration & Storefront

| ID | Requirement | Notes |
|---|---|---|
| FR-01 | The system shall allow a user to register as a pharmacy owner by providing: pharmacy name, owner name, phone number, email, physical address, DGDA license number, pharmacist name, pharmacist registration number, and operating hours. | Data is stored for later verification. |
| FR-02 | The system shall allow the pharmacy owner to pin their pharmacy's location on a map during registration to capture precise geocoordinates (latitude/longitude). | Required for the 2 km radius feature. |
| FR-03 | The system shall send an email/SMS verification to confirm the pharmacy owner's contact information before the storefront becomes visible to customers. | Basic spam prevention. |
| FR-04 | Once registered and verified, the pharmacy owner shall be able to log in to a dashboard where they can edit their storefront details (name, description, address, hours, photos, phone). | |
| FR-05 | The pharmacy owner can deactivate their storefront visibility temporarily. | |
| FR-06 | The pharmacy storefront must display: pharmacy name, address, operating hours, phone number, and a list of medicines they carry with prices. | |

### 3.2 Medicine Catalog Entry

| ID | Requirement | Notes |
|---|---|---|
| FR-07 | The system shall maintain a **Master Medicine Catalog** containing standardized entries with: medicine name (brand), generic name, manufacturer, dosage form (e.g., tablet, syrup, injection, cream), strength (e.g., 500mg, 10mg/5ml), and a description. | This is curated and seeded by the platform. |
| FR-08 | When adding a medicine to their storefront, the pharmacy owner shall first search the master catalog. If found, they select it and enter only their selling price. | |
| FR-09 | If the medicine is NOT found in the master catalog, the pharmacy owner may type it in as free text (name, generic name, manufacturer, dosage form, strength as free fields). This entry is flagged as **"unmatched — pending normalization"** and is visible to customers immediately but marked for admin review. | This is the "Scenario C hybrid" approach from research.md Section D.2. |
| FR-10 | The admin shall have a dedicated interface showing all unmatched free-text entries, with the ability to: (a) link them to an existing master catalog entry, (b) create a new master catalog entry, or (c) reject/flag for follow-up. | |
| FR-11 | A pharmacy owner can update the price of any of their listed medicines at any time. | |
| FR-12 | A pharmacy owner can remove a medicine from their storefront at any time. | |
| FR-13 | The system shall allow bulk upload of medicine listings (e.g., via CSV or spreadsheet) for pharmacy owners with large inventories. | Eases onboarding friction for pharmacy owners with many items. |
| FR-14 | The master medicine catalog shall be seeded with a starter set of at least the 500 most commonly prescribed medicines in Bangladesh (drawn from public formularies). The exact contents will be defined by the System Designer and a domain expert. | Must include all 39 DGDA-authorized OTC drugs. |

### 3.3 Customer Location & Discovery

| ID | Requirement | Notes |
|---|---|---|
| FR-15 | Upon opening the app, the customer shall be prompted to grant location permission. If granted, the default view shows a list/map of pharmacies within a 2 km straight-line radius of their current location, sorted by distance (nearest first). | |
| FR-16 | If location permission is denied, the customer may manually enter an address or drag a pin on a map to set a reference location. | Graceful fallback. |
| FR-17 | The customer may adjust the radius filter (presets: 1 km, 2 km (default), 5 km, 10 km, or "entire city") to expand or narrow their search. | |
| FR-18 | The pharmacy list view shall display: pharmacy name, distance from user, operating hours, and an indicator of whether they are currently open. | |
| FR-19 | The customer may toggle between a map view (pharmacy pins on a map) and a list view. | |

### 3.4 Medicine Search & Price Comparison

| ID | Requirement | Notes |
|---|---|---|
| FR-20 | The customer may search for a medicine by name (brand name or generic name). | |
| FR-21 | Search results shall show matching medicines across all pharmacies within the customer's current radius, grouped by medicine with the lowest price prominently displayed. | Core differentiator. |
| FR-22 | Each result shall display: medicine name, generic name, strength, manufacturer, lowest available price, and the number of pharmacies carrying it within range. | |
| FR-23 | The customer may tap a medicine to view its **Medicine Detail Page**, showing a comparison table of that medicine's price at every in-range pharmacy that carries it, sorted by price (lowest first). | |
| FR-24 | The Medicine Detail Page shall display: medicine info (brand name, generic name, manufacturer, strength, dosage form, description), followed by a table with columns: Pharmacy Name, Distance, Price, and a button to "View Pharmacy." | |
| FR-25 | The customer may filter medicine search results by: manufacturer, price range, or availability (in-stock only if the pharmacy has indicated stock). | |
| FR-26 | If a medicine is not available within the customer's current radius, the system shall suggest widening the radius or searching for similar medicines. | |
| FR-27 | The Medicine Detail Page shall include a "Notify me when ordering is available" button. When clicked by an unauthenticated user, the system shall prompt for an email or phone number to subscribe. When clicked by a logged-in customer, the system shall use their registered contact. Submissions shall be stored and retrievable for future bulk notification when the ordering module launches. | Captures demand pipeline for Module 2; mitigates R-05. |

### 3.5 Pharmacy Search

| ID | Requirement | Notes |
|---|---|---|
| FR-28 | The customer may search for a pharmacy by name (full or partial match). | |
| FR-29 | Pharmacy search results shall show matching pharmacies with their distance, address, and a link to their storefront page. | |
| FR-30 | The customer may filter pharmacy search results by: currently open, has specific medicine in stock, or operating hours. | |

### 3.6 Pharmacy Storefront (Public View)

| ID | Requirement | Notes |
|---|---|---|
| FR-31 | Each pharmacy shall have a public storefront page showing: pharmacy name, address, operating hours, phone, photos (if uploaded), and a searchable list of their medicines with prices. | |
| FR-32 | The customer may sort the pharmacy's medicine list by: price (low to high), name (alphabetical), or category. | |
| FR-33 | The customer may search within a pharmacy's medicine list. | |

### 3.7 Admin Dashboard (Basic Visibility)

| ID | Requirement | Notes |
|---|---|---|
| FR-34 | The admin shall have a dashboard showing: total registered pharmacies, total medicine listings, total customers, pending unmatched entries count. | |
| FR-35 | The admin may view a list of all pharmacies with: name, status (active/suspended/pending), registration date, license number. | |
| FR-36 | The admin may toggle a pharmacy between active and suspended visibility. | |
| FR-37 | The admin may view all unmatched free-text medicine entries and normalize them (link to master catalog, create new master entry, or flag). | |
| FR-38 | The admin may view the complete master medicine catalog and add/update entries. | |

---

## 4. Data Model Considerations

### 4.1 Entities (Anticipating Future Modules)

The data model for Module 1 must be designed so that future modules (ordering, payments, prescriptions, delivery) can be added **without breaking existing data or requiring migration of production data.**

#### 4.1.1 Pharmacy

```
Pharmacy {
  id: UUID (PK)
  name: string
  owner_name: string
  phone: string
  email: string (optional)
  address_line: string
  city: string
  division: string
  latitude: float (geospatial index)
  longitude: float (geospatial index)
  dgda_license_number: string
  pharmacist_name: string
  pharmacist_registration_number: string
  operating_hours: JSON (e.g., {"mon": "09:00-21:00", ...})
  status: enum (active, suspended, pending_review)  // default: active for M1
  is_verified: boolean  // placeholder — will be used when DGDA verification is added
  created_at: datetime
  updated_at: datetime
}
```

**Future-proofing notes:**
- `status` field is defined now even though only "active" and "suspended" are used in Module 1. Future modules will add `pending_review` (for license verification queue) and `rejected`.
- `is_verified` is a boolean placeholder for the future DGDA license verification workflow.
- A `delivery_config` JSON field may be added later to store delivery radius, fee, and policy per pharmacy.

#### 4.1.2 Master Medicine Catalog

```
MasterMedicine {
  id: UUID (PK)
  brand_name: string
  generic_name: string
  manufacturer: string
  dosage_form: string (e.g., "Tablet", "Syrup", "Injection", "Cream")
  strength: string (e.g., "500mg", "10mg/5ml")
  description: text (optional)
  category: string (optional, for future use — e.g., "Antibiotic", "Antihypertensive", "OTC")
  requires_prescription: boolean  // critical for future prescription flow
  is_active: boolean
  created_at: datetime
  updated_at: datetime

  // Unique constraint on (brand_name, manufacturer, strength, dosage_form)
}
```

**Future-proofing notes:**
- `requires_prescription` is defined NOW even though Module 1 doesn't handle prescriptions. This lets the system classify medicines from day one without a migration later. In Module 1, this field is informational only. In Module 2+, it gates the ordering flow.
- `category` field anticipates future categorization for browsing, filtering, and regulatory reporting.
- The unique constraint ensures the master catalog stays clean.

#### 4.1.3 Pharmacy Medicine Listing (PIVOT — critical entity)

This is the most important entity for future-proofing. Every future order will reference a `PharmacyMedicineListing` instance, not a `MasterMedicine` instance, because the price, pharmacy, and availability are specific to the listing.

```
PharmacyMedicineListing {
  id: UUID (PK)
  pharmacy_id: UUID (FK → Pharmacy)
  master_medicine_id: UUID (FK → MasterMedicine, nullable)
  // If master_medicine_id is null, this is a free-text unmatched entry
  unmatched_name: string (nullable)  // free-text name if not in master catalog
  unmatched_generic_name: string (nullable)
  unmatched_manufacturer: string (nullable)
  unmatched_dosage_form: string (nullable)
  unmatched_strength: string (nullable)
  price: decimal (10, 2)  // in BDT
  stock_status: enum (in_stock, out_of_stock, unknown)  // default: unknown for M1
  is_active: boolean
  normalization_status: enum (matched, unmatched_pending, normalized_by_admin)
  created_at: datetime
  updated_at: datetime
}
```

**Future-proofing notes:**
- Future `OrderItem` will reference `PharmacyMedicineListing.id`, NOT `MasterMedicine.id`. This ensures order history is preserved even if the listing price changes later or the medicine is removed.
- `stock_status` is defined now even though Module 1 doesn't process orders. The pharmacy owner can mark items as in/out of stock, and customers see availability. This is useful data before ordering exists.
- When ordering is added in Module 2+, `stock_status` becomes a gating condition (can't order if out_of_stock).
- The nullable `master_medicine_id` with fallback free-text fields supports the Scenario C hybrid model.

#### 4.1.4 Customer

```
Customer {
  id: UUID (PK)
  name: string
  phone: string (unique)
  email: string (optional)
  password_hash: string
  default_latitude: float (nullable)  // saved home location for future default view
  default_longitude: float (nullable)
  is_active: boolean
  created_at: datetime
  updated_at: datetime
}
```

**Future-proofing notes:**
- `default_latitude`/`default_longitude` saves a customer's home location so that on future visits they see nearby pharmacies even without granting GPS permission each time.
- Future modules will add: `saved_addresses` (table for multiple delivery addresses), `default_payment_method`, and a link to order history.

#### 4.1.5 Admin

```
Admin {
  id: UUID (PK)
  name: string
  email: string (unique)
  password_hash: string
  role: enum (super_admin, moderator)  // defined now for future scale
  is_active: boolean
  created_at: datetime
}
```

### 4.2 Key Entity Relationship Diagram (Textual)

```
Customer ──╼ (browses) ──╼ Pharmacy (within radius)
                               │
                               │ has many
                               ▼
                    PharmacyMedicineListing ────► MasterMedicine
                               │                      │
                               │ (future)             │ (future)
                               ▼                      ▼
                    OrderItem ◄─────────────── Order  │
                                                     │
                                                     ▼
                                              Prescription (future)
```

### 4.3 Geospatial Data

- Pharmacy locations are stored as `latitude`/`float` and `longitude`/`float` columns.
- A geospatial index (PostGIS or equivalent for the chosen database) should be created on these columns to support efficient radius queries.
- The 2 km radius search will use the **Haversine formula** (great-circle distance) for straight-line distance calculation, executed via the database's geospatial functions for performance.
- Future consideration: road-distance routing via a mapping API (Google Maps, OSRM, etc.) — flagged as a future optimization, not a v1 requirement.

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement |
|---|---|
| NFR-01 | The 2 km radius pharmacy search must return results within **2 seconds** under normal network conditions (4G) for areas with up to 100 pharmacies in range. |
| NFR-02 | The medicine price comparison view must load within **3 seconds** for a medicine carried by up to 20 pharmacies. |
| NFR-03 | Pharmacy storefront pages must load within **2 seconds**. |
| NFR-04 | The system must handle at least **1,000 concurrent users** in the Dhaka metro area during peak hours without degradation. |
| NFR-05 | All API responses should be paginated where list results may exceed 20 items. |

### 5.2 Data Accuracy & Quality

| ID | Requirement |
|---|---|
| NFR-06 | Medicine prices displayed must reflect the most recent value entered by the pharmacy owner (eventually consistent within 60 seconds — no hard real-time requirement for v1). |
| NFR-07 | Free-text unmatched medicine entries must be clearly differentiated from master-catalog-matched entries in the UI (e.g., with a visual indicator like "(unverified listing)" or italicized text). |
| NFR-08 | The system must prevent duplicate master catalog entries via the unique constraint on (brand_name, manufacturer, strength, dosage_form). Normalization UI should surface potential duplicates during admin review. |

### 5.3 Security

| ID | Requirement |
|---|---|
| NFR-09 | All API communication must be over HTTPS (TLS 1.2+). |
| NFR-10 | Passwords must be hashed using bcrypt or Argon2. |
| NFR-11 | Customer browsing of pharmacies and medicine prices shall be publicly accessible without authentication. No login or registration shall be required to search for medicines, view pharmacy storefronts, or compare medicine prices. Authentication is required only for pharmacy owner storefront management and customer registration for future features (e.g., "notify me" subscriptions). |

### 5.4 Internationalization (i18n)

| ID | Requirement |
|---|---|
| NFR-12 | All user-facing strings must be stored in locale files (JSON, YAML, or gettext .po format), not hardcoded in templates or views. |
| NFR-13 | Django's built-in i18n framework should be used (or equivalent for Django REST Framework — `django-rosetta` or similar for translations). |
| NFR-14 | Module 1 ships with English as the only active locale. Bengali (bn) locale files should be structured and stubbed (even if empty) to confirm the architecture works. |
| NFR-15 | The UI text direction must default to LTR. RTL support for Arabic is not required. |

### 5.5 Platform & Technology

| ID | Requirement |
|---|---|
| NFR-16 | Backend: Django REST Framework (shared across both frontends). |
| NFR-17 | Customer-facing mobile app: Android (native Kotlin or cross-platform — System Designer's call). |
| NFR-18 | Customer-facing website: Responsive web app (React or Django templates — System Designer's call). |
| NFR-19 | Pharmacy owner dashboard: responsive web app (desktop + mobile browser). |
| NFR-20 | Admin dashboard: responsive web app (desktop-primary). |
| NFR-21 | Database: PostgreSQL with PostGIS extension (for geospatial queries). |
| NFR-22 | Infrastructure: Open-source and free-tier-friendly where feasible (per client's budget direction). |

### 5.6 Availability & Reliability

| ID | Requirement |
|---|---|
| NFR-23 | Target uptime: 99.5% (excluding planned maintenance). |
| NFR-24 | The system should gracefully degrade if the geospatial database is unavailable — fall back to displaying pharmacies without distance sorting or filtering. |
| NFR-25 | Scheduled maintenance windows should be communicated via a status page. |

---

## 6. Assumptions Carried Forward

| # | Assumption | Source |
|---|---|---|
| A-01 | Straight-line (Euclidean) distance is acceptable for the 2 km radius feature in Module 1. Road-distance routing is deferred. | Client decision in Cycle 1 review. |
| A-02 | i18n architecture will be set up in Module 1, but only English strings are implemented. Bengali is a fast-follow. | Client decision in Cycle 1 review. |
| A-03 | Pharmacy license numbers are captured in Module 1 but not verified against DGDA records. This is an accepted risk for the discovery phase. | Client decision — risk register item. |
| A-04 | The master medicine catalog will be seeded with ~500 commonly prescribed medicines. Exact contents need a domain expert/pharmacist to define. | Product Manager assumption — client should confirm or provide a source. |
| A-05 | A customer does NOT need to be logged in to browse pharmacies and compare medicine prices (public browsing). | Confirmed by client in SRS Review — Cycle 1. |
| A-06 | The API backend (Django REST Framework) and database schema defined in this SRS can accommodate all future modules without breaking changes. | Design principle guiding the data model. |
| A-07 | Pharmacy owners have sufficient digital literacy to use the storefront management web interface. | Research.md Section E.1 #7 — unverified assumption. |
| A-08 | Medicine prices in Bangladesh are set independently by each pharmacy (no nationwide MRP enforcement across all channels). | General market assumption — verify with domain expert. |

---

## 7. Open Items (Need Client or System Designer Input)

| # | Question | Resolution |
|---|---|---|
| O-02 | Master catalog seed source | Check public Bangladesh essential medicines list first (e.g., official formulary or DGDA sources). If none sufficiently complete exists, budget for one-time paid consultation with a registered pharmacist. Do NOT block development — catalog can be seeded incrementally; hybrid free-text fallback (FR-09) ensures app is usable with a partial catalog on day one. |
| O-03 | Document upload (license/NID) at pharmacy owner registration? | **Not in Module 1.** Text fields only. Document upload + DGDA license verification is part of a future admin/compliance module. |
| O-04 | Bulk upload threshold and format | CSV upload with a downloadable template. No hard row limit for v1 — System Designer shall implement a sane technical ceiling (row count and/or file size) with a clear error message for exceeded limits. |
| O-05 | Separate radius defaults for dense vs sparse areas? | **Not needed.** FR-17's existing radius presets (1/2/5/10 km, entire city) already cover both use cases. Users in sparse areas can widen the radius manually. |
| O-06 | Pharmacy owner analytics (storefront views, comparison appearances)? | **Nice-to-have, not required for Module 1 launch.** Include only if it comes cheaply as a byproduct of existing logging. Otherwise, backlog. Do not delay core scope. |
| O-07 | Android: native (Kotlin/Jetpack Compose) vs cross-platform (Flutter/React Native)? | System Designer's recommendation. Optimize for fastest path to a solid, maintainable Module 1 — no heavy on-device logic in this discovery-only MVP. |
| O-08 | Customer website: SPA (React/Vue) vs server-rendered (Django templates + htmx)? | System Designer's recommendation. Same reasoning as O-07. |

---

## 8. Future Module Touchpoints

This section documents how the Module 1 data model anticipates future modules. It is **informational** for System Designer — not requirements for Module 1.

### 8.1 Module 2 — Ordering & Cart

- `PharmacyMedicineListing` is the entity that `OrderItem` will reference via FK.
- A future `Order` table will reference `Pharmacy` (the seller) and `Customer` (the buyer).
- `stock_status` on `PharmacyMedicineListing` becomes a gating condition for adding to cart.
- `requires_prescription` on `MasterMedicine` will gate the ordering flow (must upload prescription before checkout for Rx medicines).

### 8.2 Module 3 — Payment Integration

- A future `Payment` table will reference `Order`.
- `Customer` will need a `default_payment_method` field or a saved payment methods table.
- `Pharmacy` may need a `payout_method` (bank account, bKash merchant) for receiving funds.

### 8.3 Module 4 — Prescription Verification

- A future `Prescription` entity will reference `Customer` and contain an uploaded image URL.
- `PharmacyMedicineListing` → `MasterMedicine.requires_prescription` is the gating flag.
- `Pharmacy`'s `pharmacist_registration_number` becomes actionable — the verifying pharmacist must be registered with the Pharmacy Council.

### 8.4 Module 5 — Photo-Proof-of-Dispensing

- A future `OrderProofPhoto` entity or a `proof_photo_url` field on `Order` will store the pharmacist-uploaded image.
- This is the last step before an order status moves to "ready for delivery."

### 8.5 Module 6 — Delivery Coordination

- A future `Delivery` entity may track: assigned delivery person, status updates, tracking history.
- `Pharmacy` may get a `delivery_config` JSON field (delivery radius, fee, estimated time).

### 8.6 Module 7 — Reviews & Ratings

- A future `Review` table will reference `Pharmacy` and `Customer`.
- The `Pharmacy` entity's aggregate rating can be cached in a `rating_avg` field or computed on the fly.

---

## 9. Risk Register (Relevant to Module 1)

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Marketplace license ambiguity (E.2 #1 from research.md) — Module 1 is designed to not trigger this. But if a regulator considers listing/comparison alone as "online pharmacy operation," there is regulatory exposure. | Low (Module 1 has no sales) | High | Module 1 scoped to exclude all transactions. Legal counsel engagement added as pre-launch action item before Module 2. |
| R-02 | Pharmacy owners do not adopt the platform because the effort of listing medicines outweighs the benefit (no orders yet in Module 1). | Medium | Medium | The bulk upload feature (FR-13) reduces onboarding effort. The PM should track pharmacy sign-ups vs listings as a Module 1 success metric. If adoption is low, consider incentives or a concierge onboarding service. |
| R-03 | Free-text medicine entries flood the system, making the master catalog hard to maintain and the price comparison feature unreliable. | Medium | High | The hybrid approach (FR-09, FR-10) with admin normalization interface is the mitigation. The PM must monitor the ratio of matched-to-unmatched entries weekly. |
| R-04 | Geospatial query performance degrades as pharmacy count grows. | Low (at launch) | Medium | PostGIS indexing (NFR-21) should handle this. Monitor and optimize before Module 2. |
| R-05 | Customers find the app useful but have no way to act on the information (no ordering) — leading to frustration and churn before Module 2 ships. | Medium | Medium | Communicate clearly in the app that ordering is coming soon. Collect "notify me when ordering launches" emails during Module 1 as a pipeline for Module 2. |

---

## 10. Success Metrics for Module 1

| Metric | Target | Measurement |
|---|---|---|
| Pharmacy owners registered | ≥ 50 within 4 weeks of launch | Admin dashboard count |
| Pharmacy owners with ≥ 20 medicines listed | ≥ 30 within 4 weeks | Database query |
| Master catalog utilization rate (% of listings matched to master catalog) | ≥ 70% | Ratio of matched to unmatched listings |
| Price comparison views (a customer viewed a medicine's comparison table) | ≥ 1,000 views per week | Analytics event |
| Customer search-to-result success rate (searches that return at least one result) | ≥ 80% | Analytics funnel |
| App/website average page load | ≤ 3 seconds | Performance monitoring |
| Pharmacy owner storefront page views (total across all pharmacies) | ≥ 5,000 per week | Analytics event |

---

*This SRS is ready for handoff to System Designer (architecture and API design) and UI/UX Designer (customer and pharmacy owner interfaces). Any questions from those teams about scope interpretation should be directed to the Product Manager.*
