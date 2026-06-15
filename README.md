# Digital Wallet Management System

A PayPal/EasyPaisa/JazzCash-style Digital Wallet with Django REST Framework backend and React frontend.

## Quick Start

### 1. Supabase (Free Database)
1. Create account at [supabase.com](https://supabase.com)
2. Create new project → Copy **Transaction Pooler** connection string
3. Format: `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`

### 2. Deploy to Vercel (FREE - Backend + Frontend)
1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com) → Import repo
3. Root Directory: `.` (leave as root)
4. Add Environment Variables:
   - `SECRET_KEY` = your-secret-key
   - `DATABASE_URL` = your-supabase-url
   - `DEBUG` = False
   - `CORS_ALLOW_ALL_ORIGINS` = True
5. Deploy!

### 3. Run Migrations (After first deploy)
```bash
# Install Vercel CLI
npm i -g vercel

# Link project
vercel link

# Run migrations
vercel env pull .env.local
python backend/manage.py migrate --settings=wallet_project.settings
python backend/manage.py createsuperuser --settings=wallet_project.settings
```

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Docs
- Swagger: `/api/docs/`
- ReDoc: `/api/redoc/`

## Free Tier Limits
| Service | Free Tier |
|---------|-----------|
| Vercel | 100GB bandwidth, Serverless Functions |
| Supabase | 500MB database, 50K auth users |
