import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router";

import { type CardView, getJson, type ItemType, postJson, relativeTime } from "../api/client";
import TopicBadges from "../components/TopicBadges";

const fmt = new Intl.NumberFormat();

const FIELDS: { key: "what_it_is" | "problem_it_solves" | "whats_special" | "worth_trying"; label: string }[] = [
  { key: "what_it_is", label: "What it is" },
  { key: "problem_it_solves", label: "Problem it solves" },
  { key: "whats_special", label: "What's special" },
  { key: "worth_trying", label: "Worth trying?" },
];

const SOURCE_LABEL = { readme: "README", article: "article text", title: "title only" } as const;

function Signals({ view }: { view: CardView }) {
  const it = view.item;
  const parts: string[] = [];
  if (it.stars !== null) parts.push(`★ ${fmt.format(it.stars)}`);
  if (it.stars_per_day !== null) parts.push(`+${fmt.format(Math.round(it.stars_per_day))}/day`);
  if (it.points !== null) parts.push(`${fmt.format(it.points)} points`);
  if (it.comments !== null) parts.push(`${fmt.format(it.comments)} comments`);
  if (it.points_per_hour !== null) parts.push(`${fmt.format(Math.round(it.points_per_hour))}/h`);
  if (it.language) parts.push(it.language);
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-stone-600">
      {parts.map((p) => (
        <span key={p} className="tabular-nums">
          {p}
        </span>
      ))}
      <TopicBadges topics={it.matched_topics} />
    </div>
  );
}

/** One item's card (spec 004): model-written fields + live signals; "Write card" if none yet. */
export default function Card() {
  const { itemType = "repo", itemId = "0" } = useParams();
  const type = (itemType === "news" ? "news" : "repo") as ItemType;
  const path = `/cards/${type}/${itemId}`;
  const queryClient = useQueryClient();

  const view = useQuery({ queryKey: ["card", type, itemId], queryFn: () => getJson<CardView>(path) });
  const write = useMutation({
    mutationFn: () => postJson<CardView>(path),
    onSuccess: (data) => {
      queryClient.setQueryData(["card", type, itemId], data);
      void queryClient.invalidateQueries({ queryKey: [type === "repo" ? "repos" : "news"] });
      void queryClient.invalidateQueries({ queryKey: ["llm-usage"] });
    },
  });

  if (view.isPending) return <p className="text-stone-500">Loading…</p>;
  if (view.isError) return <p className="text-red-600">Could not load this item: {view.error.message}</p>;

  const { item, card } = view.data;
  const links = [
    item.url && { href: item.url, label: type === "repo" ? "GitHub" : "Article" },
    item.hn_url && { href: item.hn_url, label: "HN discussion" },
    item.linked_repo && { href: `https://github.com/${item.linked_repo}`, label: item.linked_repo },
  ].filter(Boolean) as { href: string; label: string }[];

  return (
    <article className="space-y-6">
      <header className="space-y-2">
        <p className="text-xs font-medium tracking-wide text-stone-500 uppercase">
          {type === "repo" ? "Repository" : "News story"}
        </p>
        <h1 className="text-2xl font-semibold break-words">{item.title}</h1>
        {item.description && <p className="text-stone-600">{item.description}</p>}
        <Signals view={view.data} />
        {links.length > 0 && (
          <p className="flex flex-wrap gap-3 text-sm">
            {links.map((l) => (
              <a key={l.href} href={l.href} target="_blank" rel="noreferrer" className="underline underline-offset-2">
                {l.label} ↗
              </a>
            ))}
          </p>
        )}
      </header>

      {card ? (
        <section className="space-y-4 rounded-lg border border-stone-200 bg-white p-5">
          {card.limited && (
            <p className="rounded bg-amber-50 px-3 py-2 text-sm text-amber-800">
              Limited source: the page couldn't be read, so this card is based on the title only.
            </p>
          )}
          <dl className="space-y-4">
            {FIELDS.map((f) => (
              <div key={f.key}>
                <dt className="text-sm font-semibold text-stone-900">{f.label}</dt>
                <dd className="mt-0.5 text-stone-700">{card[f.key]}</dd>
              </div>
            ))}
          </dl>
          <p className="border-t border-stone-100 pt-3 text-xs text-stone-500">
            Written by {card.model} from the {SOURCE_LABEL[card.source_kind]}{" "}
            <span title={new Date(card.created_at).toLocaleString()}>{relativeTime(card.created_at)}</span>.
            It's rewritten only when the source changes.
          </p>
        </section>
      ) : (
        <section className="space-y-3 rounded-lg border border-dashed border-stone-300 p-5">
          <p className="text-stone-600">No card yet for this {type === "repo" ? "repository" : "story"}.</p>
          <button
            type="button"
            onClick={() => write.mutate()}
            disabled={write.isPending}
            className="rounded-md bg-stone-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-stone-700 disabled:opacity-60"
          >
            {write.isPending ? "Writing… (about 10 s)" : "Write card"}
          </button>
          {write.isError && <p className="text-sm text-red-600">{write.error.message}</p>}
          <p className="text-xs text-stone-500">Uses one LLM call; counts toward the monthly token cap.</p>
        </section>
      )}
    </article>
  );
}
