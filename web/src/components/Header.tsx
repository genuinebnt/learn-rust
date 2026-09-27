import { Link, useRouterState } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { ACCENTS, useAppearance } from "../settings";

const AREAS = [
  { to: "/dsa", label: "DSA", color: "var(--acc)", match: ["/dsa"] },
  { to: "/rust", label: "Rust", color: "var(--vio)", match: ["/rust"] },
  { to: "/build", label: "Build", color: "var(--grn)", match: ["/build"] },
] as const;

/** Nav items whose screens are designed but not built yet. */
const LATER = ["Library", "Mock interview"];

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
        <Link to="/progress" className={path.startsWith("/progress") ? "on" : ""} style={{ color: path.startsWith("/progress") ? "var(--fg)" : "var(--dim)" }}>
          Progress
        </Link>
        <span className="nav-later" title="Designed; not built yet">
          Readiness
        </span>
      </nav>
      <div className="hdr-r">
        <span className="rd">
          SOLVED <b>{solved ?? "–"}</b>
        </span>
        <button className="thm" onClick={toggleTheme} title="Toggle theme" aria-label="Toggle theme">
          <span />
        </button>
        <Account />
      </div>
    </header>
  );
}

/** The avatar menu: accent colour, and Sign out when login is on. */
function Account() {
  const session = useQuery({ queryKey: ["session"], queryFn: api.session, staleTime: Infinity });
  const { accent, set } = useAppearance();
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const close = (e: MouseEvent) => !box.current?.contains(e.target as Node) && setOpen(false);
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", esc);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", esc);
    };
  }, [open]);
  return (
    <div className="acct" ref={box}>
      <button className="av" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen(!open)} title="Settings">
        gb
      </button>
      {open && (
        <div className="acct-menu" role="menu">
          <span className="acct-lab">ACCENT</span>
          <div className="swatches" role="radiogroup" aria-label="Accent colour">
            {ACCENTS.map((a) => (
              <button key={a.id} role="radio" aria-checked={accent === a.id} className={`swatch${accent === a.id ? " on" : ""}`} data-swatch={a.id} onClick={() => set(a.id)} title={a.label}>
                <span />
                {a.label}
              </button>
            ))}
          </div>
          {session.data?.required && (
            <button
              role="menuitem"
              className="acct-out"
              onClick={async () => {
                await api.logout().catch(() => undefined);
                location.assign("/login");
              }}
            >
              Sign out
            </button>
          )}
        </div>
      )}
    </div>
  );
}
