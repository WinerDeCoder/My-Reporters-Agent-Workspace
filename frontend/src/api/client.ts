// Thin fetch helper. Types mirror the backend's Pydantic models (see /docs);
// `npm run gen:api` (backend running) can generate them from OpenAPI instead.

async function errorMessage(res: Response, path: string): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // not JSON
  }
  return `${res.status} ${res.statusText} on ${path}`;
}

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`);
  if (!res.ok) throw new Error(await errorMessage(res, path));
  return res.json() as Promise<T>;
}

export async function postJson<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: "POST",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await errorMessage(res, path));
  return res.json() as Promise<T>;
}

export type BriefItem = {
  section: "top" | "repos" | "news";
  item_type: ItemType;
  item_id: number;
  title: string;
  url: string | null;
  hn_url: string | null;
  domain: string | null;
  description: string | null;
  language: string | null;
  stars: number | null;
  stars_per_day: number | null;
  points: number | null;
  comments: number | null;
  points_per_hour: number | null;
  linked_repo: string | null;
  matched_topics: string[];
  score: number | null;
  /** from the item's latest card */
  what_it_is: string | null;
  has_card: boolean;
  /** 1 = 👍, -1 = 👎, null = not rated */
  rating: number | null;
};

export type Brief = {
  id: number;
  date: string;
  created_at: string;
  opened_at: string | null;
  items: BriefItem[];
};

export type Today = { brief: Brief | null; brief_time: string };

export type ItemType = "repo" | "news";

export type CardItem = {
  item_type: ItemType;
  item_id: number;
  title: string;
  url: string | null;
  description: string | null;
  language: string | null;
  stars: number | null;
  stars_per_day: number | null;
  points: number | null;
  comments: number | null;
  points_per_hour: number | null;
  hn_url: string | null;
  linked_repo: string | null;
  matched_topics: string[];
  score: number | null;
};

export type CardContent = {
  what_it_is: string;
  problem_it_solves: string;
  whats_special: string;
  worth_trying: string;
  source_kind: "readme" | "article" | "title";
  source_url: string | null;
  limited: boolean;
  model: string;
  created_at: string;
};

export type CardView = { item: CardItem; card: CardContent | null };

export type LlmUsage = {
  month_start: string;
  calls: number;
  input_tokens: number;
  output_tokens: number;
  tokens: number;
  cap: number;
  estimated_usd: number | null;
};

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
  /** stars/day × topic boost × penalties; null until stars/day exists */
  score: number | null;
  matched_topics: string[];
  has_card: boolean;
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
  matched_topics: string[];
  /** AI/dev story, eligible for the brief */
  ai_dev: boolean;
  /** points/hour × topic boost × penalties; null when not AI/dev */
  score: number | null;
  has_card: boolean;
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
