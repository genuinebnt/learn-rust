import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

const names = ["n0", "n1", "n2", "n3", "n4", "n5"];
const run = (request: APIRequestContext, stage: string, status: ("ok" | "bad")[], commit: string) =>
    request.post("/api/courses/bustub/runs", { data: { stage_id: stage, tests: status.map((s, i) => ({ name: names[i], ok: s === "ok", detail: s === "ok" ? "" : "assertion failed" })), commit, duration_ms: 1200 } });

test.describe("Last run", () => {
    const stage = "4a-05";
    test.beforeAll(async ({ request }) => {
        await request.post("/api/courses/bustub/runs", { data: { stage_id: stage, problem: "error[E0308]: mismatched types\n  --> src/x.rs:1:1\n", commit: "1111111", duration_ms: 500 } });
        await run(request, stage, ["ok", "bad", "bad", "ok", "bad", "bad"], "2222222"); // 2 passed
        await run(request, stage, ["ok", "bad", "ok", "ok", "bad", "ok"], "3333333"); // 4 passed: n2 and n5 fixed
        await run(request, stage, ["ok", "bad", "ok", "bad", "bad", "ok"], "4444444"); // 3 passed: n3 newly failing
    });
    const open = async (page: Page) => {
        await page.goto(`/courses/bustub/${stage}#run`);
        await expect(page.locator(".cx-rsum")).toBeVisible();
    };

    test("the history shows the recent runs, the newest selected", async ({ page }) => {
        await open(page);
        expect(await page.locator(".cx-hbar").count()).toBeGreaterThanOrEqual(4);
        await expect(page.locator(".cx-hbar").last()).toHaveAttribute("aria-pressed", "true");
        await expect(page.locator(".cx-rsum")).toContainText("3 failed");
    });

    test("the newest run says how it differs from the one before", async ({ page }) => {
        await open(page);
        await expect(page.locator(".cx-rdelta")).toContainText("1 fewer passing");
        await expect(page.locator(".cx-rdelta")).toContainText("1 newly failing");
    });

    test("picking an older run shows that run and its own comparison", async ({ page }) => {
        await open(page);
        const bars = page.locator(".cx-hbar");
        await bars.nth((await bars.count()) - 2).click(); // the run with 4 passed
        await expect(page.locator(".cx-rsum")).toContainText("2 failed");
        await expect(page.locator(".cx-rsum")).toContainText("4 passed");
        await expect(page.locator(".cx-rdelta")).toContainText("2 more passing");
    });

    test("the Failed and Passed filters show one side each", async ({ page }) => {
        await open(page);
        await page.locator(".cx-rflt").getByRole("button", { name: "Failed" }).click();
        await expect(page.locator(".cx-rfail")).toHaveCount(3);
        await expect(page.locator(".cx-rfold")).toHaveCount(0);
        await page.locator(".cx-rflt").getByRole("button", { name: "Passed" }).click();
        await expect(page.locator(".cx-rfail")).toHaveCount(0);
        await expect(page.locator(".cx-rrow")).toHaveCount(3);
    });

    test("compare marks what is newly failing, still failing and fixed", async ({ page }) => {
        await open(page);
        await page.getByRole("switch", { name: "Compare with the previous run" }).click();
        await expect(page.locator(".cx-rfail", { hasText: "n3" }).locator(".cx-rtag")).toHaveText("NEWLY FAILING");
        await expect(page.locator(".cx-rfail", { hasText: "n1" }).locator(".cx-rtag")).toHaveText("STILL FAILING");
        // the run before: its two fixed tests
        const bars = page.locator(".cx-hbar");
        await bars.nth((await bars.count()) - 2).click();
        await page.getByRole("switch", { name: "Compare with the previous run" }).click();
        await page.locator(".cx-rfoldh").click();
        await expect(page.locator(".cx-rrow .cx-rtag.fix")).toHaveCount(2);
    });

    test("a run with a compile error is shown as one that did not run", async ({ page }) => {
        await open(page);
        const bars = page.locator(".cx-hbar");
        const n = await bars.count();
        // the compile-error run is the oldest of the four seeded: three bars before the newest
        await bars.nth(n - 4).click();
        await expect(page.locator(".cx-rsum")).toContainText("Did not run");
        await expect(page.locator(".cx-rprob")).toContainText("error[E0308]");
    });

    test("a run that arrives while the tab is open becomes the selected one", async ({ page, request }) => {
        await open(page);
        const before = await page.locator(".cx-hbar").count();
        await run(request, stage, ["ok", "ok", "bad", "ok", "ok", "ok"], "5555555");
        await expect(page.locator(".cx-rsum")).toContainText("1 failed", { timeout: 15_000 });
        expect(await page.locator(".cx-hbar").count()).toBeGreaterThanOrEqual(Math.min(before + 1, 10));
    });
});

test.describe("Concepts", () => {
    const stage = "4a-04";
    // Read state lives on the server: start each test from "nothing read".
    test.beforeEach(async ({ page, request }) => {
        const st = await (await request.get(`/api/courses/bustub/stages/${stage}`)).json();
        for (const k of st.concepts) await request.put(`/api/courses/bustub/concepts/${k.id}/read`, { data: { read: false } });
        await page.goto(`/courses/bustub/${stage}#concepts`);
        await expect(page.locator(".cx-chdr")).toBeVisible();
    });

    test("the header counts the required reading and each concept has a card", async ({ page }) => {
        await expect(page.locator(".cx-chdr")).toContainText("Required reading: 0 of 3 done");
        await expect(page.locator(".cx-ccard")).toHaveCount(3);
        await expect(page.locator(".cx-cbadge.req")).toHaveCount(3);
        await expect(page.getByRole("tab", { name: /^Concepts/ })).toContainText("0/3");
    });

    test("marking one as read updates the header, the tab and the page panel, and it is kept", async ({ page }) => {
        await page.locator(".cx-ccard").first().getByRole("button", { name: /Preview/ }).click();
        await page.locator(".cx-ccard").first().getByRole("switch").click();
        await expect(page.locator(".cx-chdr")).toContainText("1 of 3 done");
        await expect(page.getByRole("tab", { name: /^Concepts/ })).toContainText("1/3");
        await expect(page.locator(".cx-toc .cx-crow.read")).toHaveCount(1);
        await expect(page.locator(".cx-ccard.read")).toHaveCount(1);
        await page.reload();
        await expect(page.locator(".cx-chdr")).toContainText("1 of 3 done");
        // and it can be undone
        await page.locator(".cx-ccard").first().getByRole("button", { name: /Preview/ }).click();
        await page.locator(".cx-ccard").first().getByRole("switch").click();
        await expect(page.locator(".cx-chdr")).toContainText("0 of 3 done");
    });

    test("Preview opens a card and Read opens the article", async ({ page }) => {
        const first = page.locator(".cx-ccard").first();
        const btn = first.getByRole("button", { name: /Preview|Close/ });
        await expect(btn).toHaveAttribute("aria-expanded", "false");
        await btn.click();
        await expect(btn).toHaveAttribute("aria-expanded", "true");
        await first.getByRole("link", { name: /Read/ }).click();
        await expect(page).toHaveURL(/\/courses\/bustub\/concept\//);
    });

    test("marking all the required ones read says so", async ({ page }) => {
        for (let i = 0; i < 3; i++) {
            const c = page.locator(".cx-ccard").nth(i);
            await c.getByRole("button", { name: /Preview/ }).click();
            await c.getByRole("switch").click();
        }
        await expect(page.locator(".cx-chdr")).toContainText("Required reading done");
    });
});
