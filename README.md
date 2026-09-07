# Phase 8 - Full Stack App with Resend Email

## Email Features
- ✅ Email verification on registration
- ✅ Password reset via email
- ✅ Welcome emails
- ✅ Beautiful HTML templates
- ✅ Powered by Resend

## Setup Resend

### 1. Create Account
- Go to https://resend.com
- Free tier: 100 emails/day, 3,000/month

### 2. Get API Key
- Dashboard → API Keys
- Copy your API key (starts with `re_`)

### 3. Add Domain (Optional)
- Dashboard → Domains → Add Domain
- Verify DNS records
- Or use `onboarding@resend.dev` for testing

### 4. Update .env
```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=onboarding@resend.dev
```

### 5. Restart
```bash
docker-compose up --build
```

## Quick Start

### Local Development
```bash
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

## Email Flow

1. **Register** → Verification email sent via Resend
2. **Click link** → Email verified, welcome email sent
3. **Login** → Access app
4. **Forgot password** → Reset link sent via Resend
5. **Reset password** → Password updated

## Tech Stack
- **Frontend**: React 18, React Router, Axios
- **Backend**: Flask, Resend Python SDK
- **Email**: Resend (resend.com)
- **Database**: PostgreSQL
- **Deployment**: Railway, Docker Hub
