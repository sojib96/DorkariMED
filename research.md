# Research Document: Pharmacy Marketplace Mobile App (Bangladesh)

> **Status:** Draft — Initial Discovery  
> **Prepared for:** Client review and discussion  
> **Date:** July 2026  
> **Author:** Product Manager (Research Phase)  
> **Document purpose:** This is a discovery-stage research document only. It does not define requirements, scope, architecture, or design decisions. It identifies what we know, what we don't know, and what needs client input before we proceed.

---

## A. Domain & Regulatory Context (Bangladesh-specific)

### A.1 Governing Regulatory Body

The **Directorate General of Drug Administration (DGDA)**, under the Ministry of Health & Family Welfare (MOHFW), is the sole drug regulatory authority in Bangladesh. It regulates all activities related to import, procurement, production, export, sales, pricing, etc. of all medicines including Allopathic, Ayurvedic, Unani, Herbal, and Homoeopathic systems.

### A.2 Primary Legislation

The **Drugs and Cosmetics Act, 2023** (Act No. 29 of 2023) is the current governing law, repealing the Drugs Act, 1940 and the Drugs (Control) Ordinance, 1982. This is the most relevant law for an online pharmacy marketplace.

**Key provisions relevant to this project:**

1. **Section 14(2) — License requirement for online sales:** *"No person or establishment shall use internet or web based platforms for selling, stocking, distributing or displaying for the purpose of sale of any drugs without having the license from the Licensing Authority or outside the conditions imposed in the license."*

   **→ Implication:** Every pharmacy onboarded to the marketplace must hold a valid DGDA drug license. The platform itself likely needs a license as an online pharmacy platform. This is a hard regulatory gate that cannot be bypassed.

2. **Section 40 — Prohibition on sale of certain drugs:** Prohibits sale of antibiotics or any drug *except* an over-the-counter (OTC) drug without a prescription from a registered physician. Also prohibits sale of expired drugs, government drugs, and physician samples.

   **→ Implication:** The app must handle prescription-only medicines differently from OTC medicines. A prescription upload/verification flow is legally required for any sale of antibiotics or non-OTC drugs.

3. **Section 45 — Supervision by qualified person for retail sale:** Allopathic drugs can only be sold under the personal supervision of a registered **Pharmacist** (Grade A), **Diploma Pharmacist** (Grade B), or **Pharmacy Technician** (Grade C) registered with the Pharmacy Council of Bangladesh.

   **→ Implication:** Every pharmacy on the platform must have a qualified pharmacy professional on staff who oversees dispensing. The app should surface which qualified professional is responsible for each order.

### A.3 DGDA Standard Operating Procedure (SOP) for Online Pharmacies

DGDA published an SOP for online pharmacies (available from their guidance documents section). Key requirements identified from published research referencing this SOP:

- Online pharmacies must follow DGDA guidelines
- Prescription medicines must not be sold without a valid prescription verified by a registered pharmacist
- Online pharmacies should display their license/permission documents on their website/app
- Every online medicine order should be verified by a registered pharmacist
- SOP covers online payments and cash-on-delivery procedures
- All medicines must be verified by a registered pharmacist before delivery

### A.4 OTC vs Prescription-Only (Rx) Classification

