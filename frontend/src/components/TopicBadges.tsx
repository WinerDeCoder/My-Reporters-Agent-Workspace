/** Matched interest topics (spec 003), shown on repo and story rows. */
export default function TopicBadges({ topics }: { topics: string[] }) {
  if (topics.length === 0) return null;
  return (
    <>
      {topics.map((t) => (
        <span
          key={t}
          title="Matches one of your interest topics (config.yaml → interests.topics)"
          className="rounded bg-indigo-50 px-1.5 py-0.5 text-xs font-medium text-indigo-700"
        >
          {t}
        </span>
      ))}
    </>
  );
}
