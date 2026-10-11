import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { type ItemType, postJson } from "../api/client";

/** 👍/👎 for one brief item (REQ-FBK-001). Clicking the selected one again clears it. */
export default function Rating({
  briefId,
  type,
  id,
  initial,
}: {
  briefId: number;
  type: ItemType;
  id: number;
  initial: number | null;
}) {
  const [rating, setRating] = useState<number | null>(initial);
  const queryClient = useQueryClient();
  const save = useMutation({
    mutationFn: (value: number) =>
      postJson<{ rating: number | null }>("/feedback", {
        brief_id: briefId,
        item_type: type,
        item_id: id,
        rating: value,
      }),
    onSuccess: (data) => {
      setRating(data.rating);
      void queryClient.invalidateQueries({ queryKey: ["today"] });
    },
  });

  const button = (value: 1 | -1, label: string, title: string) => {
    const active = rating === value;
    return (
      <button
        type="button"
        title={title}
        aria-label={title}
        aria-pressed={active}
        disabled={save.isPending}
        onClick={() => save.mutate(active ? 0 : value)}
        className={`rounded-md px-2 py-0.5 text-sm ring-1 transition ${
          active
            ? value === 1
              ? "bg-emerald-50 ring-emerald-300"
              : "bg-red-50 ring-red-300"
            : "ring-stone-200 hover:bg-stone-100"
        } disabled:opacity-60`}
      >
        {label}
      </button>
    );
  };

  return (
    <span className="inline-flex items-center gap-1.5">
      {button(1, "👍", "Useful")}
      {button(-1, "👎", "Not useful")}
      {save.isError && <span className="text-xs text-red-600">{save.error.message}</span>}
    </span>
  );
}
