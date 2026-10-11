// Thin fetch helper. Types mirror the backend's Pydantic models (see /docs);
// `npm run gen:api` (backend running) can generate them from OpenAPI instead.

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`);
  return res.json() as Promise<T>;
}

export type Health = { status: string; db: boolean };

export type RepoRow = {
  id: number;
  full_name: string;
  url: string;
  description: string | null;
  language: string | null;
  topics: string[];
  license: string | null;
  stars: number | null;
  /** null until the repo has 6 h of snapshot history */
  stars_per_day: number | null;
  snapshots: number;
  first_seen: string;
  last_seen: string;
};

export type NewsItem = {
  id: number;
  hn_id: number;
  title: string;
  /** null for Ask HN / text posts */
  url: string | null;
  domain: string | null;
  hn_url: string;
  points: number;
  comments: number;
  posted_at: string;
  points_per_hour: number;
  /** owner/repo when the story links a GitHub repo */
  linked_repo: string | null;
};

export type LastRun = {
  started_at: string;
  finished_at: string;
  ok: boolean;
  result: number | null;
  error: string | null;
};

export type CollectorStatus = {
  job: string;
  last_run: LastRun | null;
  next_run: string | null;
};

/** "just now", "12 min ago", "3 h ago", "2 d ago" — or "in 5 h" for future times. */
export function relativeTime(iso: string, now: number = Date.now()): string {
  const diff = (new Date(iso).getTime() - now) / 1000;
  const abs = Math.abs(diff);
  const [value, unit] =
    abs < 60
      ? [0, ""]
      : abs < 3600
        ? [Math.round(abs / 60), "min"]
        : abs < 86400
          ? [Math.round(abs / 3600), "h"]
          : [Math.round(abs / 86400), "d"];
  if (!unit) return diff >= 0 ? "in under a minute" : "just now";
  return diff >= 0 ? `in ${value} ${unit}` : `${value} ${unit} ago`;
}
