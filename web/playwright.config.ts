import { defineConfig } from "@playwright/test";

// End-to-end tests of the built web app against a running API (see e2e/README.md). They share one database, so one worker.
export default defineConfig({
    testDir: "e2e",
    workers: 1,
    retries: process.env.CI ? 1 : 0,
    reporter: process.env.CI ? [["list"], ["github"]] : "list",
    use: {
        baseURL: process.env.E2E_BASE_URL ?? "http://127.0.0.1:8791",
        viewport: { width: 1440, height: 900 },
        trace: "retain-on-failure",
        // Locally, E2E_CHROME=1 uses the installed Chrome instead of the downloaded Chromium.
        channel: process.env.E2E_CHROME ? "chrome" : undefined,
    },
});
