import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { getJson, type NewsItem, relativeTime } from "../api/client";
import CardLink from "../components/CardLink";
import CollectorStatus from "../components/CollectorStatus";
import TopicBadges from "../components/TopicBadges";

type Sort = "forYou" | "momentum" | "points" | "newest";

const SORTS: Record<Sort, { label: string; compare: (a: NewsItem, b: NewsItem) => number }> = {
  forYou: {
    label: "For you",
    // score = points/hour × your-topic boost (spec 003); non-AI/dev stories have no score
    compare: (a, b) =>
      Number(a.score === null) - Number(b.score === null) ||
      (b.score ?? 0) - (a.score ?? 0) ||
      b.points_per_hour - a.points_per_hour,
  },
  momentum: { label: "Points / hour", compare: (a, b) => b.points_per_hour - a.points_per_hour },
  points: { label: "Points", compare: (a, b) => b.points - a.points },
  newest: { label: "Newest", compare: (a, b) => b.posted_at.localeCompare(a.posted_at) },
};

const fmt = new Intl.NumberFormat();

function matches(item: NewsItem, query: string): boolean {
  if (!query) return true;
  const haystack = [item.title, item.domain ?? "", item.linked_repo ?? "", ...item.matched_topics]
    .join(" ")
    .toLowerCase();
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
          <TopicBadges topics={item.matched_topics} />
          <CardLink type="news" id={item.id} hasCard={item.has_card} />
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
  const [sort, setSort] = useState<Sort>("forYou");
  const [aiDevOnly, setAiDevOnly] = useState(true);

  const shown = useMemo(
    () =>
      (news.data ?? [])
        .filter((n) => (!aiDevOnly || n.ai_dev) && matches(n, query.trim()))
        .sort(SORTS[sort].compare),
    [news.data, query, sort, aiDevOnly],
  );
  const linked = (news.data ?? []).filter((n) => n.linked_repo).length;
  const aiDevCount = (news.data ?? []).filter((n) => n.ai_dev).length;

  return (
    <section className="space-y-5">
      <div className="space-y-3">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h1 className="text-2xl font-semibold">News</h1>
          {news.data && (
            <p className="text-sm text-stone-500">
              {news.data.length} stories from the last 7 days · {aiDevCount} AI/dev
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
        <label className="flex items-center gap-1.5 rounded-md border border-stone-300 bg-white px-2 py-1.5">
          <input
            type="checkbox"
            checked={aiDevOnly}
            onChange={(e) => setAiDevOnly(e.target.checked)}
            aria-label="AI/dev only"
          />
          AI/dev only
        </label>
      </div>

      <p className="text-xs text-stone-500">
        "For you" ranks AI/dev stories by points/hour, boosted for your interest topics. Topics and the
        AI/dev word list live in <code>config.yaml</code> → <code>interests</code>.
      </p>

      {news.isPending && <p className="text-stone-500">Loading stories…</p>}
      {news.isError && <p className="text-red-600">Could not load stories: {news.error.message}</p>}
      {news.data && shown.length === 0 && (
        <p className="text-stone-500">
          {news.data.length === 0
            ? "No stories yet. The Hacker News collector runs daily at 07:00, or about a minute after the backend starts if it hasn't run in the last 20 hours."
            : "No stories match these filters."}
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
