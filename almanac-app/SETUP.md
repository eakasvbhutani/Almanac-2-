# Setting up Almanac

This app needs three free accounts before it'll run. None of these need a
credit card for the scale of a ~10-person hobby project.

## 1. Supabase (auth + database + file storage)

1. Go to [supabase.com](https://supabase.com), sign up, and create a new project (free tier).
2. In the project dashboard, go to **Settings → API** and copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Go to **SQL Editor**, paste the contents of [`supabase/schema.sql`](supabase/schema.sql), and run it. This creates all the tables, the row-level security policies that keep each person's data private, and the `timetables` storage bucket for uploaded files.

That's it for Supabase — email/password sign-up works immediately, no extra config.

## 2. Anthropic API key (parses uploaded timetables)

1. Go to [console.anthropic.com](https://console.anthropic.com) and create an API key.
2. Put it in `ANTHROPIC_API_KEY`.
3. This is pay-per-use, but for ~10 friends occasionally uploading a timetable image, cost is negligible (a few cents per parse).

## 3. (Optional) GitHub OAuth — "Continue with GitHub" button

Skip this if email/password is enough for your friend group — it already works with zero setup.

1. Go to **GitHub → Settings → Developer settings → OAuth Apps → New OAuth App**.
2. Homepage URL: your Vercel URL (or `http://localhost:3000` while developing).
3. Authorization callback URL: `https://<your-project>.supabase.co/auth/v1/callback`
4. Copy the Client ID and generate a Client Secret.
5. In Supabase: **Authentication → Providers → GitHub**, paste them in, and enable it.

No code changes needed — the button in the app is already wired up.

## 4. Environment variables

```bash
cp .env.local.example .env.local
# then fill in the values above
```

## 5. Run it

```bash
npm install
npm run dev
```

Open http://localhost:3000 — you'll land on `/login` since no one's signed in yet.

## Deploying (GitHub + Vercel)

1. Push this repo to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new), import the repo.
3. Add the same environment variables from `.env.local` in the Vercel project settings (Settings → Environment Variables). Set `NEXT_PUBLIC_SITE_URL` to your real Vercel URL (e.g. `https://almanac-yourname.vercel.app`).
4. Deploy. Free tier comfortably covers 10 users.

If you enabled GitHub OAuth, update its callback URL registration if your Supabase project URL changes — it doesn't need to know about Vercel at all, only Supabase's own callback URL.
