# DEPLOYMENT GUIDE - Digital Wallet on Vercel + Supabase (100% FREE)

> Backend = Django REST Framework (Vercel Serverless)
> Frontend = React + Vite (Vercel Static)
> Database = Supabase PostgreSQL (Free Tier)
> Total Cost = $0

---

## STEP 1: Create Supabase Database (FREE)

1. Go to https://supabase.com and click **"Start your project"**
2. Sign up using GitHub (easiest)
3. Click **"New Project"**
   - **Project Name**: `digital-wallet`
   - **Database Password**: Choose a strong password — **WRITE IT DOWN, you'll need it!**
   - **Region**: Pick the one closest to you
4. Wait 2-3 minutes while Supabase creates your database
5. Once ready, go to **Settings** (gear icon, bottom left) → **Database**
6. Scroll down to **"Connection string"** section
7. Select the **"Transaction pooler"** tab (NOT "Direct connection")
8. Copy the URI — it looks like:
   ```
   postgresql://postgres.xxxxx:YOUR-PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
   **This is your DATABASE_URL — SAVE IT!**

> **Why Transaction Pooler?** Vercel serverless functions create many short-lived connections. The pooler (port 6543) handles this efficiently. Direct connection (port 5432) would exhaust connection limits.

---

## STEP 2: Extract ZIP and Push to GitHub

### 2a. Extract the ZIP file
Extract `digital-wallet.zip` to a folder on your computer.

### 2b. Create a GitHub repository
1. Go to https://github.com → Click **"New"** (green button, top right)
2. Repository name: `digital-wallet`
3. Make it **Private** or **Public** (your choice)
4. **DO NOT** check "Add a README" or "Add .gitignore" — leave all unchecked
5. Click **"Create repository"**

### 2c. Push your code to GitHub
Open a terminal/command prompt and run these commands:

```bash
# Navigate to the extracted folder
cd digital-wallet

# Initialize Git
git init

# Add all files
git add .

# Create first commit
git commit -m "Digital Wallet Management System - Initial commit"

# Rename branch to main
git branch -M main

# Connect to your GitHub repo (REPLACE YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/digital-wallet.git

# Push to GitHub
git push -u origin main
```

> If GitHub asks you to login, use your GitHub username and a Personal Access Token (not your password). To create a token: GitHub → Settings → Developer Settings → Personal Access Tokens → Generate new token (select "repo" scope).

---

## STEP 3: Deploy on Vercel

### 3a. Sign up on Vercel
1. Go to https://vercel.com
2. Click **"Sign Up"** → Choose **"Continue with GitHub"**
3. Authorize Vercel to access your GitHub

### 3b. Import your project
1. On the Vercel dashboard, click **"Add New..."** → **"Project"**
2. You should see your `digital-wallet` repo — click **"Import"**
   - If you don't see it, click "Adjust GitHub App Permissions" and grant access

### 3c. Configure the project
Fill in these settings:

| Setting | Value |
|---------|-------|
| **Project Name** | `digital-wallet` (or whatever you want) |
| **Framework Preset** | **Other** |
| **Root Directory** | Click "Edit" → leave as `.` (dot, meaning root) |
| **Build and Output Settings** | Leave defaults (override is NOT needed) |

### 3d. Add Environment Variables
Click **"Environment Variables"** and add these one by one:

| Name | Value |
|------|-------|
| `SECRET_KEY` | A random secret key, e.g. `dw-8k2m$n4p!q7r*s0t1u2v3w4x5y6z7a9b0c` |
| `DATABASE_URL` | Your Supabase pooler connection string from Step 1 |
| `DEBUG` | `False` |
| `CORS_ALLOW_ALL_ORIGINS` | `True` |
| `ALLOWED_HOSTS` | `.vercel.app,localhost,127.0.0.1` |

> **How to add each variable**: Type the Name, type the Value, click the "+" button, then add the next one.

### 3e. Deploy
Click **"Deploy"** and wait 2-3 minutes.

You'll see a building animation. When it's done, you'll get your live URL:
```
https://digital-wallet-xxxx.vercel.app
```

> **BUT** — your database tables aren't created yet! You need to run migrations next.

---

## STEP 4: Run Database Migrations (CRITICAL)

Your Supabase database is empty right now. You need to create the tables.

### Option A: Run locally against Supabase (RECOMMENDED)

This is the easiest and most reliable method:

```bash
# 1. Navigate to the backend folder
cd digital-wallet/backend

