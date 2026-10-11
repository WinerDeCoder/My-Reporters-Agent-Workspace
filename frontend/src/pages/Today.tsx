import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";

import { getJson, type Health } from "../api/client";
import CollectorStatus from "../components/CollectorStatus";

export default function Today() {
  const health = useQuery({ queryKey: ["health"], queryFn: () => getJson<Health>("/health") });

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Today</h1>

      <div className="space-y-3 rounded-lg border border-stone-200 bg-white p-4 text-sm">
        <p className="font-medium">System status</p>
        {health.isPending && <p className="text-stone-500">Checking…</p>}
        {health.isError && <p className="text-red-600">Backend unreachable: {health.error.message}</p>}
        {health.data && (
          <p className="text-stone-600">
            API {health.data.status} · Database {health.data.db ? "connected" : "not reachable"}
          </p>
        )}
        <CollectorStatus />
      </div>

      <div className="rounded-lg border border-dashed border-stone-300 p-4 text-sm text-stone-600">
        <p>
          The daily brief will appear here once scoring and cards are built: a top story, 3–5 rising repos and 2–3
          news items.
        </p>
        <p className="mt-2">
          Meanwhile, see everything being collected on{" "}
          <Link to="/repos" className="font-medium text-stone-900 underline underline-offset-2">
            Rising repos
          </Link>
          .
        </p>
      </div>
    </section>
  );
}
