# Axeom Challenge — Data Inventory & Source File Audit

This document provides a reproducible, cryptographic inventory and structural audit of all business data files supplied in `data/`.

---

## 1. File Integrity & Basic Properties

| Filename | Byte Size | SHA-256 Checksum | Encoding | Delimiter | Header Count | Logical Data Rows |
|---|---|---|---|---|---|---|
| `bookings.csv` | 15,000 | `f697a35b82ebf6ba7b27ef0119d56fc83101dbaa1985dad5c05d181494f407e6` | UTF-8 | `,` | 7 | 175 |
| `costs.csv` | 215 | `fd04cb418e7de02caff27dc84836dec425079e0b8aa67615712db89e09e3a092` | UTF-8 | `,` | 3 | 2 |
| `invoices.csv` | 15,411 | `9a4cdfd02fe6c91cff8b44498b6df1da8001eda39aacf04a0c6a192ce769ab34` | UTF-8 | `,` | 8 | 152 |
| `leads.csv` | 10,505 | `51ab96783265d9a4e0040bbeb094f79b5ac97db59311864595473d9e5e8249f8` | UTF-8 | `,` | 9 | 99 |
| `messages.txt` | 27,439 | `29ecbd05b322a78e10ec82e38728ac9909ed666cd4511cd258e3b8da41438f18` | UTF-8 | N/A (Text) | 0 | 208 logical messages |
| `payments.csv` | 9,946 | `a422c617884347e071867d43d93b2abfe4e4c1aca03a24398b8f4f60cc6ded4e` | UTF-8 | `,` | 7 | 131 |
| `production_board.csv` | 24,412 | `6dfc64cf8912ed6bb4e80f390163babbe4a30a20a27cb92fb2e5fb2a5ab7ac22` | UTF-8 | `,` | 10 | 333 |
| `team.csv` | 187 | `0901d17c2002be2b20e1dd6bbbecbbda0f3cc38a3ecb80cc91c309c911176e42` | UTF-8 | `,` | 4 | 5 |

*Total raw rows across tabular files*: 904 rows.  
*Total logical communication events*: 208 messages.

---

## 2. Table-by-Table Schema & Data Quality Audit

### 2.1 `bookings.csv`
- **Discovered Columns**: `booking_id`, `date`, `client_name`, `email`, `service`, `status`, `price`
- **Primary Key**: `booking_id` (175 unique values, range `B001`–`B175`, 0 duplicates).
- **Missing / Null Values**: 0 nulls across all fields.
- **Data Types & Encodings**:
  - `date`: String in `DD/MM/YYYY` format (e.g. `04/03/2026`, `16/04/2026`). Must NOT be parsed as `MM/DD/YYYY`.
  - `price`: Mixed currency strings (e.g. `"$1,500"`, `"$300"`, `"300"`, `"900"`). Requires normalization removing `$` and `,`.
  - `status`: Categorical values: `completed` (157), `upcoming` (17), `cancelled` (1: `B148` for Lone Star Realty).
  - `service`: `Reels Pack` (57), `Podcast Studio 2hr` (53), `Content Day` (28), `Retainer Shoot` (22), `Podcast Studio 4hr` (15).
- **Quality Observations**:
  - Contains one email typo: `sarah@khandental.con` on booking `B045` (matching `Dr. Sarah Khan`).

### 2.2 `invoices.csv`
- **Discovered Columns**: `invoice_no`, `bill_to`, `email`, `issued`, `due`, `amount`, `status`, `memo`
- **Primary Key**: `invoice_no` (152 unique values, range `INV-1001`–`INV-1152`, 0 duplicates).
- **Missing / Null Values**: `memo` is null/empty in 21 rows.
- **Data Types & Encodings**:
  - `issued`, `due`: ISO `YYYY-MM-DD` strings.
  - `amount`: Decimal strings (e.g. `"300.00"`, `"1500.00"`).
  - `status`: `paid` (129), `unpaid` (21), `partial` (1: `INV-1077`), `void` (1: `INV-1147`).
  - `memo`: Free text frequently referencing bookings (e.g. `"B003 Content Day"`, `"Podcast Studio 2hr 4/3"`).

