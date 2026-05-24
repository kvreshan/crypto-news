# 🚀 CryptoSignals LK — Complete Setup Guide

## Overview
Automated crypto news site with:
- AI-generated articles (Claude + Gemini backup)
- Copyright-free images (Unsplash + Pexels backup)
- Admin dashboard (magic link login)
- Adsterra ad management
- Affiliate links management
- Auto-publish via GitHub Actions (free)
- Hosted on Vercel (free)
- Database on Supabase (free)

---

## 📋 Prerequisites

Get these free accounts/keys before starting:

| Service | URL | Notes |
|---------|-----|-------|
| Supabase | supabase.com | Free 500MB |
| Vercel | vercel.com | Free hosting |
| GitHub | github.com | Free automation |
| Anthropic | console.anthropic.com | $5 deposit needed |
| Gemini | aistudio.google.com | 100% free |
| Unsplash | unsplash.com/developers | Free 50 req/hr |
| Pexels | pexels.com/api | Free 200 req/hr |

---

## STEP 1 — Supabase Setup

1. Go to **supabase.com** → Create new project
2. Name: `crypto-news`
3. Region: **Singapore** (closest to Sri Lanka)
4. Note your **Database Password**

5. Go to **SQL Editor** → New query
6. Copy contents of `supabase_setup.sql`
7. Paste → Click **Run**

8. Go to **Settings → API**
9. Copy:
   - **Project URL** → `https://xxxx.supabase.co`
   - **anon public** key
   - **service_role** key (keep secret!)

10. Go to **Authentication → URL Configuration**
11. Add Site URL: `https://your-project.vercel.app`
12. Add Redirect URL: `https://your-project.vercel.app/admin/dashboard.html`

---

## STEP 2 — Update Config Files

Open `public/js/config.js` and replace:
```javascript
SUPABASE_URL: 'YOUR_SUPABASE_URL',        // paste your URL
SUPABASE_ANON_KEY: 'YOUR_SUPABASE_ANON_KEY',  // paste anon key
```

---

## STEP 3 — Deploy to Vercel

1. Push this project to **GitHub** (new repo)
2. Go to **vercel.com** → New Project
3. Import your GitHub repo
4. Click **Deploy** (no config needed — vercel.json handles it)
5. Copy your Vercel URL: `https://your-project.vercel.app`

---

## STEP 4 — Setup GitHub Secrets

Go to GitHub repo → **Settings → Secrets → Actions** → New secret

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Your service_role key |
| `ANTHROPIC_API_KEY` | sk-ant-... |
| `GEMINI_API_KEY` | AIza... |
| `UNSPLASH_ACCESS_KEY` | Your Unsplash key |
| `PEXELS_API_KEY` | Your Pexels key |

---

## STEP 5 — Test Automation

1. Go to GitHub repo → **Actions**
2. Click **Crypto News Automation**
3. Click **Run workflow** → Run workflow
4. Watch the logs — should see articles being generated
5. Check your Supabase `news` table — articles should appear
6. Check your live site — articles should be visible!

---

## STEP 6 — Admin Dashboard Login

1. Go to `https://your-project.vercel.app/admin/login.html`
2. Enter your email
3. Click **Send Magic Link**
4. Check email → Click the link
5. You're in! 🎉

---

## STEP 7 — Add Adsterra Ads

1. Login to Adsterra → Get ad code
2. Go to admin dashboard → **Ad Codes**
3. Click **+ Add Ad Code**
4. Select placement (header, article, sidebar, etc.)
5. Paste Adsterra code → Save
6. Ad goes live immediately ✅

---

## STEP 8 — Add Affiliate Links

1. Sign up for Binance/Bybit/OKX affiliate program
2. Get your referral URL
3. Go to admin → **Affiliate Links**
4. Add your links with coin tags
5. Links auto-appear on articles and sidebar

---

## 🔄 Automation Schedule

Runs automatically at:
- **8:00 AM** Sri Lanka time (daily)
- **5:00 PM** Sri Lanka time (daily)

Each run generates **3 articles** from trending coins.

To change schedule, edit `.github/workflows/automation.yml`:
```yaml
- cron: '0 2 * * *'    # Change this
```
Use https://crontab.guru to build cron expressions.

---

## 📁 File Structure

```
crypto-news/
├── public/                 → Public website
│   ├── index.html          → Homepage (news feed)
│   ├── signals.html        → Signals page
│   ├── article/
│   │   └── index.html      → Single article page
│   ├── css/
│   │   └── style.css       → Dark crypto theme
│   └── js/
│       ├── config.js       → Your Supabase credentials
│       ├── supabase.js     → Database helpers
│       ├── ads.js          → Ad injection
│       ├── index.js        → Homepage logic
│       └── article.js      → Article page logic
│
├── admin/                  → Admin dashboard
│   ├── login.html          → Magic link login
│   ├── dashboard.html      → Overview + analytics
│   ├── news.html           → Manage articles
│   ├── affiliates.html     → Manage affiliate links
│   ├── ads.html            → Manage Adsterra codes
│   ├── css/admin.css       → Admin styles
│   └── js/auth.js          → Auth helpers
│
├── automation/
│   └── run.py              → Python automation script
│
├── .github/workflows/
│   └── automation.yml      → GitHub Actions cron
│
├── supabase_setup.sql      → Database setup SQL
├── vercel.json             → Vercel config
├── .env.example            → Environment variables template
└── .gitignore
```

---

## 💰 Monetization

1. **Adsterra** — Add ad codes via admin dashboard
2. **Affiliate Links** — Binance/Bybit/OKX auto-inserted in articles
3. **Telegram** — Link your channel in Settings

---

## 🛠️ Troubleshooting

**Articles not generating?**
- Check GitHub Actions logs for error details
- Verify all secrets are set correctly
- Check Claude/Gemini API keys are valid

**Admin login not working?**
- Verify Supabase redirect URL includes your Vercel domain
- Check spam folder for magic link email

**Ads not showing?**
- Make sure ad code is marked as Active in admin
- Check browser console for script errors

**Images not loading?**
- Verify Unsplash and Pexels API keys in GitHub secrets
- Default fallback images will be used if both fail

---

## 📞 Support

All code is plain HTML/CSS/JS + Python.
No frameworks, no build step, just works. ✅
