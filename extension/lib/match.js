// Resume-fit scoring. This is how well a posting matches YOUR profile, not a hiring probability.
import { SKILL_VOCAB, DEFAULT_PROFILE } from "./profile.js";

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const wordRx = (body) => new RegExp(`(?:^|[^a-z0-9+#])(?:${body})(?=$|[^a-z0-9+#])`, "i");
const VOCAB_RX = Object.entries(SKILL_VOCAB).map(([name, alts]) => [name, wordRx(alts.join("|"))]);

export function skillsIn(text, extra = []) {
  const found = new Set();
  for (const [name, rx] of VOCAB_RX) if (rx.test(text)) found.add(name);
  for (const s of extra) {
    const k = s.toLowerCase().trim();
    if (k && !SKILL_VOCAB[k] && wordRx(esc(k)).test(text)) found.add(k);
  }
  return found;
}

const SENIOR = /\b(senior|sr\.?|lead|principal|manager|head of|director|architect|staff engineer|vp)\b/i;
const JUNIOR = /\b(intern(ship)?|fresher|freshers|graduate|grad|entry[- ]level|junior|jr\.?|trainee|apprentice|campus|0\s*-\s*[12]\s*(yrs|years)|2026|2027 batch|2027)\b/i;

function minYears(text) {
  let best = null;
  for (const m of text.matchAll(/(\d{1,2})\s*(?:\+|-|to|–)?\s*(?:\d{1,2})?\s*\+?\s*(?:years?|yrs?)/gi)) {
    const n = Number(m[1]);
    if (n <= 20 && (best === null || n < best)) best = n;
  }
  return best;
}

export function scoreJob(job, profile = DEFAULT_PROFILE) {
  const title = (job.title || "").toLowerCase();
  const text = [job.title, (job.tags || []).join(", "), job.experience, job.desc].filter(Boolean).join("\n").toLowerCase();
  const mine = new Set(profile.skills.map((s) => s.toLowerCase()));

  // 1. Skills (45%)
  const wanted = skillsIn(text, profile.skills);
  const have = [...wanted].filter((s) => mine.has(s));
  const missing = [...wanted].filter((s) => !mine.has(s));

  // 2. Role (25%)
  let role = 0.1, roleHit = "";
  for (const r of profile.roles) {
    if (title.includes(r.toLowerCase())) { role = 1; roleHit = r; break; }
  }
  if (role < 1 && /\b(analyst|analytics|data|developer|engineer|backend|python|machine learning|ml|ai)\b/.test(title)) role = 0.5;
  // No recognisable tech skills: neutral if the title is in your field, zero if it isn't.
  const coverage = wanted.size ? have.length / wanted.size : role >= 0.5 ? 0.4 : 0;

  // 3. Level (20%) - you're a 2027 student, so seniority matters a lot
  const years = minYears(`${job.experience || ""} ${text.slice(0, 3000)}`);
  let level = 0.6, levelNote = "";
  if (SENIOR.test(title)) { level = 0; levelNote = "Senior role"; }
  else if (JUNIOR.test(`${title} ${job.experience || ""}`)) { level = 1; levelNote = "Fresher / intern friendly"; }
  else if (years !== null) {
    if (years <= 1) { level = 0.9; levelNote = `${years}+ yrs asked`; }
    else if (years === 2) { level = 0.4; levelNote = "2+ yrs asked"; }
    else { level = 0.05; levelNote = `${years}+ yrs asked`; }
  } else if (JUNIOR.test(text.slice(0, 2000))) { level = 0.9; levelNote = "Fresher / intern friendly"; }

  // 4. Location (10%)
  const loc = (job.location || "").toLowerCase();
  let place = 0.6;
  if (/remote|work from home|wfh|anywhere/.test(loc)) place = 1;
  else if (loc && profile.locations.some((l) => loc.includes(l.toLowerCase()))) place = 1;
  else if (loc) place = 0.3;

  let fit = Math.round(100 * (0.45 * coverage + 0.25 * role + 0.2 * level + 0.1 * place));
  if (level === 0 || level === 0.05) fit = Math.min(fit, 35); // can't out-skill a 5-years-experience filter
  fit = Math.max(3, Math.min(98, fit));

  const reasons = [];
  if (wanted.size) reasons.push(`${have.length}/${wanted.size} skills match`);
  if (roleHit) reasons.push(`Role: ${roleHit}`);
  if (levelNote) reasons.push(levelNote);
  if (place === 1 && loc) reasons.push(job.location);

  return { fit, have: have.slice(0, 12), missing: missing.slice(0, 8), reasons };
}

// Pull a deadline out of free text, e.g. Internshala's "Apply By 5 Dec' 26".
export function findDeadline(text = "") {
  const m = text.match(/(?:apply\s*by|last\s*date(?:\s*to\s*apply)?|deadline|applications?\s*close[sd]?(?:\s*on)?)\s*[:\-]?\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})[,'’\s]*(\d{2,4})?/i);
  if (!m) return null;
  const months = "jan feb mar apr may jun jul aug sep oct nov dec".split(" ");
  const mi = months.indexOf(m[2].slice(0, 3).toLowerCase());
  if (mi < 0) return null;
  let y = m[3] ? Number(m[3]) : new Date().getFullYear();
  if (y < 100) y += 2000;
  const d = new Date(y, mi, Number(m[1]), 23, 59);
  if (!m[3] && d < Date.now() - 864e5 * 30) d.setFullYear(y + 1);
  return isNaN(d) ? null : d.toISOString();
}

export function daysLeft(iso) {
  if (!iso) return null;
  const end = new Date(iso);
  end.setHours(23, 59, 59, 999);
  return Math.floor((end - Date.now()) / 864e5);
}
