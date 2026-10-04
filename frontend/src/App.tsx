import { NavLink, Route, Routes } from "react-router";

import Card from "./pages/Card";
import Leaderboard from "./pages/Leaderboard";
import Stats from "./pages/Stats";
import Today from "./pages/Today";

const links = [
  { to: "/", label: "Today" },
  { to: "/leaderboard", label: "Leaderboard" },
  { to: "/stats", label: "Stats" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-stone-50 text-stone-900">
      <header className="border-b border-stone-200 bg-white">
        <nav className="mx-auto flex max-w-3xl items-center gap-6 px-4 py-3">
          <span className="font-semibold">Tech Radar</span>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end
              className={({ isActive }) =>
                isActive ? "font-medium text-stone-900" : "text-stone-500 hover:text-stone-900"
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="mx-auto max-w-3xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Today />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/stats" element={<Stats />} />
          <Route path="/cards/:itemType/:itemId" element={<Card />} />
        </Routes>
      </main>
    </div>
  );
}
