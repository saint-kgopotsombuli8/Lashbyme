# Lashed by Me

Flask booking site + admin dashboard for a lash studio.

## Project structure
```
lashed-by-me/
├── app.py            # Flask app factory
├── models.py          # Booking & CalendarEvent models
├── routes.py           # Public + admin routes
├── requirements.txt
├── vercel.json
├── templates/          # home.html, login.html, dashboard.html, orders.html, calendar.html
└── static/
    ├── css/
    └── img/            # add your logo + kit photos here (see below)
```

## Before you deploy

### 1. Set a real database — required
By default this app falls back to SQLite in `/tmp`, which Vercel wipes on
every cold start. **On Vercel this means bookings can disappear.**

Set a `DATABASE_URL` environment variable in your Vercel project settings
to a hosted Postgres database. Free options: [Neon](https://neon.tech),
[Supabase](https://supabase.com), or Vercel's own Postgres add-on. The app
already handles the `postgres://` → `postgresql://` fix, so no code changes
are needed — just add the env var.

### 2. Set a real secret key
Set a `SECRET_KEY` environment variable in Vercel (any long random string).
The code currently falls back to a hardcoded key if this isn't set.

### 3. Move the admin login out of source code
`routes.py` currently has the admin email/password hardcoded
(`owethu@gmail.com` / `admin123`). Anyone who can read the repo can log in.
Before sharing this repo or making it public, move these into environment
variables and check them from there instead.

### 4. Add your images
`static/img/` is currently empty. The homepage expects:
- `Logo.png`
- `Beginner_Kit.jpg`
- `Intermediate_Kit.jpg`
- `Professional_Kit.jpg`
- `Lash_artist.jpeg`

Drop them into `static/img/` with those exact filenames (case-sensitive).

## Deploying to Vercel
1. Push this folder to a GitHub repo.
2. Import the repo in Vercel.
3. Add the `DATABASE_URL` and `SECRET_KEY` environment variables under
   Project Settings → Environment Variables.
4. Deploy.

## Local development
```bash
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000`.
# Lashbyme
