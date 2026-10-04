import { useParams } from "react-router";

export default function Card() {
  const { itemType, itemId } = useParams();

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Card</h1>
      <p className="text-stone-500">
        Full card for {itemType} #{itemId}. Coming soon.
      </p>
    </section>
  );
}
