# Tool Inventory Web Application - Product Requirements Document

**Project Name:** Tool Inventory System
**Document Version:** 2.0
**Date:** March 15, 2026
**Status:** Updated - Awaiting Final Approval

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Mar 15, 2026 | Initial draft with core features |
| 2.0 | Mar 15, 2026 | **Updated per user feedback:** <br>• Expanded database schema (image_url, brand_platform, serial_number, estimated_value)<br>• Dynamic locations (no hardcoded values)<br>• Manual add/edit form with mobile camera upload<br>• CSV export feature<br>• Accept any URL format (no strict validation)<br>• Confirmed merge strategy: (Item Name + Box) as composite key |

---

## 1. Executive Summary

### Problem Statement
We need to track a growing collection of 500-2,000 electrical, carpentry, and construction tools, plus spare parts across multiple storage locations. Current commercial solutions (like Sortly) have limitations that prevent us from efficiently managing our inventory. We need a custom, scalable system that provides instant visibility into what we have and where it is.

### Solution Overview
A lightweight, cloud-hosted web application with:
- **Bulk CSV import** for rapid data entry from existing tool documentation (with extended metadata support)
- **Manual add/edit forms** with mobile camera integration for taking tool photos
- **QR code generation** for physical box locations enabling instant mobile access
- **Alexa voice queries** for hands-free inventory lookups
- **Simple, fast search** with dynamic location and category filtering
- **CSV export** for data portability and backup

### Success Criteria
- ✅ Import 500+ items from CSV in under 2 minutes (including extended fields)
- ✅ QR code scan → item details with photos displayed in < 2 seconds
- ✅ Mobile camera upload → image stored and displayed in < 5 seconds
- ✅ Alexa responds to voice queries with 95%+ accuracy
- ✅ Dynamic filters populate from database (no hardcoded values)
- ✅ Export full inventory database to CSV in < 10 seconds
- ✅ Zero-cost hosting on free tiers (Supabase 500MB DB + 1GB Storage, Vercel)

---

## 2. Core Requirements

### 2.1 Functional Requirements

#### FR1: Bulk Data Import
- **FR1.1** Admin dashboard accepts CSV/Excel upload
- **FR1.2** CSV format: `Item Name, Category, Quantity, Box/Location, Dropbox URL`
- **FR1.3** Upload creates or updates items (merge strategy: match by Item Name + Box/Location)
- **FR1.4** Auto-extracts unique box locations and creates box records
- **FR1.5** Displays upload summary (items added, updated, errors)

#### FR2: QR Code System
- **FR2.1** Generate one unique QR code per physical box/location
- **FR2.2** QR code encodes URL: `https://[app-domain]/box/[box-id]`
- **FR2.3** Printable QR sheet (PDF) with box names and QR codes
- **FR2.4** Scanning QR opens mobile-optimized page showing all items in that box
- **FR2.5** Item details include: name, category, current quantity, Dropbox manual link (clickable)

#### FR3: Search & Filtering
- **FR3.1** Global search bar (searches item names and categories)
- **FR3.2** Location filter dropdown: Dynamically populated from unique box locations in database (e.g., "Truck 1", "Shop", "Jobsite A", "Warehouse")
- **FR3.3** Category filter dropdown: Dynamically populated from unique categories in database (e.g., "Electrical", "Carpentry", "Consumables")
- **FR3.4** Combined filters (e.g., "Electrical in Truck 1")
- **FR3.5** Search results display: Item name, category, quantity, box location, thumbnail image (if available)

#### FR4: Low Stock Highlighting
- **FR4.1** Each consumable item has configurable `low_stock_threshold` field
- **FR4.2** Frontend highlights rows (yellow/orange) when `quantity < low_stock_threshold`
- **FR4.3** Admin can set threshold during CSV upload or manual edit
- **FR4.4** Default threshold: 5 units (configurable globally)

#### FR5: Auto-Timestamping
- **FR5.1** Database field `last_updated` automatically updates on any quantity change
- **FR5.2** Timestamp displayed in item details view (e.g., "Last updated: Mar 15, 2026")
- **FR5.3** Helps identify stale data

#### FR6: Alexa Voice Integration
- **FR6.1** Custom Alexa Skill backend API endpoint
- **FR6.2** Query: "Alexa, how many [item name] do we have?" → responds with quantity
- **FR6.3** Query: "Alexa, where is the [item name]?" → responds with box location
- **FR6.4** Handles fuzzy matching (e.g., "wire cutter" matches "Wire Cutters - 8 inch")
- **FR6.5** Responds with "I found [X] items" if multiple matches

#### FR7: Manual Add/Edit Items
- **FR7.1** UI form to manually add new items with fields: name, category, quantity, box/location, brand/platform, serial number, estimated value, Dropbox URL, low stock threshold
- **FR7.2** Image upload field with mobile camera support (`<input type="file" accept="image/*" capture="environment">`)
- **FR7.3** Edit existing items via inline editing or dedicated edit modal
- **FR7.4** Image uploads saved to Supabase Storage bucket `tool-images/` and URL stored in `items.image_url`
- **FR7.5** Form validates required fields (name, category, quantity, box)

