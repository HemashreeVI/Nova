# Nova Launchpad

Your personal Chrome new tab for the job hunt:

- **Left:** F1 standings and the next race with a live countdown.
- **Right:** **Job Radar** (jobs scored against your resume) and **LeetCode**: today's daily problem, a countdown to the reset and your streak.
- **Bottom:** a ticker of hot tech news.

## Install (2 minutes)

1. Download this repo: **Code → Download ZIP** on GitHub, then unzip it.
2. Open `chrome://extensions` and turn on **Developer mode** (top right).
3. Click **Load unpacked** and pick the `extension` folder.
4. Chrome asks whether to keep the new new-tab page: choose **Keep it**.
   If you still have the old F1 new-tab extension, turn it off. Chrome only lets one extension own the new tab, and Nova already has F1 in it.
5. Pin Nova: puzzle icon → pin. The red number on the icon is the count of new strong job matches.
6. The settings drawer opens on first run. Fill in your **name** and **LeetCode username**, check the **job searches**, then click **Save**.
7. Click **Send a test notification**. If nothing appears, allow Chrome notifications in your OS settings (Windows: Settings → System → Notifications → Google Chrome).

Everything is stored only in your Chrome profile. Use **Settings → Export backup** now and then.

## What it does

| Feature | How |
|---|---|
| **Job Radar** | Gives each job a **fit %**, a deadline when the site lists one, and the skills you're missing. Click a row to open the job. ♡ saves it, ✓ marks it applied, ✕ hides it. |
| **Naukri / Internshala auto-scan** | Every 4 h (your choice) Nova opens your saved searches in a *minimized* window, reads the results and closes it, 3 searches per run. Only runs while Chrome is open. |
| **Every other job site** | Browse LinkedIn, Indeed, Unstop, Wellfound, Instahyre, foundit, Glassdoor or company career pages, and Nova reads the listings you see. A fit badge appears on job pages, showing the skills you have and the ones you're missing. |
| **Remote jobs** | Remotive's public API, checked on every scan. |
| **Job alerts** | A notification for new jobs at or above your fit threshold (default 70%). A reminder 2 days before a saved job's deadline. |
| **LeetCode reminders** | At 7:00 pm and 10:30 pm (editable), *only if you haven't solved anything yet that LeetCode day*. The daily resets at 05:30 IST. |
| **Tech news** | Google News for your topics (NVIDIA, GTA 6, OpenAI…) plus Hacker News, in the ticker. A notification every 4 h, quiet 11 pm–8 am. |
| **Your background** | Click the 🖼 button and pick any photo. |
| **Right-click → Save this job to Nova** | Works on any page. |

### About the fit %
It measures **how well a job matches your resume**:
- skills (45%)
- role (25%)
- seniority: a 2027 student vs. "5+ years" (20%)
- location (10%)

It is *not* the probability of being hired; nobody can calculate that. Use it to decide which jobs to apply to first. Your skills, roles and locations can be edited in **Settings → Profile**.

### If a site stops being read
Job sites change their page layouts sometimes. **Settings → Job searches** shows the last scan result for each search, for example "⚠ naukri · data analyst · 0 read". If one keeps reading 0, the card selectors in `content/jobs.js` need updating for the new layout. Pages that include standard `JobPosting` data keep working regardless.

## Files
```
manifest.json      extension config
background.js      reminders, scans, notifications
newtab.*           the new tab page
popup.*            toolbar popup
content/jobs.js    reads job pages and draws the fit badge
lib/profile.js     your resume skills (default profile)
lib/match.js       fit % scoring
lib/feeds.js       LeetCode, F1, weather, news, Remotive
```
