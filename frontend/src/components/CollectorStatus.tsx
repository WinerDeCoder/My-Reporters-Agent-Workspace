import { useQuery } from "@tanstack/react-query";

import { type CollectorStatus as Status, getJson, type LlmUsage, relativeTime } from "../api/client";

const JOBS: Record<string, { label: string; unit: string }> = {
  github_trending: { label: "GitHub Trending", unit: "repos" },
  github_api: { label: "GitHub star snapshots", unit: "repos" },
  hacker_news: { label: "Hacker News", unit: "stories" },
  cards: { label: "Cards (LLM)", unit: "new cards" },
  brief: { label: "Daily brief", unit: "items" },
  prune: { label: "Weekly cleanup", unit: "rows deleted" },
};

const compact = new Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 1 });

/** LLM tokens used this month vs the cap (Q-023). */
function LlmUsageLine() {
  const usage = useQuery({
    queryKey: ["llm-usage"],
    queryFn: () => getJson<LlmUsage>("/llm/usage"),
    refetchInterval: 60_000,
  });
  if (!usage.data) return null;
  const u = usage.data;
  const pct = u.cap > 0 ? Math.min(100, (u.tokens / u.cap) * 100) : 100;
  const bar = pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <li className="flex flex-wrap items-center gap-x-2 gap-y-1 pt-1 text-sm">
      <span className="font-medium">LLM tokens this month</span>
      <span className="text-stone-500 tabular-nums">
        {compact.format(u.tokens)} of {compact.format(u.cap)} · {u.calls} calls
        {u.estimated_usd !== null && ` · ≈ $${u.estimated_usd.toFixed(2)}`}
      </span>
      <span className="h-1.5 w-24 overflow-hidden rounded bg-stone-200" aria-hidden>
        <span className={`block h-full ${bar}`} style={{ width: `${pct}%` }} />
      </span>
    </li>
  );
}

function Dot({ tone }: { tone: "ok" | "fail" | "idle" }) {
  const color = { ok: "bg-emerald-500", fail: "bg-red-500", idle: "bg-stone-300" }[tone];
  return <span className={`inline-block size-2 shrink-0 rounded-full ${color}`} aria-hidden />;
}

/** Last run / next run per background job (REQ-UI-002). */
export default function CollectorStatus() {
  const { data, isPending, isError, error } = useQuery({
    queryKey: ["collectors"],
    queryFn: () => getJson<Status[]>("/collectors/status"),
    refetchInterval: 60_000,
  });

  if (isPending) return <p className="text-sm text-stone-500">Loading collector status…</p>;
  if (isError) return <p className="text-sm text-red-600">Collector status unavailable: {error.message}</p>;

  return (
    <ul className="space-y-1.5 text-sm">
      {data.map((s) => {
        const run = s.last_run;
        const tone = !run ? "idle" : run.ok ? "ok" : "fail";
        return (
          <li key={s.job} className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
            <Dot tone={tone} />
            <span className="font-medium">{JOBS[s.job]?.label ?? s.job}</span>
            <span className="text-stone-500">
              {!run && "not run yet"}
              {run && (
                <span title={new Date(run.finished_at).toLocaleString()}>
                  {run.ok ? "ran" : "failed"} {relativeTime(run.finished_at)}
                  {run.ok && run.result !== null && ` · ${run.result} ${JOBS[s.job]?.unit ?? "items"}`}
                </span>
              )}
              {s.next_run && (
                <span title={new Date(s.next_run).toLocaleString()}> · next {relativeTime(s.next_run)}</span>
              )}
            </span>
            {run && !run.ok && run.error && (
              <span className="basis-full pl-4 text-xs break-words text-red-600">{run.error}</span>
            )}
          </li>
        );
      })}
      <LlmUsageLine />
    </ul>
  );
}