#### FR8: Data Export
- **FR8.1** "Export to CSV" button on admin dashboard
- **FR8.2** Exports entire inventory database to CSV with all fields (including image URLs)
- **FR8.3** CSV filename includes timestamp (e.g., `inventory-export-2026-03-15.csv`)
- **FR8.4** Prevents vendor lock-in by allowing full data portability

### 2.2 Non-Functional Requirements

#### NFR1: Performance
- Page load time < 2 seconds on 4G mobile connection
- Search results return in < 500ms for 2,000 items
- CSV upload processes 500 rows in < 30 seconds

#### NFR2: Usability
- Mobile-first responsive design (works on iPhone/Android)
- Minimal clicks to find items (search + filter in one view)
- No login required (single shared access)

#### NFR3: Scalability
- Support up to 10,000 items without performance degradation
- Database uses indexes on item_name, category, box_id

#### NFR4: Reliability
- 99.5% uptime (leveraging Vercel/Supabase SLAs)
- Automatic database backups (Supabase built-in)

#### NFR5: Security
- HTTPS only (enforced by Vercel)
- Supabase Row-Level Security (RLS) disabled for single-user mode
- No sensitive data stored (Dropbox URLs are team-accessible)

### 2.3 Out of Scope (Explicitly Excluded)

❌ User authentication/authorization (single shared access only)
❌ Item status tracking ("Available", "In Use", "Needs Repair")
❌ Check-out/check-in or loan tracking
❌ Maintenance schedules or service history
❌ Vendor/supplier integration
❌ Purchase history or depreciation tracking
❌ Multi-tenancy or team workspaces
❌ Mobile native app (mobile web only)
❌ Offline mode
❌ Alexa voice commands for updating quantities (read-only voice queries)

---

## 3. System Architecture

### 3.1 Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Backend** | FastAPI (Python 3.11+) | Fast, async, auto-generated API docs, easy deployment |
| **Database** | Supabase (PostgreSQL) | 500MB free, hosted, auto-backups, REST API, real-time subscriptions |
| **Image Storage** | Supabase Storage | 1GB free, S3-compatible, direct upload from mobile browsers |
| **Frontend** | HTML + TailwindCSS + Alpine.js | Lightweight, no build step, fast load, easy to customize |
| **QR Codes** | `qrcode` Python library | Simple, generates PNG/SVG QR codes |
| **Deployment** | Vercel (Frontend + Serverless Functions) | Free tier, GitHub integration, auto HTTPS, edge CDN |
| **File Storage** | Dropbox (existing) | Already used for tool manuals (URLs stored, not files) |
| **Voice** | Alexa Skill + AWS Lambda (optional) | If Alexa integration needed; or FastAPI endpoint |

### 3.2 Architecture Diagram

```
┌─────────────────┐
│   User Device   │
│  (Phone/Alexa)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│          Vercel Edge Network            │
│  ┌─────────────┐    ┌─────────────────┐ │
│  │  Frontend   │    │ API (Serverless │ │
│  │  (Static)   │◄──►│   Functions)    │ │
│  └─────────────┘    └────────┬────────┘ │
└─────────────────────────────┼───────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Supabase      │
                    │   (PostgreSQL)   │
                    │   - items table  │
                    │   - boxes table  │
                    └──────────────────┘
```

### 3.3 Data Flow

**1. CSV Upload Flow:**
```
Admin uploads CSV → FastAPI validates → Parses rows →
Extracts unique boxes → Creates/updates box records →
Creates/updates item records → Generates QR codes →
Returns success summary
```

**2. QR Scan Flow:**
```
User scans QR → Redirects to /box/{id} →
FastAPI fetches box + items → Returns HTML page →
User sees items + manual links
```

**3. Alexa Query Flow:**
```
User: "Alexa, how many wire strippers?" →
Alexa Skill → FastAPI /alexa/query →
Fuzzy search items → Returns quantity →
Alexa: "You have 3 wire strippers in Box A"
```

---

## 4. Database Schema

### 4.1 Tables

#### Table: `boxes`
Represents physical storage containers/locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique box identifier |
| `name` | VARCHAR(255) | UNIQUE, NOT NULL | Box name/label (e.g., "Box A - Warehouse") |
| `location` | VARCHAR(100) | NOT NULL | Primary location: Warehouse, Small Shed, Big Shed |
| `sublocation` | VARCHAR(100) | NULLABLE | Optional sub-location (e.g., "Shelf 2", "Corner") |
| `qr_code_url` | TEXT | NULLABLE | URL to generated QR code image (stored in Supabase Storage) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_boxes_location` on `location` (for filtering)
- `idx_boxes_name` on `name` (for search)

---

#### Table: `items`
Represents individual tools or parts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique item identifier |
| `name` | VARCHAR(255) | NOT NULL | Item name (e.g., "Wire Stripper - 8 inch") |
| `category` | VARCHAR(100) | NOT NULL | Category: Electrical, Carpentry, Consumables, etc. |
| `quantity` | INTEGER | NOT NULL, CHECK (>= 0) | Current stock quantity |
| `box_id` | UUID | FOREIGN KEY → boxes(id) | Which box contains this item |
| `dropbox_manual_url` | TEXT | NULLABLE | Link to PDF manual in Dropbox (accepts any URL) |
| `image_url` | TEXT | NULLABLE | Link to tool photo (stored in Supabase Storage) |
| `brand_platform` | VARCHAR(100) | NULLABLE | Brand/platform (e.g., "M18", "20V Max", "DeWalt") |
| `serial_number` | VARCHAR(100) | NULLABLE | Serial number for tracking |
| `estimated_value` | DECIMAL(10,2) | NULLABLE | Estimated value in USD |
| `low_stock_threshold` | INTEGER | DEFAULT 5 | Quantity below which item is flagged |
| `last_updated` | TIMESTAMP | DEFAULT NOW() | Auto-updated on quantity change |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `idx_items_box_id` on `box_id` (for box detail queries)
- `idx_items_category` on `category` (for filtering)
- `idx_items_name` on `name` (for search)
- `idx_items_name_trgm` using GIN (for fuzzy text search via pg_trgm extension)

**Triggers:**
- `update_last_updated` trigger: sets `last_updated = NOW()` on UPDATE of `quantity`

---

### 4.2 Relationships

```
boxes (1) ──< (many) items
   │
   └─ One box contains many items
   └─ Each item belongs to exactly one box
