import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getJson, type LeaderboardLatest, postJson } from "../api/client";
import CardLink from "../components/CardLink";
import TopicBadges from "../components/TopicBadges";

const fmt = new Intl.NumberFormat();

function shortDate(iso: string): string {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
}

/** Weekly leaderboard (spec 006): top repos by stars gained over 7 days (Q-026). */
export default function Leaderboard() {
  const queryClient = useQueryClient();
  const latest = useQuery({
    queryKey: ["leaderboard"],
    queryFn: () => getJson<LeaderboardLatest>("/leaderboard/latest"),
  });
  const build = useMutation({
    mutationFn: () => postJson<LeaderboardLatest>("/leaderboard/build"),
    onSuccess: (data) => queryClient.setQueryData(["leaderboard"], data),
  });

  if (latest.isPending) return <p className="text-stone-500">Loading…</p>;
  if (latest.isError) return <p className="text-red-600">Could not load the leaderboard: {latest.error.message}</p>;

  const lb = latest.data.leaderboard;
  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-2xl font-semibold">Weekly leaderboard</h1>
        {lb && <p className="text-sm text-stone-500">Week of {shortDate(lb.week_of)} · stars gained over 7 days</p>}
      </div>

      {!lb && (
        <div className="space-y-3 rounded-lg border border-dashed border-stone-300 p-5">
          <p className="text-stone-600">
            No leaderboard yet. It's built every Monday at {latest.data.run_at} from the week's star snapshots.
          </p>
          <button
            type="button"
            onClick={() => build.mutate()}
            disabled={build.isPending}
            className="rounded-md bg-stone-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-stone-700 disabled:opacity-60"
          >
            {build.isPending ? "Building…" : "Build this week's now"}
          </button>
          {build.isError && <p className="text-sm text-red-600">{build.error.message}</p>}
        </div>
      )}

      {lb && lb.entries.length === 0 && <p className="text-stone-500">Not enough snapshots yet for this week.</p>}
      {lb && lb.entries.length > 0 && (
        <ol className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white px-4">
          {lb.entries.map((e) => (
            <li key={e.item_id} className="flex gap-4 py-3">
              <span className="w-6 shrink-0 pt-0.5 text-right text-lg font-semibold text-stone-400 tabular-nums">
                {e.rank}
              </span>
              <div className="min-w-0 flex-1 space-y-1">
                <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                  <a href={e.url ?? "#"} target="_blank" rel="noreferrer" className="font-semibold break-all hover:underline">
                    {e.title}
                  </a>
                  <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700 tabular-nums">
                    +{fmt.format(e.stars_gained)} this week
                  </span>
                  <TopicBadges topics={e.matched_topics} />
                </div>
                {(e.what_it_is ?? e.description) && (
                  <p className="text-sm text-stone-700">{e.what_it_is ?? e.description}</p>
                )}
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-stone-500">
                  <span className="tabular-nums">★ {fmt.format(e.stars)} total</span>
                  {e.language && <span>{e.language}</span>}
                  {e.since && <span title="Tracked for less than 7 days">since {shortDate(e.since)}</span>}
                  <CardLink type="repo" id={e.item_id} hasCard={e.has_card} />
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
