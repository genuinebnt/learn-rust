import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import { toast } from "./toasts";

/** "Reset progress" for one track or pattern: forgets what you solved there. Asks for the word "reset" first. */
export function ResetTrack({ slug, name, onDone }: { slug: string; name: string; onDone: () => void }) {
    const qc = useQueryClient();
    const [word, setWord] = useState("");
    const [busy, setBusy] = useState(false);
    const go = async () => {
        setBusy(true);
        try {
            const r = await api.resetTrack(slug);
            toast("ok", "Progress reset", `${r.attempts_removed} attempt${r.attempts_removed === 1 ? "" : "s"} on ${r.problems} problems forgotten.`);
            await qc.invalidateQueries();
            onDone();
        } catch (e) {
            toast("in", "Could not reset", e instanceof Error ? e.message : String(e));
        } finally {
            setBusy(false);
        }
    };
    return (
        <div className="trk-reset" role="group" aria-label="Reset progress">
            <p>
                Forgets what you solved in <b>{name}</b>: attempts, runs, saved drafts, scratch files and the review schedule of its problems. Your written solutions are kept.
            </p>
            <label>
                Type <b>reset</b> to confirm
                <input value={word} onChange={(e) => setWord(e.target.value)} placeholder="reset" autoComplete="off" />
            </label>
            <button className="trk-del" disabled={word.trim() !== "reset" || busy} onClick={go}>
                {busy ? "Resetting…" : "Reset progress"}
            </button>
        </div>
    );
}
