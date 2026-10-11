import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { getJson, type NewsItem, relativeTime } from "../api/client";
import CollectorStatus from "../components/CollectorStatus";

type Sort = "momentum" | "points" | "newest";

const SORTS: Record<Sort, { label: string; compare: (a: NewsItem, b: NewsItem) => number }> = {
  momentum: { label: "Points / hour", compare: (a, b) => b.points_per_hour - a.points_per_hour },
  points: { label: "Points", compare: (a, b) => b.points - a.points },
  newest: { label: "Newest", compare: (a, b) => b.posted_at.localeCompare(a.posted_at) },
};

const fmt = new Intl.NumberFormat();

function matches(item: NewsItem, query: string): boolean {
  if (!query) return true;
  const haystack = [item.title, item.domain ?? "", item.linked_repo ?? ""].join(" ").toLowerCase();
  return query
    .toLowerCase()
    .split(/\s+/)
    .every((word) => haystack.includes(word));
}

function StoryItem({ item, rank }: { item: NewsItem; rank: number }) {
  return (
    <li className="flex gap-3 py-3">
      <span className="w-6 shrink-0 pt-0.5 text-right text-sm text-stone-400 tabular-nums">{rank}</span>
      <div className="min-w-0 flex-1 space-y-1">
        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
          <a
            href={item.url ?? item.hn_url}
            target="_blank"
            rel="noreferrer"
            className="font-medium break-words hover:underline"
          >
            {item.title}
          </a>
          {item.domain && <span className="text-xs text-stone-400">{item.domain}</span>}
        </div>
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-stone-500">
          <span className="rounded bg-orange-50 px-1.5 py-0.5 font-medium text-orange-700 tabular-nums">
            {fmt.format(Math.round(item.points_per_hour))}/h
          </span>
          <span className="tabular-nums">{fmt.format(item.points)} points</span>
          <span>·</span>
          <a href={item.hn_url} target="_blank" rel="noreferrer" className="hover:underline">
            {fmt.format(item.comments)} comments
          </a>
          <span>·</span>
          <span title={new Date(item.posted_at).toLocaleString()}>{relativeTime(item.posted_at)}</span>
          {item.linked_repo && (
            <a
              href={`https://github.com/${item.linked_repo}`}
              target="_blank"
              rel="noreferrer"
              title="This story links a GitHub repo; it is now tracked on Rising repos"
              className="rounded bg-stone-100 px-1.5 py-0.5 font-medium text-stone-700 hover:bg-stone-200"
            >
              repo: {item.linked_repo}
            </a>
          )}
        </div>
      </div>
    </li>
  );
}

/** Hacker News stories from the last 7 days; search and sort (REQ-UI-003). */
export default function News() {
  const news = useQuery({
    queryKey: ["news"],
    queryFn: () => getJson<NewsItem[]>("/news"),
    refetchInterval: 60_000,
  });
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<Sort>("momentum");

  const shown = useMemo(
    () => (news.data ?? []).filter((n) => matches(n, query.trim())).sort(SORTS[sort].compare),
    [news.data, query, sort],
  );
  const linked = (news.data ?? []).filter((n) => n.linked_repo).length;

  return (
    <section className="space-y-5">
      <div className="space-y-3">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h1 className="text-2xl font-semibold">News</h1>
          {news.data && (
            <p className="text-sm text-stone-500">
              {news.data.length} stories from the last 7 days
              {linked > 0 && ` · ${linked} link a GitHub repo`}
            </p>
          )}
        </div>
        <div className="rounded-lg border border-stone-200 bg-white p-3">
          <CollectorStatus />
        </div>
      </div>

      <div className="flex flex-wrap gap-2 text-sm">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search title, site, repo…"
          aria-label="Search stories"
          className="min-w-0 flex-1 basis-56 rounded-md border border-stone-300 bg-white px-3 py-1.5"
        />
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as Sort)}
          aria-label="Sort by"
          className="rounded-md border border-stone-300 bg-white px-2 py-1.5"
        >
          {(Object.keys(SORTS) as Sort[]).map((s) => (
            <option key={s} value={s}>
              Sort: {SORTS[s].label}
            </option>
          ))}
        </select>
      </div>

      <p className="text-xs text-stone-500">
        All front-page and popular stories are shown; filtering to AI/dev topics comes with scoring.
      </p>

      {news.isPending && <p className="text-stone-500">Loading stories…</p>}
      {news.isError && <p className="text-red-600">Could not load stories: {news.error.message}</p>}
      {news.data && shown.length === 0 && (
        <p className="text-stone-500">
          {news.data.length === 0
            ? "No stories yet. The Hacker News collector runs about 90 seconds after the backend starts, then hourly."
            : "No stories match this search."}
        </p>
      )}
      {shown.length > 0 && (
        <ul className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white px-3">
          {shown.map((item, i) => (
            <StoryItem key={item.id} item={item} rank={i + 1} />
          ))}
        </ul>
      )}
    </section>
  );
}
