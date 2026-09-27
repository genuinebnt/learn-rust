import { Link, useRouterState } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";

const AREAS = [
  { to: "/dsa", label: "DSA", color: "var(--acc)", match: ["/dsa"] },
  { to: "/rust", label: "Rust", color: "var(--vio)", match: ["/rust"] },
  { to: "/build", label: "Build", color: "var(--grn)", match: ["/build"] },
] as const;

/** Nav items whose screens are designed but not built yet. */
const LATER = ["Library", "Mock interview", "Readiness"];

function toggleTheme() {
  const root = document.documentElement;
  const current = root.dataset.theme ?? (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  const next = current === "dark" ? "light" : "dark";
  root.dataset.theme = next;
  try {
    localStorage.setItem("anneal-theme", next);
  } catch {
    // Private windows can refuse storage; the toggle still works for this visit.
  }
}

export function Header({ area }: { area?: "dsa" | "rust" | "build" }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const tracks = useQuery({ queryKey: ["tracks"], queryFn: api.tracks });
  const solved = tracks.data?.reduce((n, t) => n + t.solved, 0);
  return (
    <header className="hdr">
      <Link className="logo" to="/" aria-label="anneal home">
        <span className="mk">
          <span style={{ background: "var(--acc)" }} />
          <span style={{ background: "var(--vio)" }} />
          <span style={{ background: "var(--grn)" }} />
          <span style={{ boxShadow: "inset 0 0 0 1px var(--line)" }} />
        </span>
        <b>
          anneal<i>.genuinebasil.dev</i>
        </b>
      </Link>
      <nav className="nav" aria-label="Sections">
        {AREAS.map((a) => {
          const on = area === a.to.slice(1) || a.match.some((m) => path.startsWith(m));
          return (
            <Link key={a.to} to={a.to} className={on ? "on" : ""} style={{ color: a.color }} aria-current={on ? "page" : undefined}>
              {a.label}
            </Link>
          );
        })}
        <span style={{ color: "var(--line)" }}>|</span>
        {LATER.map((l) => (
          <span key={l} className="nav-later" title="Designed; not built yet">
            {l}
          </span>
        ))}
      </nav>
      <div className="hdr-r">
        <span className="rd">
          SOLVED <b>{solved ?? "–"}</b>
        </span>
        <button className="thm" onClick={toggleTheme} title="Toggle theme" aria-label="Toggle theme">
          <span />
        </button>
        <span className="av">gb</span>
      </div>
    </header>
  );
}
