import { useQuery } from "@tanstack/react-query";

import { type CollectorStatus as Status, getJson, relativeTime } from "../api/client";

const JOB_LABELS: Record<string, string> = {
  github_trending: "GitHub Trending",
  github_api: "GitHub star snapshots",
};

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
            <span className="font-medium">{JOB_LABELS[s.job] ?? s.job}</span>
            <span className="text-stone-500">
              {!run && "not run yet"}
              {run && (
                <span title={new Date(run.finished_at).toLocaleString()}>
                  {run.ok ? "ran" : "failed"} {relativeTime(run.finished_at)}
                  {run.ok && run.result !== null && ` · ${run.result} repos`}
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
    </ul>
  );
}