# 2. Create a Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set the DATABASE_URL to your Supabase connection string
# On Windows (Command Prompt):
set DATABASE_URL=postgresql://postgres.xxxxx:YOUR-PASSWORD@aws-0-region.pooler.supabase.com:6543/postgres
# On Windows (PowerShell):
$env:DATABASE_URL="postgresql://postgres.xxxxx:YOUR-PASSWORD@aws-0-region.pooler.supabase.com:6543/postgres"
# On Mac/Linux:
export DATABASE_URL="postgresql://postgres.xxxxx:YOUR-PASSWORD@aws-0-region.pooler.supabase.com:6543/postgres"

# 6. Run migrations (this creates all tables in Supabase)
python manage.py migrate

# 7. Create a superuser (admin account)
python manage.py createsuperuser
# Enter username, email, password when prompted

# 8. Verify tables were created
python manage.py showmigrations
# All should show [X] (checked)
```

### Option B: Using Supabase SQL Editor

If Option A doesn't work for you:

1. Run the project locally with SQLite first:
   ```bash
   cd digital-wallet/backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   ```
2. Go to Supabase Dashboard → **SQL Editor**
3. You can run the SQL generated by Django's migrations manually
4. This is more tedious, so try Option A first

---

## STEP 5: Test Your Live App

1. Visit your Vercel URL: `https://digital-wallet-xxxx.vercel.app`
2. You should see the landing page with the purple theme
3. Click **"Get Started"** → Register a new account
4. After registration, your wallet is auto-created with **$1,000 balance**
5. Test these features:
   - **Dashboard** — see your balance and recent transactions
   - **Send Money** — enter a wallet number and amount (you need 2 accounts)
   - **Receive Money** — see your wallet number, share it
   - **Settings** → **Set Transaction PIN** — set a 4-digit PIN
   - After setting PIN, **Send Money** will ask for PIN confirmation
   - **Transactions** — view transaction history with filters
   - **Dark/Light mode** — toggle in Settings or navbar

6. For **Admin Dashboard**: Login with your superuser account → navigate to `/admin`

---

## STEP 6: Verify Supabase Connection

To confirm your app is actually using Supabase:

1. Go to **Supabase Dashboard** → **Table Editor**
2. You should see these tables:
   - `users` — your registered users
   - `wallets_wallet` — wallet data with balances
   - `transactions_transaction` — transaction records
   - `refunds_refund` — refund requests
   - `notifications_notification` — notifications
   - `accounts_auditlog` — audit trail
3. Click on `users` table → you should see your registered user(s)
4. Click on `wallets_wallet` → you should see the wallet with $1000 balance
5. Every transaction, registration, etc. will appear here in real-time!

---

## TROUBLESHOOTING

### Problem: "500 Internal Server Error" on API calls
**Fix**: Check Vercel function logs:
1. Go to Vercel Dashboard → your project → **Logs** tab
2. Look for error messages
3. Common cause: missing environment variable or wrong DATABASE_URL

### Problem: "CORS error" in browser console
**Fix**: Make sure you added `CORS_ALLOW_ALL_ORIGINS=True` in Vercel environment variables.

### Problem: "Migration table already exists"
**Fix**: This means migrations already ran. Check Supabase Table Editor to confirm tables exist.

### Problem: "Cold start takes 2-3 seconds"
**Fix**: This is normal for serverless. After the first request, subsequent requests are fast (<100ms).

### Problem: "psycopg2" build error on Windows
**Fix**: Use `psycopg2-binary` instead (it's already in requirements.txt). If still failing:
```bash
pip install psycopg2-binary
```

### Problem: "Port 6543 connection refused"
**Fix**: Use the **Transaction pooler** URL (port 6543) from Supabase Settings. Make sure you selected "Transaction pooler" not "Direct connection".

---

## FREE TIER LIMITS

| Platform | Limit |
|----------|-------|
| **Vercel** | 100GB bandwidth/month, 100K serverless calls/day, unlimited deployments |
| **Supabase** | 500MB database, 50K monthly active users, 500MB file storage, 5GB bandwidth |

These limits are generous for a personal project or small app.

---

## HOW THE DEPLOYMENT WORKS

```
Your Vercel URL (https://digital-wallet.vercel.app)
         │
         ├── /api/*  ──────────►  Vercel Python Serverless Function
         │                           │
         │                           ├── Django REST Framework
         │                           ├── JWT Authentication
         │                           └── Connects to Supabase PostgreSQL
         │
         └── /*  ──────────────►  Vercel Static Hosting
                                     │
                                     └── React + Vite (built HTML/JS/CSS)
```

- **Frontend**: Static files served directly (fast!)
- **Backend**: Django runs as a Python serverless function
- **Database**: Supabase PostgreSQL, accessed via connection pooler
- **All requests**: Go through Vercel's CDN (global edge network)
