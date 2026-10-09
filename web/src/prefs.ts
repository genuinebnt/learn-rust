// Small choices remembered in this browser (panel sizes, "don't show again"). Storage can be blocked or full: every read and write is guarded.

const PREFIX = "anneal:";

export function getPref<T>(key: string, fallback: T): T {
    try {
        const v = localStorage.getItem(PREFIX + key);
        return v === null ? fallback : (JSON.parse(v) as T);
    } catch {
        return fallback;
    }
}

export function setPref(key: string, value: unknown) {
    try {
        localStorage.setItem(PREFIX + key, JSON.stringify(value));
    } catch {
        // nothing to do: the choice is simply not remembered
    }
}
