import { Link } from "react-router";

import type { ItemType } from "../api/client";

/** Link to an item's card page; shows whether a card exists yet (spec 004). */
export default function CardLink({ type, id, hasCard }: { type: ItemType; id: number; hasCard: boolean }) {
  return (
    <Link
      to={`/cards/${type}/${id}`}
      title={hasCard ? "Read the card" : "No card yet: open to write one"}
      className={
        hasCard
          ? "rounded bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100"
          : "rounded px-1.5 py-0.5 text-xs text-stone-500 ring-1 ring-stone-200 hover:bg-stone-100"
      }
    >
      {hasCard ? "card" : "write card"}
    </Link>
  );
}
