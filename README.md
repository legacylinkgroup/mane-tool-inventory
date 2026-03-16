# Tool Inventory Web Application

A lightweight, cloud-hosted inventory management system for electrical, carpentry, and construction tools with QR code scanning and Alexa voice integration.

## 🎯 Project Overview

This application helps track 500-2,000+ tools and spare parts across multiple storage locations (trucks, shops, jobsites) with:
- **Bulk CSV import** with extended metadata (brand, serial number, estimated value, images)
- **QR code generation** for box locations → scan with phone to see contents
- **Alexa voice queries** → "Alexa, where is the circular saw?"
- **Mobile camera integration** → take photos of tools directly from the app
- **Dynamic search & filtering** → locations and categories populate from database
- **CSV export** → full data portability, no vendor lock-in

## 📚 Documentation

- **[PRD.md](PRD.md)** - Complete Product Requirements Document with:
  - System architecture
  - Database schema (SQL migration script included)
  - API design (10 REST endpoints)
  - Frontend design (4 screens)
  - 5-phase implementation plan
  - Deployment guide (GitHub → Vercel)

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI (Python 3.11+) | Fast, async, auto-docs |
| Database | Supabase (PostgreSQL) | 500MB free, hosted, auto-backups |
| Storage | Supabase Storage | 1GB free, images & QR codes |
| Frontend | HTML + TailwindCSS + Alpine.js | Lightweight, no build step |
| Deployment | Vercel | Free tier, GitHub auto-deploy |
| Voice | Alexa Skill | Hands-free inventory queries |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account (free tier)
- Vercel account (free tier)
- Git & GitHub

### Phase 1: Database Setup

1. **Create Supabase project:**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Copy project URL and API key

2. **Run database migration:**
   - Open Supabase SQL Editor
   - Run the SQL script from `PRD.md` Section 16.5
   - Creates `boxes` and `items` tables with indexes and triggers

3. **Create storage buckets:**
   ```sql
   INSERT INTO storage.buckets (id, name, public) VALUES ('tool-images', 'tool-images', true);
   INSERT INTO storage.buckets (id, name, public) VALUES ('qr-codes', 'qr-codes', true);
   ```

### Phase 2: Local Development

1. **Clone and install:**
   ```bash
   cd tool-inventory
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Run locally:**
   ```bash
   uvicorn app.main:app --reload
   # API: http://localhost:8000
   # Docs: http://localhost:8000/docs
   ```

### Phase 3: Deploy to Vercel

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import GitHub repository
   - Add environment variables (Supabase URL, API key)
   - Deploy!

## 📋 CSV Import Format

**Minimal Format (Required):**
```csv
Item Name,Category,Quantity,Box/Location,Dropbox URL
Wire Stripper - 8in,Electrical,3,Truck 1,https://dropbox.com/manual1.pdf
```

**Extended Format (All Fields):**
```csv
Item Name,Category,Quantity,Box/Location,Brand/Platform,Serial Number,Estimated Value,Dropbox URL,Image URL
Impact Driver,Power Tools,2,Jobsite A,M18,SN67890,149.99,https://dropbox.com/manual.pdf,https://imgur.com/img.jpg
```

## 📱 Features

### Core Features (MVP)
- ✅ Bulk CSV upload with merge strategy
- ✅ Manual add/edit form with mobile camera
- ✅ QR code generation per box location
- ✅ Mobile-responsive search & filtering
- ✅ Low stock highlighting
- ✅ Auto-timestamp tracking
- ✅ Alexa voice queries (read-only)
- ✅ CSV export for data portability

### Future Enhancements (Parking Lot)
- Barcode scanning for item-level tracking
- Low stock email alerts
- Check-out/check-in tracking
- Multi-user roles & permissions
- Mobile PWA with offline mode
- Analytics dashboard

## 🗂️ Project Structure

```
tool-inventory/
├── PRD.md                    # Product Requirements Document
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment config
├── .env.example             # Environment variables template
├── app/                     # FastAPI backend
│   ├── main.py             # Entry point
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── models/             # Database models
├── frontend/               # Static HTML/CSS/JS
│   ├── index.html         # Main inventory view
│   ├── admin.html         # Upload dashboard
│   ├── item-form.html     # Add/edit form
│   └── box.html           # QR scan target
├── migrations/            # Database migration scripts
└── tests/                 # Unit & integration tests
```

## 🎯 Success Criteria

- ✅ Import 500+ items from CSV in < 2 minutes
- ✅ QR scan → item details in < 2 seconds
- ✅ Mobile camera → image uploaded in < 5 seconds
- ✅ Alexa query accuracy > 95%
- ✅ Zero-cost hosting (Supabase + Vercel free tiers)

## 📞 Support

See [PRD.md](PRD.md) for:
- Complete API documentation
- Database schema details
- Implementation phases
- Troubleshooting guide

---

**Status:** 📝 PRD Approved - Ready for Implementation
**Next Steps:** Begin Phase 1 (Database & Backend Foundation)