**DGDA has authorized 39 specific medicines as OTC (allopathic).** These can be dispensed without a prescription. The complete list (sourced from DGDA's Model Pharmacy accreditation documentation) includes common items such as:

- Paracetamol (tablet/syrup/suspension/suppository)
- Antacid (chewable tablet/suspension)
- ORS sachets
- Multivitamin tablets/capsules/drops
- Omeprazole capsule
- Low-dose contraceptive pills
- Calcium tablets
- Vitamin B Complex
- Chlorpheniramine Maleate (tablet/syrup)
- Diclofenac gel
- Chloramphenicol eye/ear ointment/drops
- Salbutamol tablet
- And others (total 39 items)

**Everything else (including ALL antibiotics, antihypertensives, antidiabetics, psychotropics, etc.) requires a valid prescription from a registered physician.**

> ⚠️ **Needs legal verification:** The exact list of 39 OTC drugs was obtained from a DGDA accreditation document. This list may be updated or superseded. A legal review should confirm whether the OTC list is still current and whether any additional categories (e.g., scheduled drugs, narcotics) have special restrictions for online sale.

### A.5 Licensed Online Pharmacies in Bangladesh

According to a 2025 legal analysis article (SCLS, April 2025):
- As of mid-2024, only **14 regulated e-pharmacies** were licensed under the Drugs and Cosmetics Act, 2023
- Over **1,500 illegal online drug vendors** were operating on Facebook and WhatsApp
- The DGDA partnered with Meta to remove 600+ illegal drug-selling pages
- An SMS-based verification system exists: text a pharmacy's name to **6969** to verify licensing status

### A.6 Market Context Numbers (verified from DGDA / WHO sources)

| Metric | Value |
|---|---|
| Estimated pharmaceutical market value | US$ 2.7 billion |
| Number of retail pharmacies (registered) | ~264,908 |
| Number of registered wholesalers/distributors | 2,695 |
| Number of pharmaceutical manufacturers | 275 |
| DGDA OTC medicines list | 39 allopathic drugs |
| Price-controlled products | 117 medicines |
| Online pharmacy market projection (2027) | ~$172.9 million (23.99% CAGR) |

> **Needs legal verification:** The exact thresholds for what constitutes an "online pharmacy" vs a "marketplace connecting licensed pharmacies" under Bangladeshi law. It is unclear whether a marketplace model (where the platform does not own inventory but connects buyers to licensed pharmacies) falls under the same licensing requirements as an inventory-led online pharmacy. This distinction is critical to the business model and needs legal counsel.

---

## B. Competitive Landscape

### B.1 Major Players

The online pharmacy sector in Bangladesh is growing but still nascent. Most major players use an **inventory-led model** (they own the inventory, warehouse, and delivery) rather than a true marketplace connecting independent pharmacies. This is an important distinction — your proposed **marketplace model** would be structurally different from most incumbents.

| Player | Model | Key Features | Rating | Notes |
|---|---|---|---|---|
| **Arogga** | Inventory-led | Medicine ordering, prescription upload, health info, refill reminders, medicine database with pictures/prices, cashback/rewards | 3.7★ (9K+ reviews) | Best-funded startup in the space; comprehensive medicine database; doctor booking feature |
| **MedEasy** | Inventory-led | Medicine delivery, doctor video consultation (23 specialties), lab tests, health records, prescription upload | 4.2★ (1.2K+ reviews) | Valid DGDA license (DC-22112); supported by ICT Division; Bangla + English support |
| **BanglaMeds** | Inventory-led | Medicine delivery (owned by Chaldal — major e-commerce platform) | — | Acquired by Chaldal; leverages existing logistics network |
| **Lazz Pharma** | Hybrid (offline chain + online) | Medicine delivery from chain stores | — | Oldest/largest pharmacy chain in Bangladesh (founded 1974); strong brand trust |
| **Osudpotro** | Inventory-led | Fast delivery (45 min–4.5 hrs), OTC + healthcare products, medication reminders | — | Launched during COVID; tech-forward |
| **Shombhob Health** | Inventory-led | Medicines + healthcare products; women-focused branding | — | $300K seed; unique positioning |
| **ePharma** | Inventory-led | Full healthcare platform | — | Part of Limitless Solutions Ltd |
| **Praava Health** | Broader healthcare play | Pharmacy + diagnostics + doctor consultation | — | Offline clinics + online |

### B.2 Key Competitive Observations

1. **No true marketplace model exists yet.** All prominent players own inventory. Your model (connecting independent pharmacies to customers) would be a differentiator — but also comes with unique challenges (quality control, consistent inventory data, pharmacist supervision across hundreds of independent shops).

2. **Medicine price comparison across pharmacies does not exist in current apps.** This is a potential differentiator for your app. Current apps show one price (the platform's own price). Your app could show the same medicine priced differently across nearby pharmacies.

3. **Prescription upload is standard.** Arogga and MedEasy both support prescription upload as a core flow. This is table stakes, not a differentiator.

4. **Telemedicine integration is common.** MedEasy and Arogga both offer doctor consultations. This seems to be a common expansion path but may not be necessary for an MVP.

5. **Delivery logistics are a major operational challenge.** Customer reviews consistently mention late deliveries, deliveryman quality issues, and extra charges for card payments. A marketplace model pushes delivery responsibility to individual pharmacies, which could be a pro (less operational burden) or a con (inconsistent customer experience).

6. **Customer trust is a significant barrier.** Multiple reviews mention fake/expired products, refund issues, and poor customer service. Any marketplace must invest heavily in trust mechanisms.

7. **The offline pharmacy network is vast (~265K registered outlets).** Almost every locality in Bangladesh has multiple pharmacies within walking distance, creating a strong "I'll just walk to the corner shop" habit that online platforms must overcome.

### B.3 Delivery/Logistics Norms

- Delivery range for online pharmacies is typically within major cities (Dhaka first, then divisional cities)
- Delivery times range from 45 minutes (Osudpotro, express) to 12–24 hours (MedEasy standard)
- Cash on delivery is common; card payments often incur 2.5–3% surcharge (based on user reviews)
- Minimum order thresholds for free delivery: typically 499–999 BDT
- Last-mile delivery in congested urban areas and "old town" neighborhoods is a recurring pain point based on user reviews

---

## C. Core User Personas

### C.1 Persona: Customer (Patient / General User)

**Demographics:** Age 20–50, urban or semi-urban, owns a smartphone, moderate-to-high digital literacy. May be managing a chronic condition (diabetes, hypertension) requiring regular medication, or a caregiver for elderly parents.

**Primary goals:**
- Get the right medicine quickly without visiting a pharmacy
- Find the cheapest/best price for a specific medicine nearby
- Compare medicine availability across pharmacies before going out or ordering
- Reorder regular medications conveniently
- Trust that the medicine received is authentic and not expired

**Pain points:**
- Multiple pharmacy visits to find a medicine in stock or at an affordable price
- Difficulty comparing prices without physically visiting different pharmacies
- Wasted trips to pharmacies that don't have the needed medicine
- Concern about counterfeit/expired medicine when buying online
- Language barrier (Bengali content preferred by many users)
- Unreliable delivery times and poor deliveryman communication (from existing app reviews)

**Key behaviors:**
- Searches by medicine name (brand or generic)
- Price-sensitive — willing to travel slightly farther or wait longer for savings
- Prefers to see expiry date before purchase
- Often has a prescription from a doctor visit

### C.2 Persona: Pharmacy Owner

**Demographics:** Age 30–60, owns/operates a retail pharmacy. May or may not be a pharmacist themselves (but must employ one per Section 45 of the Act). Moderate digital literacy — comfortable with smartphones for WhatsApp/browsing but may not be tech-savvy for complex inventory management.

**Primary goals:**
- Increase customer reach beyond walk-in foot traffic
- Sell more medicine, especially slow-moving stock
- Compete with nearby pharmacies and larger chains
- Maintain accurate inventory records
- Avoid selling expired medicine (legal liability)

**Pain points:**
- Manual inventory management — time-consuming and error-prone
- Difficulty attracting new customers beyond the immediate neighborhood
- Price competition from larger chains and online-only players
- Regulatory compliance burden (license display, prescription records, pharmacist supervision)
- Concern about showing prices publicly — fear of being undercut
- May not have the technical ability or staff to upload/maintain a full digital catalog
- Expired stock management — needs a systematic way to track and remove

**Key behaviors:**
- Skeptical about sharing pricing data openly
- Needs clear ROI to invest time in maintaining a digital storefront
- Values trust and reputation in the local community
- May use a mix of Bengali and English

### C.3 Persona: Admin / Platform Operator

**Demographics:** Internal team member(s) managing the platform. Could be a small operations team initially.

**Primary goals:**
- Ensure regulatory compliance across all onboarded pharmacies
- Maintain platform trust (no counterfeit/expired listings)
- Manage the pharmacy onboarding and verification process
- Resolve disputes between customers and pharmacies
- Ensure the medicine catalog is clean and standardized
- Drive growth (more pharmacies, more customers)

**Pain points:**
- Verifying pharmacy licenses and pharmacist credentials is manual and slow
- Cleaning up inconsistent medicine listings (free-text entries vs catalog entries)
- Enforcing the photo-proof-of-dispensing rule (order confirmation with expiry date photo)
- Handling complaints about wrong/expired medicine
- Balancing growth (onboard fast) with quality (verify thoroughly)
- Regulatory risk — platform could be held liable for pharmacy non-compliance

---

## D. Technical Feasibility Notes (Research-Level Only)

These are not design decisions or architectural commitments. They are observations to inform scope discussions.

### D.1 Geolocation-Based Radius Search

- The feature requires calculating distances between a user's current location and pharmacy locations, then filtering to a 2 km radius
- This is a well-understood problem in location-based services. Common approaches include geospatial indexing (geohash, H3, or spatial database queries) and API-based geocoding
- **Open question:** Should the radius be fixed at 2 km or configurable? What happens in rural/less-dense areas where 2 km returns zero results?
- **Open question:** Should "nearby" be based on straight-line distance or road distance? Road distance accounts for physical accessibility but is more complex to implement
- Battery/power usage of continuous GPS tracking should be considered for the customer app

### D.2 Medicine Database Standardization

**This is a critical open question that needs a client decision.**

**Scenario A — Free-text entry (pharmacy owners type medicine names):**
- Pros: Easy for pharmacy owners to start, no upfront catalog work
- Cons: Massive inconsistency (same medicine entered as "Napa Extra", "napa extra", "Napa Extra 500mg", "Napa 500 mg Paracetamol"); impossible to match the same medicine across pharmacies for price comparison; search quality degrades rapidly

**Scenario B — Master medicine catalog (pharmacy owners select from a curated list):**
- Pros: Clean matching across pharmacies; search works reliably; price comparison is straightforward; analytics are meaningful
- Cons: Significant upfront effort to build and maintain the catalog; pharmacy owners may not find their exact product (different manufacturers, pack sizes, strengths); catalog maintenance is ongoing

**Scenario C — Hybrid: Master catalog + open entry for unrecognized medicines, later normalized by admin:**
- Pros: Balances onboarding ease with data quality
- Cons: Admin overhead for normalization; temporary inconsistency between upload and normalization

> **Client decision needed:** Which approach do you prefer? The choice has major implications for scope, timeline, and the overall user experience of the comparison feature.

### D.3 Marketplace Model Considerations

- This is a true two-sided marketplace (pharmacies + customers), which is operationally different from the inventory-led model used by current competitors
- The platform does not own inventory, so it does not bear inventory risk or expiry risk
- However, the platform **does** bear trust risk — if a customer receives expired medicine from a pharmacy on the platform, the platform's reputation suffers even if the platform didn't sell it directly
- The photo-proof-of-dispensing requirement (pharmacist must upload photo of the medicine with visible expiry date before order is confirmed) is a key trust mechanism but adds friction to the pharmacy's workflow
- Revenue model (commission per transaction? subscription for pharmacies? listing fees?) is not yet defined and affects how the two-sided network effects are managed

### D.4 Photo Upload for Order Confirmation

- The requirement that pharmacists upload a photo showing the physical item with a visible expiry date before an order can proceed is novel and not commonly implemented in existing Bangladeshi pharmacy apps
- Technical feasibility is straightforward (camera access, image upload, storage)
- Operational feasibility is the real question: pharmacy owners may find this burdensome, especially during busy periods
- Storage costs and image moderation (ensuring photos are genuine and legible) need consideration

### D.5 Language

- Bangladesh is a Bengali-speaking country. The app should support Bengali as a first-class language, not an afterthought
- Both MedEasy and Arogga support Bengali; this is table stakes for adoption beyond English-literate users
- Medicine names, however, are typically in English (brand names) — so the app will likely be bilingual in practice

### D.6 Payment

- Cash on delivery (COD) is dominant in Bangladesh for e-commerce
- Mobile financial services (bKash, Nagad, Rocket) are widely used
- Card payments exist but user reviews mention 2.5–3% surcharges
- Digital payment integration will be necessary but the primary payment method will likely be COD or mobile wallet

---

## E. Open Questions / Assumptions

### E.1 Assumptions Made During This Research

| # | Assumption | Rationale |
|---|---|---|
| 1 | The Drugs and Cosmetics Act, 2023 is the primary governing law for online medicine sales | Verified — this is the current law, confirmed via official gazette and legal analysis |
| 2 | DGDA is the relevant licensing authority | Verified — confirmed by WHO country profile, DGDA website, and legal sources |
| 3 | 39 OTC medicines are authorized without prescription | Sourced from DGDA accreditation document — needs verification that this list is current |
| 4 | Arogga and MedEasy are the major competitors | Confirmed by multiple market reports, app store data, and news articles |
| 5 | 264,908 retail pharmacies exist in Bangladesh | Sourced from WHO 2025 Bangladesh Medical Products Profile (DGDA data) |
| 6 | The market is projected at ~$172.9M by 2027 | Sourced from Statista via Future Startup report; dependent on methodology |
| 7 | Most pharmacy owners have moderate digital literacy | Assumption based on smartphone penetration (~50%) and general e-commerce trends — not directly verified |
| 8 | Customers prefer Bengali language for the app | Assumption based on national language being Bengali; both major competitors offer Bengali support |

### E.2 Questions That Could Not Be Confidently Answered

| # | Question | Why It Matters |
|---|---|---|
| 1 | Does a **marketplace** model (platform connects customers to independent pharmacies without owning inventory) require a separate DGDA license, or does each pharmacy's individual license suffice? | Determines regulatory path and timeline; critical go/no-go factor |
| 2 | What are the specific fines/penalties for an online platform that enables a sale of a prescription drug without a valid prescription? | Determines legal risk exposure for the platform |
| 3 | Is the 39-item OTC list still current and complete as of 2026? | Determines which medicines can flow without prescription checking |
| 4 | Are there any specific data localization requirements for health/pharmacy data in Bangladesh? | Affects cloud infrastructure decisions |
| 5 | What are the tax implications for marketplace transactions (VAT, source tax, etc.)? | Affects revenue model and pricing |
| 6 | Can a single pharmacy fulfill orders outside its licensed premises (i.e., delivery to customer home)? | Some licenses restrict sale to the physical premises only |
| 7 | Are there restrictions on distance-based medicine delivery? | Could affect the 2 km radius feature if medicine delivery beyond a certain range has restrictions |
| 8 | What is the regulatory stance on displaying medicine prices publicly for comparison? | Some countries restrict price advertising for medicines; unclear for Bangladesh |
| 9 | What is the actual smartphone penetration rate among pharmacy owners in Bangladesh? | Affects assumptions about the pharmacy owner app adoption |
| 10 | Is there an existing master medicine database (like a national drug registry) we can leverage? | Would dramatically reduce the medicine catalog effort |

### E.3 Key Strategic Questions for the Client

These are questions that shape the **product direction** and need your input before we proceed:

1. **Marketplace vs Inventory-Led:** All current competitors use the inventory-led model. Are you committed to the marketplace model despite no local precedent, or would you consider a hybrid approach (e.g., start inventory-led with a few partner pharmacies and expand to marketplace later)?

2. **First Module:** What is the first, smallest useful thing you want to ship? Options include:
   - Just the customer-facing medicine search + price comparison (no ordering yet)
   - Just the pharmacy owner onboarding and storefront setup
   - A full order flow with a single pilot pharmacy chain
   - What's the priority?

3. **Revenue Model:** How does this app make money? Commission per transaction? Monthly subscription for pharmacy owners? Listing fees? Advertising? This affects the entire incentive design.

4. **Delivery:** Who handles delivery? The pharmacy (each delivers their own orders)? The platform (own fleet)? A third-party logistics partner? This is a major operational decision.

5. **Prescription Handling:** Do you want the platform to handle prescription verification (upload → pharmacist check → approve), or is that the responsibility of each pharmacy? If the platform verifies, you need registered pharmacists on staff.

6. **Target Geography:** Start in Dhaka only, or nation-wide from day one?

7. **Medicine Catalog Approach:** Free-text entry, master catalog, or hybrid? (See Section D.2 above.)

---

## Questions for Client

Before concluding this research phase and moving toward requirement definition, I need your input on the following:

1. **Regulatory risk tolerance:** Are you comfortable proceeding while several regulatory questions remain unanswered, or do you want a legal consultation first on the marketplace license question?

2. **Marketplace viability:** Given that no existing competitor operates a pure marketplace model in Bangladesh, is this a deliberate differentiation strategy, or is there flexibility to consider an inventory-led or hybrid start?

3. **Scope priority:** What is the first modular piece you want built? (Customer search + comparison? Pharmacy onboarding? Full order flow with one partner pharmacy? Other?)

4. **Revenue model preference:** Do you have one in mind, or is this to be determined after further research?

5. **Delivery model:** Who delivers — pharmacy, platform, or third party?

6. **Language priority:** Must the app support Bengali from day one, or is English-first acceptable for an MVP?

7. **Platform:** Android only first, or both iOS and Android from day one?

8. **Timeline expectations:** Do you have a target launch timeline that affects scope decisions?

9. **Budget context:** (Optional) Any budget constraints that would influence build-vs-buy decisions?

10. **Legal counsel:** Do you have access to legal counsel for the regulatory questions flagged in this document, or should we budget for that?

---

*This document represents the best available evidence from public sources as of July 2026. Where claims could not be verified, they are explicitly marked. No design, architecture, or scope decisions should be made from this document alone — it is intended to inform a strategic conversation before requirements work begins.*
