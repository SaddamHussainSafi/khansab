# Khan Sa'b Halal Food — 30-Day Instagram Campaign

Automated daily Instagram posting via GitHub Actions + Instagram Graph API.

- **Posters:** `poster-01.jpg` … `poster-30.jpg` (1080×1350, JPEG)
- **Schedule:** 1 post/day, 09:00 America/Toronto, 2026-07-27 → 2026-08-25
- **Pipeline:** `pipeline/publish.py`, config in `pipeline/config.json`
- **Duplicate guard:** `pipeline/posted.log` (tracked in git)
- **Workflow:** `.github/workflows/daily-post.yml` (cron 13:00 UTC + 3 retry slots)

## Manual run
Actions → *Daily Instagram post* → **Run workflow**
- `poster`: force a specific number (blank = today's)
- `dry`: `true` to build the media container without publishing

## Setup checklist
- [ ] Repo is **public** (required — Instagram must fetch the raw image URL)
- [ ] `ig_user_id` filled in `pipeline/config.json`
- [ ] Repo secret `IG_TOKEN` set (Settings → Secrets and variables → Actions)
- [ ] Token is a 60-day long-lived token; note the expiry