```

---

## 5. API Design

Base URL: `https://tool-inventory.vercel.app/api`

### 5.1 REST Endpoints

#### **POST /api/upload**
Upload CSV file to create/update inventory.

**Request:**
```http
POST /api/upload
Content-Type: multipart/form-data

file: [CSV file]
```

**CSV Format (Required Columns):**
```csv
Item Name,Category,Quantity,Box/Location,Dropbox URL
Wire Stripper - 8in,Electrical,3,Truck 1,https://dropbox.com/manual1.pdf
Hammer - 16oz,Carpentry,5,Shop,https://dropbox.com/manual2.pdf
```

**CSV Format (Extended with Optional Columns):**
```csv
Item Name,Category,Quantity,Box/Location,Brand/Platform,Serial Number,Estimated Value,Dropbox URL,Image URL
Wire Stripper - 8in,Electrical,3,Truck 1,Klein Tools,SN12345,29.99,https://dropbox.com/manual1.pdf,
Impact Driver,Power Tools,2,Jobsite A,M18,SN67890,149.99,https://dropbox.com/manual2.pdf,https://i.imgur.com/example.jpg
```

**Notes:**
- CSV parser accepts any URL format in Dropbox URL and Image URL columns (no strict validation)
- Merge strategy: (Item Name + Box/Location) is composite unique key. If match found, update quantity and other fields. If not found, create new item.
- Empty optional fields are allowed and stored as NULL

**Response:**
```json
{
  "success": true,
  "summary": {
    "items_created": 45,
    "items_updated": 12,
    "boxes_created": 3,
    "errors": []
  },
  "boxes": [
    {"id": "uuid-1", "name": "Box A - Warehouse", "qr_url": "https://..."},
    {"id": "uuid-2", "name": "Box B - Small Shed", "qr_url": "https://..."}
  ]
}
```

---

#### **GET /api/items**
Search and filter items.

