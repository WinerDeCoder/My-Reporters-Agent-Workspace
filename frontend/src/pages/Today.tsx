import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router";

import { type BriefItem, getJson, type Health, postJson, type Today as TodayData } from "../api/client";
import CardLink from "../components/CardLink";
import CollectorStatus from "../components/CollectorStatus";
import Rating from "../components/Rating";
import TopicBadges from "../components/TopicBadges";

const fmt = new Intl.NumberFormat();

function signals(it: BriefItem): string {
  if (it.item_type === "repo") {
    const parts = [];
    if (it.stars_per_day !== null) parts.push(`+${fmt.format(Math.round(it.stars_per_day))} stars/day`);
    if (it.stars !== null) parts.push(`${fmt.format(it.stars)} total`);
    if (it.language) parts.push(it.language);
    return parts.join(" · ");
  }
  const parts = [];
  if (it.points !== null) parts.push(`${fmt.format(it.points)} points on HN`);
  if (it.comments !== null) parts.push(`${fmt.format(it.comments)} comments`);
  if (it.domain) parts.push(it.domain);
  return parts.join(" · ");
}

function Item({ it, briefId, big = false }: { it: BriefItem; briefId: number; big?: boolean }) {
  const summary = it.what_it_is ?? it.description;
  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <a
          href={it.url ?? it.hn_url ?? "#"}
          target="_blank"
          rel="noreferrer"
          className={`font-semibold break-words hover:underline ${big ? "text-xl" : ""}`}
        >
          {it.title}
        </a>
        <TopicBadges topics={it.matched_topics} />
      </div>
      {summary && <p className={`text-stone-700 ${big ? "text-base" : "text-sm"}`}>{summary}</p>}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-stone-500">
        <span className="tabular-nums">{signals(it)}</span>
        {it.hn_url && (
          <a href={it.hn_url} target="_blank" rel="noreferrer" className="hover:underline">
            discussion
          </a>
        )}
        <CardLink type={it.item_type} id={it.item_id} hasCard={it.has_card} />
        <Rating briefId={briefId} type={it.item_type} id={it.item_id} initial={it.rating} />
      </div>
    </div>
  );
}

function Section({ title, items, briefId }: { title: string; items: BriefItem[]; briefId: number }) {
  if (items.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="text-xs font-semibold tracking-wider text-stone-500 uppercase">{title}</h2>
      <ol className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white px-4">
        {items.map((it) => (
          <li key={`${it.item_type}-${it.item_id}`} className="py-3">
            <Item it={it} briefId={briefId} />
          </li>
        ))}
      </ol>
    </section>
  );
}

function BriefView({ data }: { data: TodayData }) {
  const brief = data.brief!;
  const top = brief.items.find((i) => i.section === "top");
  const repos = brief.items.filter((i) => i.section === "repos");
  const news = brief.items.filter((i) => i.section === "news");
  const day = new Date(`${brief.date}T00:00:00`);
  const isToday = brief.date === new Date().toLocaleDateString("en-CA");
  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-2xl font-semibold">
          Tech Radar · {day.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}
        </h1>
        {!isToday && (
          <p className="text-sm text-amber-700">Latest brief; today's is built at {data.brief_time}.</p>
        )}
      </header>
      {brief.items.length === 0 && (
        <p className="text-stone-500">Nothing scored high enough for this brief yet.</p>
      )}
      {top && (
        <section className="space-y-3">
          <h2 className="text-xs font-semibold tracking-wider text-stone-500 uppercase">Top story</h2>
          <div className="rounded-lg border border-stone-300 bg-white p-5 shadow-sm">
            <Item it={top} briefId={brief.id} big />
          </div>
        </section>
      )}
      <Section title="Rising repos" items={repos} briefId={brief.id} />
      <Section title="News" items={news} briefId={brief.id} />
    </div>
  );
}

/** The daily brief (spec 005): top story, rising repos, news, each rated 👍/👎. */
export default function Today() {
  const queryClient = useQueryClient();
  const today = useQuery({ queryKey: ["today"], queryFn: () => getJson<TodayData>("/briefs/today") });
  const health = useQuery({ queryKey: ["health"], queryFn: () => getJson<Health>("/health") });
  const build = useMutation({
    mutationFn: () => postJson<TodayData>("/briefs/today/build"),
    onSuccess: (data) => queryClient.setQueryData(["today"], data),
  });

  return (
    <div className="space-y-10">
      {today.isPending && <p className="text-stone-500">Loading today's brief…</p>}
      {today.isError && <p className="text-red-600">Could not load the brief: {today.error.message}</p>}
      {today.data?.brief && <BriefView data={today.data} />}
      {today.data && !today.data.brief && (
        <section className="space-y-3 rounded-lg border border-dashed border-stone-300 p-5">
          <h1 className="text-2xl font-semibold">Today</h1>
          <p className="text-stone-600">
            No brief yet. It's built every morning at {today.data.brief_time}, after the collectors and cards.
          </p>
          <button
            type="button"
            onClick={() => build.mutate()}
            disabled={build.isPending}
            className="rounded-md bg-stone-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-stone-700 disabled:opacity-60"
          >
            {build.isPending ? "Building… (cards may take a minute)" : "Build today's brief now"}
          </button>
          {build.isError && <p className="text-sm text-red-600">{build.error.message}</p>}
          <p className="text-sm text-stone-500">
            Meanwhile, browse <Link to="/repos" className="underline">Rising repos</Link> and{" "}
            <Link to="/news" className="underline">News</Link>.
          </p>
        </section>
      )}

      <section className="space-y-3 rounded-lg border border-stone-200 bg-white p-4 text-sm">
        <p className="font-medium">System status</p>
        {health.data && (
          <p className="text-stone-600">
            API {health.data.status} · Database {health.data.db ? "connected" : "not reachable"}
          </p>
        )}
        {health.isError && <p className="text-red-600">Backend unreachable: {health.error.message}</p>}
        <CollectorStatus />
      </section>
    </div>
  );
}