### 2.3 `payments.csv`
- **Discovered Columns**: `payment_id`, `date`, `payer`, `payer_email`, `amount`, `method`, `reference`
- **Primary Key**: `payment_id` (131 unique values, range `P5001`–`P5131`, 0 duplicates).
- **Missing / Null Values**: `reference` is blank/empty in 24 rows; `payer_email` is blank in 4 rows (Tony Russo `P5077`, `P5119`; Tasha Green `P5104`; J Reed `P5101`).
- **Data Types & Encodings**:
  - `date`: String in `DD/MM/YYYY` format (e.g., `05/04/2026`, `16/04/2026`).
  - `method`: `card` (59), `Zelle` (37), `ACH` (35).
  - `reference`: 101 records reference an exact `invoice_no` (`INV-xxxx`). 30 records have non-invoice or missing references:
    - 24 blank strings `""`
    - 4 agency batch payments from `BRIGHTLINE MARKETING LLC`: `"Brightline Jun invoices"`, `"Brightline Jul invoices"`, `"Brightline Aug invoices"`, `"Brightline Sep invoices"`
    - 1 informal reference: `"august sessions"` (`P5104`, Tasha Green)
    - 1 installment reference: `"half now half later"` (`P5119`, Tony Russo)

### 2.4 `production_board.csv`
- **Discovered Columns**: `video_id`, `client`, `title`, `editor`, `stage`, `notes_on_board`, `revisions`, `editor_hours`, `client_approved_on`, `shoot_booking`
- **Primary Key**: `video_id` (333 unique values, range `V001`–`V333`, 0 duplicates).
- **Missing / Null Values**: `notes_on_board` empty in 259 rows; `client_approved_on` empty in 163 rows; `shoot_booking` empty in 85 rows.
- **Data Types & Encodings**:
  - `stage`: `Delivered` (306), `In edit` (17), `In review` (7), `In revision` (3).
  - `editor`: `Rita` (129), `Ali` (120), `Sam` (70), `Dev` (14).
  - `revisions`: Integer count of revisions (ranges 0 to 3).
  - `editor_hours`: Decimal hours (ranges 2.4 to 7.8 hours).
  - `shoot_booking`: 248 videos link to a valid `booking_id`; 85 videos have no booking ID (e.g. retainer shoots or independent edits).

### 2.5 `leads.csv`
- **Discovered Columns**: `lead_id`, `created`, `name`, `business`, `email`, `phone`, `source`, `first_reply`, `status`
- **Primary Key**: `lead_id` (99 unique values, range `L001`–`L099`, 0 duplicates).
- **Missing / Null Values**: `business` missing in 16 rows; `phone` missing in 4 rows; `first_reply` missing/empty in **22 rows**.
- **Data Types & Encodings**:
  - `created`: `YYYY-MM-DD HH:MM`.
  - `first_reply`: `YYYY-MM-DD` or empty string.
  - `status`: `Lost` (43), `Won` (28), `New` (23), `Talking` (5).
  - `source`: `Meta ad` (27), `Website form` (20), `Instagram` (18), `Google` (15), `LinkedIn` (12), `Referral` (7).
- **Unreplied Leads Discovery**: Exactly 22 leads have an empty `first_reply` field (`L020`, `L023`, `L034`, `L035`, `L044`, `L048`, `L062`, `L065`, `L067`, `L071`, `L075`, `L076`, `L078`, `L080`, `L082`, `L083`, `L084`, `L087`, `L088`, `L090`, `L097`, `L098`).

### 2.6 `messages.txt`
- **Format**: Plain text log of communication events.
- **Message Boundary Discovery**:
  - Pattern: `^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]\s+([A-Z\s]+)\s+(from|to)\s+([^:]+):\s*(.*)$`
  - Total raw lines: 208.
  - Total parsed logical messages: 208 (each header initiates exactly one logical communication record).
  - Channels: `EMAIL` (89), `WHATSAPP` (85), `VOICE NOTE` (23), `INSTAGRAM DM` (9), `WEBSITE FORM` (2).
  - Directions: `from` (206 incoming), `to` (2 outgoing).
  - Cross-Reference Capability: Senders include email addresses, phone numbers, and names. 137 messages match exact video titles on `production_board.csv`.

### 2.7 `team.csv` & `costs.csv`
- `team.csv`: 5 records defining team members:
  - `Zaid` (Owner, pay null/owner draw)
  - `Ali` (Editor, $35/hour)
  - `Rita` (Editor, $30/hour)
  - `Sam` (Editor, $22/hour)
  - `Dev` (Editor freelance, joined 2026-09-01, $40/hour)
- `costs.csv`: Studio operating cost rates:
  - Studio time: $40/hour (Content Day = 6 hours, Reels Pack = 3 hours, Retainer Shoot = 4 hours, Podcast sessions = booked hours).
  - Editor time: Governed by `team.csv` hourly pay applied to `editor_hours` on `production_board.csv`.