**Query Parameters:**
- `search` (optional): Text search on item name
- `location` (optional): Filter by box location (Warehouse, Small Shed, Big Shed)
- `category` (optional): Filter by category (Electrical, Carpentry, Consumables)
- `limit` (optional): Results per page (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Example:**
```http
GET /api/items?search=wire&location=Warehouse&category=Electrical
```

**Response:**
```json
{
  "total": 2,
  "items": [
    {
      "id": "uuid-1",
      "name": "Wire Stripper - 8in",
      "category": "Electrical",
      "quantity": 3,
      "low_stock": false,
      "box": {
        "id": "uuid-box1",
        "name": "Box A - Warehouse",
        "location": "Warehouse"
      },
      "dropbox_manual_url": "https://dropbox.com/...",
      "last_updated": "2026-03-15T10:30:00Z"
    }
  ]
}
```

---

#### **GET /api/box/{box_id}**
Get details of a specific box and all items inside.

**Response:**
```json
{
  "box": {
    "id": "uuid-1",
    "name": "Box A - Warehouse",
    "location": "Warehouse",
    "sublocation": "Shelf 2",
    "qr_code_url": "https://..."
  },
  "items": [
    {
      "id": "uuid-item1",
      "name": "Wire Stripper - 8in",
      "category": "Electrical",
      "quantity": 3,
      "dropbox_manual_url": "https://...",
      "last_updated": "2026-03-15T10:30:00Z"
    }
  ]
}
```

---

#### **GET /api/qr/download**
Download printable PDF with all box QR codes.

**Response:** PDF file with QR codes and box labels.

---

#### **POST /api/alexa/query**
Alexa Skill backend endpoint.

**Request:**
```json
{
  "intent": "QuantityIntent",
  "slots": {
    "item": "wire stripper"
  }
}
```

**Response:**
```json
{
  "speech": "You have 3 wire strippers in Box A - Warehouse.",
  "reprompt": "Would you like to search for something else?"
}
```

---

#### **POST /api/item**
Create new item manually.

**Request:**
```json
{
  "name": "Impact Driver - 18V",
  "category": "Power Tools",
  "quantity": 2,
  "box_location": "Truck 1",
  "brand_platform": "M18",
  "serial_number": "SN123456",
  "estimated_value": 149.99,
  "dropbox_manual_url": "https://dropbox.com/manual.pdf",
  "low_stock_threshold": 1,
  "image_url": null
}
```

**Response:**
```json
{
  "success": true,
  "item": {
    "id": "uuid-new",
    "name": "Impact Driver - 18V",
    "quantity": 2,
    "created_at": "2026-03-15T14:22:00Z"
  }
}
```

---

#### **PUT /api/item/{item_id}**
Update existing item (any field).

**Request:**
```json
{
  "quantity": 10,
  "brand_platform": "20V Max",
  "estimated_value": 199.99
}
```

**Response:**
```json
{
  "success": true,
  "item": {
    "id": "uuid-1",
    "name": "Wire Stripper - 8in",
    "quantity": 10,
    "brand_platform": "20V Max",
    "last_updated": "2026-03-15T14:22:00Z"
  }
}
```

---

#### **POST /api/item/{item_id}/upload-image**
Upload tool image (mobile camera or file).

**Request:**
```http
POST /api/item/{item_id}/upload-image
Content-Type: multipart/form-data

image: [file]
```

**Response:**
```json
{
  "success": true,
  "image_url": "https://[supabase-project].supabase.co/storage/v1/object/public/tool-images/uuid-1.jpg"
}
```

---

#### **GET /api/export**
Export entire inventory to CSV.

**Response:**
```csv
Content-Type: text/csv
Content-Disposition: attachment; filename="inventory-export-2026-03-15.csv"

Item Name,Category,Quantity,Box/Location,Brand/Platform,Serial Number,Estimated Value,Dropbox URL,Image URL,Last Updated
Wire Stripper - 8in,Electrical,3,Box A - Warehouse,Klein Tools,SN12345,29.99,https://dropbox.com/...,https://supabase.co/...,2026-03-15T10:30:00Z
```

---

#### **GET /api/filters**
Get dynamic filter options (locations and categories).

**Response:**
```json
{
  "locations": ["Truck 1", "Shop", "Warehouse", "Jobsite A"],
  "categories": ["Electrical", "Carpentry", "Power Tools", "Consumables"]
}
```

---

## 6. Frontend Design

### 6.1 Key Screens

#### Screen 1: Admin Dashboard
**URL:** `/admin`

**Components:**
- CSV Upload section (drag-drop or file picker)
- Upload history table (recent uploads, status)
- "Download All QR Codes" button (generates PDF)
- **"Export to CSV" button** (downloads entire inventory database)
- **"Add New Item" button** (opens manual entry form)

---

#### Screen 2: Manual Add/Edit Form
**URL:** `/admin/item/new` or `/admin/item/{id}/edit`

**Components:**
- Form fields (with validation):
  - **Item Name*** (text, required)
  - **Category*** (dropdown or text, required)
  - **Quantity*** (number, required, min: 0)
  - **Box/Location*** (dropdown or text, required)
  - Brand/Platform (text, optional)
  - Serial Number (text, optional)
  - Estimated Value (number, optional, $)
  - Dropbox Manual URL (text/URL, optional)
  - Low Stock Threshold (number, optional, default: 5)
  - **Image Upload** (file input with mobile camera support)
    - `<input type="file" accept="image/*" capture="environment">`
    - Shows thumbnail preview after upload
- "Save" and "Cancel" buttons
- Mobile-optimized (large touch targets, native camera picker on phones)

---

#### Screen 3: Main Inventory View
**URL:** `/`

**Components:**
- Search bar (real-time search)
- **Filter dropdowns (dynamically populated from database):**
  - Location: "All" + unique locations (e.g., Truck 1, Shop, Warehouse)
  - Category: "All" + unique categories (e.g., Electrical, Power Tools)
- Results table:
  - Columns: Thumbnail, Item Name, Category, Quantity, Box Location, Actions (View/Edit)
  - Row highlighting: yellow if low stock
  - Click row to expand details (brand, serial number, estimated value, manual link)
- Pagination controls
- "Add New Item" floating action button (mobile)

---

#### Screen 4: Box Detail View (QR Target)
**URL:** `/box/{box_id}`

**Components:**
- Box name and location (header)
- List of all items in box (cards on mobile)
- Each item shows:
  - Thumbnail image (if available)
  - Name, category, quantity
  - Brand/platform, serial number (if available)
  - "View Manual" button (opens Dropbox link)
  - Last updated timestamp

---

### 6.2 Mobile Responsiveness
- All tables convert to card layout on mobile (< 768px width)
- Filter dropdowns become collapsible accordions
- QR scan view optimized for one-handed use
- Touch-friendly buttons (min 44px tap targets)

---

## 7. QR Code System

### 7.1 Generation Strategy

**When:**
- QR codes generated during CSV upload for new boxes
- Regeneration triggered if box name changes

**Format:**
- QR encodes: `https://tool-inventory.vercel.app/box/{box_id}`
- Image format: SVG (scalable) and PNG (300 DPI for printing)
- Stored in Supabase Storage bucket: `qr-codes/`

**Printable Sheet:**
- PDF layout: 2 columns, 6 QR codes per page
- Each QR includes:
  - QR code (2x2 inches)
  - Box name (bold, 14pt)
  - Location (12pt)

### 7.2 Scanning Experience

**User Flow:**
1. User scans QR with smartphone camera (iOS/Android native camera app)
2. Camera detects URL, shows notification "Open in browser?"
3. User taps → opens `/box/{box_id}` in mobile browser
4. Page loads in < 2 seconds, shows all items in box
5. User can tap manual links to view PDFs in Dropbox

**Error Handling:**
- If box not found → "Box not found. Please contact admin."
- If no items in box → "This box is currently empty."

---

## 8. Alexa Integration

### 8.1 Skill Architecture

**Option A: Direct FastAPI Endpoint** (Recommended for MVP)
- Alexa Skill calls `POST /api/alexa/query` directly
- FastAPI handles intent parsing and DB queries
- No AWS Lambda needed

**Option B: AWS Lambda Proxy**
- Alexa Skill → Lambda → FastAPI
- Lambda handles Alexa-specific auth/session
- More scalable, but adds complexity

**Recommendation:** Start with Option A (direct endpoint).

### 8.2 Voice Intents

#### Intent 1: `QuantityIntent`
**Utterances:**
- "how many {item} do we have"
- "what's the quantity of {item}"
- "how much {item} is left"

**Response Logic:**
1. Fuzzy match `{item}` against `items.name`
2. If 1 match → "You have {quantity} {item} in {box location}."
3. If multiple matches → "I found {count} items matching {item}. Which one?"
4. If no match → "I couldn't find {item} in the inventory."

#### Intent 2: `LocationIntent`
**Utterances:**
- "where is the {item}"
- "what box is the {item} in"
- "locate the {item}"

**Response Logic:**
1. Fuzzy match `{item}`
2. If found → "The {item} is in {box name}, located in {location}."
3. If not found → "I couldn't find {item} in the inventory."

---

## 9. Implementation Plan

### Phase 1: Database & Backend Foundation (Week 1)

**Goal:** Set up database and core API endpoints.

**Tasks:**
1. Create Supabase project
   - Set up `boxes` and `items` tables with new schema (including image_url, brand_platform, serial_number, estimated_value)
   - Create indexes and triggers (including auto-update trigger for last_updated)
   - Configure RLS (disabled for single-user mode)
   - Create Storage buckets: `tool-images/` and `qr-codes/` with public read access

2. Initialize FastAPI project
   - Project structure: `app/`, `models/`, `routes/`, `utils/`
   - Install dependencies: `fastapi`, `uvicorn`, `psycopg2-binary`, `qrcode`, `pandas`, `python-multipart`, `pillow`
   - Configure Supabase connection via environment variables
   - **Create `vercel.json`** for routing `/api/*` to Python serverless functions

3. Implement core API routes
   - `GET /api/items` (search & filter with dynamic locations/categories)
   - `GET /api/filters` (return unique locations and categories)
   - `GET /api/box/{box_id}` (box details)
   - `POST /api/item` (create new item)
   - `PUT /api/item/{item_id}` (update any field)
   - `POST /api/item/{item_id}/upload-image` (image upload to Supabase Storage)
   - `GET /api/export` (export inventory to CSV)

4. Write unit tests
   - Test database queries
   - Test filtering logic
   - Test CSV merge strategy (Item Name + Box as composite key)

**Deliverables:**
- ✅ Supabase database with updated schema and storage buckets
- ✅ FastAPI backend running locally with all new endpoints
- ✅ vercel.json configured for API routing
- ✅ API tests passing

---

### Phase 2: CSV Upload & QR Generation (Week 2)

**Goal:** Enable bulk import and QR code generation.

**Tasks:**
1. Implement CSV upload endpoint
   - Parse CSV with pandas (support both minimal and extended formats)
   - Validate required columns (Item Name, Category, Quantity, Box/Location)
   - Accept optional columns (Brand/Platform, Serial Number, Estimated Value, Image URL)
   - **Accept any URL format** (no strict validation for Dropbox or Image URLs)
   - Extract unique boxes from "Box/Location" column (dynamic, no hardcoded locations)
   - **Merge strategy:** Use (Item Name + Box/Location) as composite unique key
     - If match found: UPDATE quantity and all other provided fields
     - If not found: CREATE new item record

2. QR code generation
   - Generate QR codes for new boxes
   - Save QR images to Supabase Storage bucket `qr-codes/`
   - Update `boxes.qr_code_url` field

3. Generate printable QR PDF
   - Use `reportlab` library
   - Create 2-column layout
   - Include box names and QR codes

4. Admin dashboard frontend (basic)
   - CSV upload form
   - Upload status feedback
   - "Download QR Codes" button
   - **"Export to CSV" button** (downloads entire inventory)
   - **"Add New Item" button** (opens manual entry form)

**Deliverables:**
- ✅ CSV upload working end-to-end with new fields
- ✅ CSV merge logic working correctly
- ✅ QR codes generated and stored
- ✅ Printable PDF downloads
- ✅ CSV export working

---

### Phase 3: Frontend UI & Mobile Views (Week 3)

**Goal:** Build main inventory view and box detail page.

**Tasks:**
1. Set up frontend structure
   - HTML templates (Jinja2 or static HTML)
   - TailwindCSS via CDN
   - Alpine.js for interactivity

2. Build manual add/edit form (`/admin/item/new` and `/admin/item/{id}/edit`)
   - All fields: name, category, quantity, box/location, brand, serial, value, manual URL, threshold
   - **Image upload with mobile camera support:**
     - `<input type="file" accept="image/*" capture="environment">`
     - On mobile: triggers native camera app
     - Upload to Supabase Storage via API endpoint
     - Show thumbnail preview after upload
   - Form validation (required: name, category, quantity, box)
   - Mobile-optimized (large touch targets, native inputs)

3. Build main inventory page (`/`)
   - Search bar with debouncing
   - **Dynamic filter dropdowns:**
     - Fetch unique locations/categories from `/api/filters` endpoint
     - Location dropdown populated from database (e.g., "Truck 1", "Shop", "Warehouse")
     - Category dropdown populated from database (e.g., "Electrical", "Power Tools")
   - Results table with:
     - Thumbnail column (shows image if available)
     - Low-stock highlighting (yellow background)
     - Expandable rows (show brand, serial, value, manual link)
     - Edit/Delete actions
   - Pagination

4. Build box detail page (`/box/{box_id}`)
   - Mobile-optimized card layout
   - Show item thumbnails
   - Clickable manual links
   - Display brand, serial number if available
   - Last updated timestamps

5. Responsive design testing
   - Test on iPhone (Safari) with camera upload
   - Test on Android (Chrome) with camera upload
   - Fix any layout issues

**Deliverables:**
- ✅ Fully functional frontend with manual add/edit
- ✅ Mobile camera upload working
- ✅ Dynamic filters working
- ✅ Mobile-responsive on all screens
- ✅ Low-stock highlighting working

---

### Phase 4: Alexa Integration (Week 4)

**Goal:** Enable voice queries via Alexa.

**Tasks:**
1. Create Alexa Skill in Amazon Developer Console
   - Define interaction model
   - Set up intents (`QuantityIntent`, `LocationIntent`)
   - Add sample utterances

2. Implement `/api/alexa/query` endpoint
   - Parse Alexa request JSON
   - Handle intent routing
   - Fuzzy search logic (use `fuzzywuzzy` library)
   - Return Alexa-compatible response

3. Test with Alexa Simulator
   - Test quantity queries
   - Test location queries
   - Handle edge cases (no match, multiple matches)

4. Deploy and link Alexa Skill
   - Point Skill endpoint to production URL
   - Test with physical Alexa device

**Deliverables:**
- ✅ Alexa Skill published (beta/private)
- ✅ Voice queries working end-to-end
- ✅ Tested on real Alexa device

---

### Phase 5: Deployment & Production (Week 5)

**Goal:** Deploy to production and finalize.

**Tasks:**
1. Set up GitHub repository
   - Push all code
   - Add `.env.example` file
   - Write README.md

2. Deploy to Vercel
   - Connect GitHub repo
   - Configure environment variables (Supabase URL, API key)
   - Deploy frontend and API as serverless functions

3. Test production environment
   - Upload sample CSV
   - Scan QR codes with phone
   - Test Alexa queries against production API

4. Performance optimization
   - Enable Vercel Edge Caching
   - Add database connection pooling
   - Optimize images (QR codes)

5. Documentation
   - User guide for CSV format
   - Admin instructions for QR printing
   - Troubleshooting guide

**Deliverables:**
- ✅ App live at `https://tool-inventory.vercel.app`
- ✅ All features working in production
- ✅ Documentation complete

---

## 10. Success Metrics & Acceptance Criteria

### Acceptance Criteria (Pre-Launch Checklist)

- [ ] Upload CSV with 100 items completes in < 30 seconds
- [ ] All 100 items appear in database correctly
- [ ] QR codes generated for all unique boxes
- [ ] Scan QR on iPhone → page loads in < 2 seconds
- [ ] Search for "wire" returns relevant results instantly
- [ ] Filter by "Warehouse" + "Electrical" shows correct subset
- [ ] Low stock items (qty < 5) highlighted in yellow
- [ ] Manual links open Dropbox PDFs correctly
- [ ] Alexa query "how many hammers" returns correct quantity
- [ ] Alexa query "where is the drill" returns correct box location
- [ ] App works on mobile Safari and Chrome
- [ ] No console errors or broken links

### Post-Launch Metrics

**Operational Metrics:**
- Average search response time: < 500ms
- QR scan success rate: > 95%
- Alexa query accuracy: > 90%
- Uptime: > 99%

**User Metrics:**
- Time to find an item: < 10 seconds
- Admin CSV upload frequency: 1-2x per month
- Mobile usage: > 70% of traffic

---

## 11. Future Enhancements (Parking Lot)

**Not in MVP, but potential future additions:**

1. **Barcode scanning** (in addition to QR codes, for item-level tracking)
2. **Low stock email alerts** (weekly digest to email)
3. **Check-out tracking** (if requirements change to loan tracking)
4. **Alexa voice quantity updates** ("Alexa, subtract 2 hammers")
5. **Multi-user support** (team roles, permissions, audit logs)
6. **Mobile PWA** (offline mode, installable app)
7. **Analytics dashboard** (most-used items, usage trends, value insights)
8. **Barcode label printer integration** (print labels directly from app)
9. **Bulk edit/delete** operations (select multiple, batch actions)
10. **Purchase history tracking** (when items were bought, receipts)

---

## 12. Technical Considerations

### 12.1 Data Migration & Backup
- Supabase auto-backup enabled (7-day retention)
- Export CSV download feature for manual backups
- Database migration scripts in `migrations/` folder

### 12.2 Error Handling
- All API errors return consistent JSON format:
  ```json
  {
    "error": true,
    "message": "Human-readable error",
    "code": "ERROR_CODE"
  }
  ```
- Frontend displays user-friendly error messages
- Backend logs errors to console (Vercel logs)

### 12.3 Security
- Environment variables for secrets (Supabase API key)
- HTTPS enforced by Vercel
- Input validation on all endpoints (prevent SQL injection, XSS)
- Rate limiting on API endpoints (100 req/min per IP)

### 12.4 Testing Strategy
- **Unit tests:** FastAPI route handlers (pytest)
- **Integration tests:** Database queries (pytest + Supabase test DB)
- **E2E tests:** QR scan flow (manual testing on devices)
- **Load testing:** Apache Bench for 1000 concurrent searches

---

## 13. Open Questions & Decisions Needed

**RESOLVED:**
- ✅ QR mapping strategy: One QR per box (not per item)
- ✅ Database: Supabase PostgreSQL with extended schema (image_url, brand_platform, serial_number, estimated_value)
- ✅ Deployment: GitHub → Vercel pipeline
- ✅ User access: Single shared access (no auth)
- ✅ **CSV merge behavior:** (Item Name + Box/Location) is composite unique key. Update if match, create if new.
- ✅ **Locations:** Fully dynamic (no hardcoded values), populated from database
- ✅ **URL validation:** Accept any URL format without strict validation
- ✅ **Low stock threshold:** Global default 5, editable per item

**OPEN (for implementation phase):**
- **Image file size limits:** Set max upload size (recommendation: 5MB per image, resize to 1920px max width)
- **Storage cleanup:** Delete old QR codes/images when items/boxes are deleted? (recommendation: yes, implement cascade delete)

- **Alexa fuzzy matching:** What similarity score threshold (0-100)?
  - **Recommendation:** Use 80% similarity threshold (fuzzywuzzy ratio).

---

## 14. Project Timeline

| Phase | Duration | Start | End | Status |
|-------|----------|-------|-----|--------|
| Phase 1: Backend Foundation | 1 week | TBD | TBD | Not Started |
| Phase 2: CSV & QR | 1 week | TBD | TBD | Not Started |
| Phase 3: Frontend UI | 1 week | TBD | TBD | Not Started |
| Phase 4: Alexa Integration | 1 week | TBD | TBD | Not Started |
| Phase 5: Deployment | 1 week | TBD | TBD | Not Started |
| **Total** | **5 weeks** | - | - | - |

**Note:** Timeline assumes part-time effort (10-15 hours/week). Full-time development could compress to 2-3 weeks.

---

## 15. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Supabase free tier limits (500MB) | High | Low | Monitor usage, estimate 500MB supports ~10K items |
| QR codes not scanning reliably | High | Medium | Test with multiple devices, ensure high-contrast QR codes |
| Alexa fuzzy matching too inaccurate | Medium | Medium | Implement fallback: ask user to rephrase or show top 3 matches |
| CSV format inconsistencies | Medium | High | Add robust validation, show clear error messages, provide template |
| Vercel serverless function cold starts | Low | Medium | Accept 1-2s delay on first request, optimize later if needed |

---

## 16. Appendix

### 16.1 Sample CSV Format

**Minimal Format (Required Columns Only):**
```csv
Item Name,Category,Quantity,Box/Location,Dropbox URL
Wire Stripper - 8in,Electrical,3,Truck 1,https://www.dropbox.com/s/abc123/manual1.pdf
Hammer - 16oz,Carpentry,5,Shop,https://www.dropbox.com/s/def456/manual2.pdf
Screws - Phillips #8,Consumables,150,Warehouse,https://www.dropbox.com/s/ghi789/manual3.pdf
```

**Extended Format (All Columns):**
```csv
Item Name,Category,Quantity,Box/Location,Brand/Platform,Serial Number,Estimated Value,Dropbox URL,Image URL
Wire Stripper - 8in,Electrical,3,Truck 1,Klein Tools,SN-WS-12345,29.99,https://www.dropbox.com/s/abc123/manual1.pdf,
Impact Driver - M18,Power Tools,2,Jobsite A,Milwaukee M18,SN-ID-67890,149.99,https://www.dropbox.com/s/def456/manual2.pdf,https://i.imgur.com/example.jpg
Hammer - 16oz,Carpentry,5,Shop,Estwing,,19.99,https://www.dropbox.com/s/ghi789/manual3.pdf,
```

**Notes:**
- Empty optional fields are allowed (will be stored as NULL)
- Any URL format is accepted (Dropbox, Google Drive, direct links, etc.)
- Merge key: (Item Name + Box/Location). If match exists, updates record. Otherwise creates new.
- Dynamic locations: "Truck 1", "Shop", "Warehouse", "Jobsite A" etc. are not hardcoded

### 16.2 Environment Variables

```bash
# .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_STORAGE_URL=https://xxxxx.supabase.co/storage/v1
VERCEL_URL=https://tool-inventory.vercel.app
ALEXA_SKILL_ID=amzn1.ask.skill.xxxxx
MAX_IMAGE_SIZE_MB=5
```

### 16.3 Vercel Configuration

**vercel.json:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "app/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

**Purpose:**
- Routes `/api/*` requests to FastAPI Python backend (serverless functions)
- Routes all other requests to static frontend files
- Enables GitHub → Vercel automatic deployment pipeline

### 16.4 Project Folder Structure

```
tool-inventory/
├── README.md
├── PRD.md (this document)
├── requirements.txt
├── vercel.json (API routing configuration)
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py (FastAPI entry point)
│   ├── config.py (environment variables)
│   ├── models/
│   │   ├── box.py
│   │   └── item.py
│   ├── routes/
│   │   ├── items.py (GET, POST, PUT items + filters)
│   │   ├── boxes.py (GET box details)
│   │   ├── upload.py (POST CSV upload)
│   │   ├── export.py (GET CSV export)
│   │   ├── images.py (POST image upload)
│   │   ├── alexa.py (POST Alexa queries)
│   │   └── qr.py (GET QR PDF)
│   ├── services/
│   │   ├── db.py (Supabase client + storage)
│   │   ├── csv_parser.py (parse + merge strategy)
│   │   ├── qr_generator.py (QR code + PDF generation)
│   │   ├── image_handler.py (upload, resize, storage)
│   │   └── fuzzy_search.py (Alexa matching)
│   └── utils/
│       ├── validators.py
│       └── helpers.py
├── frontend/
│   ├── index.html (main inventory view)
│   ├── admin.html (upload dashboard)
│   ├── item-form.html (manual add/edit form)
│   ├── box.html (box detail QR target)
│   ├── css/
│   │   └── styles.css (custom styles, Tailwind overrides)
│   └── js/
│       ├── app.js (Alpine.js components)
│       ├── api.js (API client)
│       └── image-upload.js (camera capture logic)
├── tests/
│   ├── test_items.py
│   ├── test_boxes.py
│   ├── test_upload.py
│   └── test_alexa.py
├── migrations/
│   └── 001_initial_schema.sql
└── docs/
    ├── USER_GUIDE.md
    └── API_DOCS.md
```

### 16.5 Database Migration SQL

**migrations/001_initial_schema.sql:**
```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Create boxes table
CREATE TABLE boxes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    location VARCHAR(100) NOT NULL,
    sublocation VARCHAR(100),
    qr_code_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create items table
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    box_id UUID NOT NULL REFERENCES boxes(id) ON DELETE CASCADE,
    dropbox_manual_url TEXT,
    image_url TEXT,
    brand_platform VARCHAR(100),
    serial_number VARCHAR(100),
    estimated_value DECIMAL(10,2),
    low_stock_threshold INTEGER DEFAULT 5,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (name, box_id) -- Composite unique constraint for merge strategy
);

-- Create indexes for performance
CREATE INDEX idx_boxes_location ON boxes(location);
CREATE INDEX idx_boxes_name ON boxes(name);

CREATE INDEX idx_items_box_id ON items(box_id);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_name_trgm ON items USING GIN (name gin_trgm_ops); -- Fuzzy search

-- Create trigger to auto-update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_items_last_updated
BEFORE UPDATE ON items
FOR EACH ROW
WHEN (OLD.quantity IS DISTINCT FROM NEW.quantity OR
      OLD.name IS DISTINCT FROM NEW.name OR
      OLD.category IS DISTINCT FROM NEW.category)
EXECUTE FUNCTION update_last_updated();

-- Create trigger to auto-update boxes updated_at
CREATE TRIGGER trigger_update_boxes_updated_at
BEFORE UPDATE ON boxes
FOR EACH ROW
EXECUTE FUNCTION update_last_updated();

-- Create Supabase Storage buckets (run in Supabase SQL Editor or via API)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('tool-images', 'tool-images', true);
-- INSERT INTO storage.buckets (id, name, public) VALUES ('qr-codes', 'qr-codes', true);

-- Disable Row-Level Security for single-user mode (run in Supabase SQL Editor)
-- ALTER TABLE boxes DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE items DISABLE ROW LEVEL SECURITY;
```

**Notes:**
- The composite unique constraint `(name, box_id)` enforces the merge strategy
- Indexes optimize search queries for 2,000+ items
- Trigger automatically updates `last_updated` when quantity/name/category changes
- Supabase Storage buckets must be created manually or via API
- RLS (Row-Level Security) is disabled for single-user shared access

---

## Sign-Off

**Prepared by:** Claude (AI Product Manager & Software Architect)
**Document Version:** 2.0 (Updated with user feedback)
**Review Status:** Ready for Final Approval
**Next Steps:**
1. User reviews and approves PRD v2.0
2. Create `tool-inventory/` folder structure in workspace
3. Initialize GitHub repository
4. Begin Phase 1: Database & Backend Foundation

**Key Improvements in v2.0:**
- ✅ Extended database schema with image, brand, serial number, estimated value
- ✅ Dynamic locations (no hardcoded values)
- ✅ Manual add/edit form with mobile camera integration
- ✅ CSV export for data portability
- ✅ Flexible URL validation (accepts any format)
- ✅ Confirmed merge strategy and tech stack

---

**END OF PRD**
