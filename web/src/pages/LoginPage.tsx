import { useQuery } from "@tanstack/react-query";
import { useEffect, useState, type FormEvent } from "react";
import { ApiError, api } from "../api";

/** Only same-site paths, so `?next=` can't send you to another site. */
function nextPath() {
  const next = new URLSearchParams(location.search).get("next") ?? "/";
  return next.startsWith("/") && !next.startsWith("//") ? next : "/";
}

export function LoginPage() {
  const session = useQuery({ queryKey: ["session"], queryFn: api.session, retry: false });
  const [passphrase, setPassphrase] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (session.data && (!session.data.required || session.data.authenticated)) location.replace(nextPath());
  }, [session.data]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.login(passphrase);
      location.replace(nextPath());
    } catch (err) {
      setError(err instanceof ApiError && err.code === "wrong_passphrase" ? "That passphrase isn't right." : err instanceof Error ? err.message : "Couldn't sign in.");
      setPassphrase("");
      setBusy(false);
    }
  }

  return (
    <main className="page login">
      <form className="login-card" onSubmit={submit}>
        <span className="logo" aria-hidden="true">
          <span className="mk">
            <span style={{ background: "var(--acc)" }} />
            <span style={{ background: "var(--vio)" }} />
            <span style={{ background: "var(--grn)" }} />
            <span style={{ boxShadow: "inset 0 0 0 1px var(--line)" }} />
          </span>
          <b>
            anneal<i>.genuinebasil.dev</i>
          </b>
        </span>
        <h1>Sign in</h1>
        <label className="login-field">
          <span>PASSPHRASE</span>
          <input
            type="password"
            autoComplete="current-password"
            autoFocus
            required
            value={passphrase}
            onChange={(e) => setPassphrase(e.target.value)}
          />
        </label>
        {error && (
          <p className="login-err" role="alert">
            {error}
          </p>
        )}
        <button className="login-go" type="submit" disabled={busy || !passphrase}>
          {busy ? "Signing in…" : "Sign in →"}
        </button>
      </form>
    </main>
  );
}
