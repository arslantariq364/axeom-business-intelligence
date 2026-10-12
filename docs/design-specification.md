# Axeom Owner OS — UI/UX Design Specification

**Reference Inspiration**: [Conneq CRM — Productivity Management Mobile App UI/UX Design (Dribbble #27082491)](https://dribbble.com/shots/27082491-Conneq-CRM-Productivity-Management-Mobile-App-UI-UX-Design)  
**Theme Direction**: Light Sage, Off-White, Dark Charcoal Typography & Bright Lime Accent.

---

## 1. Design Tokens & Color Palette

| Token Name | Hex Code | Visual Role & Usage Guidelines |
| :--- | :--- | :--- |
| `--bg-page` | `#EAF0EB` | Very light sage / gray-green page canvas background. |
| `--surface-card` | `#F7F9F6` | Off-white card surface for secondary actions, tables, and modal dialogs. |
| `--surface-muted` | `#D9E1DB` | Muted sage for input fields, metric cards, sub-tabs, and secondary buttons. |
| `--surface-active`| `#CDD7CE` | Slightly deepened sage for active/hover states on neutral components. |
| `--border-subtle` | `#D2DBD1` | Crisp, natural 1px border around cards, tables, and dividers. |
| `--text-primary`  | `#172018` | Dark charcoal for maximum legibility on off-white, muted sage, and lime cards. |
| `--text-secondary`| `#526052` | Readable muted forest-slate for secondary text, labels, and timestamps. |
| `--accent-lime`   | `#D3F940` | Bright chartreuse/lime used **selectively** to highlight the #1 Recommended Action and primary active controls. |
| `--accent-lime-hover`| `#C4EC33` | Slightly deepened lime for interactive hover and focus states. |
| `--text-on-lime`  | `#172018` | **Strict requirement**: Always dark charcoal text on lime surfaces for high contrast. |
| `--status-danger` | `#DC2626` | Deep red for overdue badges, cancellation warnings, and critical churn tags. |
| `--status-danger-bg`| `rgba(220, 38, 38, 0.10)` | Soft tinted red background for danger pills. |
| `--status-warning`| `#D97706` | Warm amber for pending triage, unbilled work, and tool errors. |
| `--status-success`| `#16A34A` | Clean emerald green for resolved tasks, cleared invoices, and good standing. |

---

## 2. Typography & Hierarchy

* **Primary Font Family**: `'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
* **Hierarchy**:
  * **Screen Title / Greeting**: `font-size: 1.5rem (24px)`, `font-weight: 800`, `color: #172018`, `letter-spacing: -0.02em`
  * **Hero Action Headline**: `font-size: 1.35rem (21.6px)`, `font-weight: 800`, `line-height: 1.3`, `color: #172018`
  * **Section Headers**: `font-size: 0.82rem (13px)`, `font-weight: 800`, `text-transform: uppercase`, `letter-spacing: 0.08em`, `color: #526052`
  * **Card Titles**: `font-size: 1.05rem (16.8px)`, `font-weight: 700`, `color: #172018`
  * **Large Metric Figures**: `font-size: 1.5rem (24px)`, `font-weight: 800`, `letter-spacing: -0.03em`, `color: #172018`
  * **Body / Explanatory Text**: `font-size: 0.85rem (13.6px)`, `font-weight: 500`, `line-height: 1.55`, `color: #526052`
  * **Micro-Labels & Tags**: `font-size: 0.72rem (11.5px)`, `font-weight: 700`, `letter-spacing: 0.04em`

---

## 3. Spatial System & Geometry

* **Corner Radii**:
  * Outer Action Cards & Hero Card: `border-radius: 22px`
  * Secondary Containers & Tables: `border-radius: 18px`
  * Input Fields & Inner Staging Boxes: `border-radius: 12px`
  * Filter Chips, Status Pills, & Nav Buttons: `border-radius: 9999px` (full pill)
* **Spacing Scale**:
  * Mobile Screen Padding: `16px` horizontal, `20px` top, `96px` bottom (clearing floating nav dock)
  * Desktop Main Content Padding: `36px 48px`
  * Card Padding: `22px 20px` on mobile, `26px 24px` on desktop
  * Inter-Card Vertical Gap: `14px` on mobile, `18px` on desktop
* **Shadows & Elevation**:
  * Minimal, flat Scandinavian-modern aesthetic.
  * Card Shadow: `0 2px 10px rgba(23, 32, 24, 0.04)`
  * Hero Lime Card: `0 6px 20px rgba(211, 249, 64, 0.35)`
  * Modal Overlay: `0 20px 40px -10px rgba(23, 32, 24, 0.25)`

---

## 4. Component Patterns

### A. Compact Header
* Brand title: **AXEOM** with a small line-art studio icon.
* Screen title: **Today**.
* Subtitle line: *"Axeom Studio Operations • Fixed Business Date: 6 Oct 2026"*.
* Prominent, easily discoverable **Add new files** button.

### B. First Recommended Action (Hero Lime Card)
* **Background**: `#D3F940` (Solid lime).
* **Text**: `#172018` (Dark charcoal).
* **Badge**: Pill tag `🚨 URGENT ACTION #1 • CHURN INTERVENTION` with dark outline.
* **Headline**: Plain-language action: *"Call Nina & Raj Patel (Patel Insurance Group)"*.
* **Impact Badge**: `$2,500/mo Retainer ($30k/yr) + Overdue INV-1122 ($2,500)`.
* **Three Short Explanatory Statements**:
  1. Nina Patel submitted an unanswered contract review inquiry (Lead L097) & email Oct 2.
  2. Raj Patel sent heated complaints regarding missing regulatory branding on *'teen driver tips'* (V088, V121).
  3. Retainer invoice INV-1122 ($2,500) is 21 days late with payment withheld (mirrors Paul Grant / Meridian churn).
* **Controls**:
  * Primary Button: Dark charcoal button with white text: **"Prepare reminder"** (opens draft modal).
  * Secondary Button: Transparent/outline button: **"View evidence"** (jumps to Patel dossier/evidence).
  * Tertiary Button: Compact **"Defer"** control.
* **10-Second Test Rule**: The Hero Lime Card and its primary button must sit entirely above the fold on mobile (390×844 and 375×812 viewports).

### C. Secondary Actions
* Off-white cards (`#F7F9F6`) with subtle border (`#D2DBD1`).
* Action #2: *"Bill 3 completed shoots ($2,950) & reconcile customer credits ($2,400)"* (Vega Auto, Ironclad, DFW Founders). Button: **"Review invoices & credits"**.
* Action #3: *"Collect 8 overdue invoices ($6,750) & fix 6 billing tool errors"* (Crown Barbers, Lonestar RG, TLC). Button: **"Review collection queue"**.

### D. Business Summary Cards
* Rounded cards in `#F7F9F6` with large numbers in `#172018`:
  * **Overdue Payments**: `$9,250.00` (9 invoices past contractual due date).
  * **Work Not Yet Invoiced**: `$2,950.00` (3 completed chargeable shoots).
  * **Customer Credits Owed**: `$2,400.00` (Glow Aesthetics overpayment & Lone Star cancelled shoot).
  * **Requests Needing Attention**: `33` missed edit notes (0 logged on board).
  * **Inquiries Awaiting Reply**: `22` incoming leads with zero first reply.

### E. Explicit Confirmation Modal (Safety Protocol)
* Appears on clicking any action button.
* Clear disclaimer: *"Axeom will NEVER automatically send messages or modify external accounting ledgers. This action logs your review decision in the durable audit history."*
* Pre-drafted script with one-click **"Copy to Clipboard"** button.
* Custom owner note field.
* Decision action buttons: **"Mark In Progress"**, **"Mark Completed"**, **"Defer (24h)"**.
* State persists immediately to SQLite `owner_decisions` table.

---

## 5. Responsive Breakpoint Rules

| Viewport Width | Layout Behavior | Navigation System |
| :--- | :--- | :--- |
| **Mobile (375px - 430px)** | Single-column linear layout. Hero action visible in first viewport. Touch targets >= 44px. Text wraps naturally without horizontal overflow. | Floating frosted glass bottom dock with 5 quick tabs (Today, Money, Clients, Requests, History). |
| **Tablet (768px - 1023px)** | 2-column grid for secondary actions and metric cards. Top header includes quick filters. | Compact icon + label top bar or collapsible rail. |
| **Desktop (1024px - 1440px+)**| Left fixed sidebar (260px) in muted sage (`#D9E1DB`). Main content constrained to comfortable reading width (`1140px`). Balanced multi-column cards. | Full left sidebar with live status badges, audit date indicator, and direct file upload trigger. |
