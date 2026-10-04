// Thin fetch helper. Once the API grows, run `npm run gen:api` (backend must be running)
// to generate src/api/schema.d.ts from FastAPI's OpenAPI and type responses from it.

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`);
  return res.json() as Promise<T>;
}

export type Health = { status: string; db: boolean };
