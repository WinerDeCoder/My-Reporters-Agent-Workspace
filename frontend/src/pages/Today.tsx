import { useQuery } from "@tanstack/react-query";

import { getJson, type Health } from "../api/client";

export default function Today() {
  const health = useQuery({ queryKey: ["health"], queryFn: () => getJson<Health>("/health") });

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Today</h1>

      <div className="rounded-lg border border-stone-200 bg-white p-4 text-sm">
        <p className="font-medium">System status</p>
        {health.isPending && <p className="text-stone-500">Checking…</p>}
        {health.isError && <p className="text-red-600">Backend unreachable: {health.error.message}</p>}
        {health.data && (
          <ul className="mt-1 text-stone-600">
            <li>API: {health.data.status}</li>
            <li>Database: {health.data.db ? "connected" : "not reachable"}</li>
          </ul>
        )}
      </div>

      <p className="text-stone-500">
        The daily brief will appear here: a top story, 3–5 rising repos and 2–3 news items.
      </p>
    </section>
  );
}
