import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { type CheckState, getJson, type Stats as StatsData } from "../api/client";

const STATE_STYLE: Record<CheckState, string> = {
  pass: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  "on track": "bg-emerald-50 text-emerald-800 ring-emerald-200",
  "not yet": "bg-stone-50 text-stone-700 ring-stone-200",
  "no data": "bg-stone-50 text-stone-500 ring-stone-200",
  below: "bg-amber-50 text-amber-800 ring-amber-200",
  fail: "bg-red-50 text-red-800 ring-red-200",
};

const pct = (v: number | null) => (v === null ? "—" : `${Math.round(v * 100)}%`);

function shortDate(iso: string): string {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
}

function Checks({ s }: { s: StatsData }) {
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {Object.entries(s.checks).map(([key, c]) => (
        <div key={key} className={`rounded-lg p-4 ring-1 ${STATE_STYLE[c.state]}`}>
          <p className="text-xs font-medium">{c.label}</p>
          <p className="mt-1 text-2xl font-semibold tabular-nums">
            {key === "opened_days" ? `${c.value ?? 0} / ${s.days}` : pct(c.value)}
          </p>
          <p className="mt-0.5 text-xs font-semibold tracking-wide uppercase">{c.state}</p>
        </div>
      ))}
    </div>
  );
}

function DayTable({ s }: { s: StatsData }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-stone-200 bg-white">
      <table className="w-full text-sm">
        <thead className="bg-stone-50 text-left text-xs text-stone-500">
          <tr>
            <th className="px-3 py-2 font-medium">Day</th>
            <th className="px-3 py-2 font-medium">Brief</th>
            <th className="px-3 py-2 font-medium">Opened</th>
            <th className="px-3 py-2 text-right font-medium">Items</th>
            <th className="px-3 py-2 text-right font-medium">Rated</th>
            <th className="px-3 py-2 text-right font-medium">👍</th>
            <th className="px-3 py-2 text-right font-medium">👎</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {s.rows.map((r) => {
            const future = r.day > s.today;
            return (
              <tr key={r.day} className={future ? "text-stone-300" : ""}>
                <td className="px-3 py-1.5 whitespace-nowrap">{shortDate(r.day)}</td>
                <td className="px-3 py-1.5">{future ? "" : r.built ? "built" : "—"}</td>
                <td className="px-3 py-1.5 whitespace-nowrap">
                  {r.opened_at ? new Date(r.opened_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : future ? "" : "—"}
                </td>
                <td className="px-3 py-1.5 text-right tabular-nums">{future ? "" : r.items}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">{future ? "" : r.rated}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">{future ? "" : r.up}</td>
                <td className="px-3 py-1.5 text-right tabular-nums">{future ? "" : r.down}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/** Stats for the 2-week trial (spec 007, Q-028, Q-029). */
export default function Stats() {
  const [view, setView] = useState<"trial" | "rolling">("trial");
  const stats = useQuery({
    queryKey: ["stats", view],
    queryFn: () => getJson<StatsData>(`/stats?view=${view}`),
    refetchInterval: 60_000,
  });

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-2xl font-semibold">Stats</h1>
        <div className="flex rounded-md ring-1 ring-stone-300" role="tablist">
          {(["trial", "rolling"] as const).map((v) => (
            <button
              key={v}
              type="button"
              role="tab"
              aria-selected={view === v}
              onClick={() => setView(v)}
              className={`px-3 py-1 text-sm ${view === v ? "bg-stone-900 text-white" : "text-stone-600 hover:bg-stone-100"} first:rounded-l-md last:rounded-r-md`}
            >
              {v === "trial" ? "2-week trial" : "Last 14 days"}
            </button>
          ))}
        </div>
      </div>

      {stats.isPending && <p className="text-stone-500">Loading…</p>}
      {stats.isError && <p className="text-red-600">Could not load stats: {stats.error.message}</p>}
      {stats.data && (
        <>
          <p className="text-sm text-stone-600">
            {view === "trial"
              ? stats.data.not_started
                ? `The trial starts ${shortDate(stats.data.start)} and runs ${stats.data.days} days.`
                : stats.data.finished
                  ? `Trial finished (${shortDate(stats.data.start)} – ${shortDate(stats.data.end)}).`
                  : `Day ${stats.data.day_number} of ${stats.data.days} (${shortDate(stats.data.start)} – ${shortDate(stats.data.end)}).`
              : `${shortDate(stats.data.start)} – ${shortDate(stats.data.end)}.`}{" "}
            {stats.data.briefs_built} briefs built · {stats.data.rated} of {stats.data.items} items rated ·{" "}
            {stats.data.up} 👍 / {stats.data.down} 👎
          </p>

          {stats.data.verdict && (
            <p
              className={`rounded-lg p-4 text-base font-medium ${
                stats.data.verdict === "continue" ? "bg-emerald-50 text-emerald-900" : "bg-amber-50 text-amber-900"
              }`}
            >
              {stats.data.verdict === "continue"
                ? "Verdict: it works. The v1 requirements become the roadmap."
                : "Verdict: fix scoring and cards before building anything else."}
            </p>
          )}

          <Checks s={stats.data} />
          <DayTable s={stats.data} />
          <p className="text-xs text-stone-500">
            Thresholds and the trial dates live in <code>config.yaml</code> → <code>trial</code>.
          </p>
        </>
      )}
    </section>
  );
}
