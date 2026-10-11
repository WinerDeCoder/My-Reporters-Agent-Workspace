import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { getJson, relativeTime, type RepoRow } from "../api/client";
import CollectorStatus from "../components/CollectorStatus";
import TopicBadges from "../components/TopicBadges";

type Sort = "forYou" | "momentum" | "stars" | "newest";

const SORTS: Record<Sort, { label: string; compare: (a: RepoRow, b: RepoRow) => number }> = {
  forYou: {
    label: "For you",
    // score = stars/day × your-topic boost (spec 003); unscored repos last, by topics then stars
    compare: (a, b) =>
      Number(a.score === null) - Number(b.score === null) ||
      (b.score ?? 0) - (a.score ?? 0) ||
      b.matched_topics.length - a.matched_topics.length ||
      (b.stars ?? 0) - (a.stars ?? 0),
  },
  momentum: {
    label: "Stars / day",
    // repos still collecting history go last, then by total stars
    compare: (a, b) =>
      Number(a.stars_per_day === null) - Number(b.stars_per_day === null) ||
      (b.stars_per_day ?? 0) - (a.stars_per_day ?? 0) ||
      (b.stars ?? 0) - (a.stars ?? 0),
  },
  stars: { label: "Total stars", compare: (a, b) => (b.stars ?? 0) - (a.stars ?? 0) },
  newest: { label: "Newest first seen", compare: (a, b) => b.first_seen.localeCompare(a.first_seen) },
};

const fmt = new Intl.NumberFormat();

function matches(repo: RepoRow, query: string): boolean {
  if (!query) return true;
  const haystack = [repo.full_name, repo.description ?? "", ...repo.topics, ...repo.matched_topics]
    .join(" ")
    .toLowerCase();
  return query
    .toLowerCase()
    .split(/\s+/)
    .every((word) => haystack.includes(word));
}

function Momentum({ value }: { value: number | null }) {
  if (value === null) {
    return (
      <span className="text-xs text-stone-400" title="Needs at least 6 hours of star snapshots">
        collecting…
      </span>
    );
  }
  const tone = value > 0 ? "text-emerald-700 bg-emerald-50" : "text-stone-500 bg-stone-100";
  return (
    <span className={`rounded px-1.5 py-0.5 text-xs font-medium tabular-nums ${tone}`}>
      {value > 0 ? "+" : ""}
      {fmt.format(Math.round(value))}/day
    </span>
  );
}

function RepoItem({ repo, rank }: { repo: RepoRow; rank: number }) {
  const [owner, name] = repo.full_name.split("/");
  return (
    <li className="flex gap-3 py-3">
      <span className="w-6 shrink-0 pt-0.5 text-right text-sm text-stone-400 tabular-nums">{rank}</span>
      <div className="min-w-0 flex-1 space-y-1">
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <a
            href={repo.url}
            target="_blank"
            rel="noreferrer"
            className="font-medium break-all hover:underline"
          >
            <span className="text-stone-500">{owner}/</span>
            {name}
          </a>
          <Momentum value={repo.stars_per_day} />
          <TopicBadges topics={repo.matched_topics} />
          <span className="text-xs text-stone-500 tabular-nums">
            ★ {repo.stars === null ? "—" : fmt.format(repo.stars)}
          </span>
        </div>
        {repo.description && <p className="line-clamp-2 text-sm text-stone-600">{repo.description}</p>}
        <div className="flex flex-wrap items-center gap-1.5 text-xs text-stone-500">
          {repo.language && <span className="font-medium text-stone-600">{repo.language}</span>}
          {repo.topics.slice(0, 5).map((t) => (
            <span key={t} className="rounded bg-stone-100 px-1.5 py-0.5">
              {t}
            </span>
          ))}
          <span title={new Date(repo.first_seen).toLocaleString()}>
            {(repo.language || repo.topics.length > 0) && "· "}first seen {relativeTime(repo.first_seen)}
          </span>
        </div>
      </div>
    </li>
  );
}

/** Every tracked repo with momentum; search, language filter, sort (REQ-UI-001). */
export default function Repos() {
  const repos = useQuery({
    queryKey: ["repos"],
    queryFn: () => getJson<RepoRow[]>("/repos"),
    refetchInterval: 60_000,
  });
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");
  const [sort, setSort] = useState<Sort>("forYou");

  const languages = useMemo(
    () => [...new Set((repos.data ?? []).map((r) => r.language).filter((l): l is string => !!l))].sort(),
    [repos.data],
  );
  const shown = useMemo(
    () =>
      (repos.data ?? [])
        .filter((r) => (!language || r.language === language) && matches(r, query.trim()))
        .sort(SORTS[sort].compare),
    [repos.data, language, query, sort],
  );
  const collecting = (repos.data ?? []).filter((r) => r.stars_per_day === null).length;

  return (
    <section className="space-y-5">
      <div className="space-y-3">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h1 className="text-2xl font-semibold">Rising repos</h1>
          {repos.data && (
            <p className="text-sm text-stone-500">
              {repos.data.length} tracked
              {collecting > 0 && ` · ${collecting} still collecting history`}
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
          placeholder="Search name, description, topic…"
          aria-label="Search repos"
          className="min-w-0 flex-1 basis-56 rounded-md border border-stone-300 bg-white px-3 py-1.5"
        />
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          aria-label="Language"
          className="rounded-md border border-stone-300 bg-white px-2 py-1.5"
        >
          <option value="">All languages</option>
          {languages.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
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

      {repos.isPending && <p className="text-stone-500">Loading repos…</p>}
      {repos.isError && <p className="text-red-600">Could not load repos: {repos.error.message}</p>}
      {repos.data && shown.length === 0 && (
        <p className="text-stone-500">
          {repos.data.length === 0
            ? "No repos tracked yet. The Trending collector runs daily at 07:10, or shortly after the backend starts if it hasn't run in the last 20 hours."
            : "No repos match these filters."}
        </p>
      )}
      {shown.length > 0 && (
        <ul className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white px-3">
          {shown.map((repo, i) => (
            <RepoItem key={repo.id} repo={repo} rank={i + 1} />
          ))}
        </ul>
      )}
    </section>
  );
}
