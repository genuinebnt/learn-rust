import { expect, test } from "@playwright/test";

const tests = (names: string[], bad: string[]) => names.map((name) => ({ name, ok: !bad.includes(name), detail: bad.includes(name) ? "assertion failed\n left: 4\nright: 3" : "" }));

test.beforeAll(async ({ request }) => {
    // Failing runs only: nothing becomes solved.
    await request.post("/api/courses/bustub/runs", {
        data: {
            stage_id: "4a-04",
            tests: tests(["a_passes", "b_fails", "c_passes", "d_passes", "e_fails", "f_passes"], ["b_fails", "e_fails"]),
            commit: "4f1c9ab1",
            duration_ms: 2400,
        },
    });
    await request.post("/api/courses/bustub/runs", {
        data: { stage_id: "4a-03", problem: "error[E0308]: mismatched types\n  --> src/x.rs:1:1\n", commit: "c70aa13f", duration_ms: 900 },
    });
});

test("the Run tab lists failures first and open, with a summary and a segment per test", async ({ page }) => {
    await page.goto("/courses/bustub/4a-04#run");
    await expect(page.locator(".cx-rsum")).toContainText("2 failed");
    await expect(page.locator(".cx-rsum")).toContainText("4 passed");
    await expect(page.locator(".cx-rbar i")).toHaveCount(6);
    await expect(page.locator(".cx-rbar i.b")).toHaveCount(2);
    await expect(page.locator(".cx-rfail")).toHaveCount(2);
    await expect(page.locator(".cx-rfail").first()).toContainText("b_fails");
    await expect(page.locator(".cx-rfail").first()).toContainText("same message as 1 other test");
    // the failures come before the passes in the page
    const fail = await page.locator(".cx-rfail").first().boundingBox();
    const pass = await page.locator(".cx-rfold").boundingBox();
    expect(fail!.y).toBeLessThan(pass!.y);
});

test("passing tests are folded until you open them", async ({ page }) => {
    await page.goto("/courses/bustub/4a-04#run");
    await expect(page.locator(".cx-rrow")).toHaveCount(0);
    await page.locator(".cx-rfoldh").click();
    await expect(page.locator(".cx-rrow")).toHaveCount(4);
    await page.locator(".cx-rfoldh").click();
    await expect(page.locator(".cx-rrow")).toHaveCount(0);
});

test("the run-again command is copyable", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto("/courses/bustub/4a-04#run");
    await expect(page.locator(".cx-rcmd code")).toHaveText("anneal course test 4a-04 --only -f b_fails");
    await page.locator(".cx-rcmd button").click();
    await expect(page.locator(".cx-rcmd button")).toHaveText("COPIED");
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe("anneal course test 4a-04 --only -f b_fails");
});

test("a run that did not compile shows the compiler output and no segments", async ({ page }) => {
    await page.goto("/courses/bustub/4a-03#run");
    await expect(page.locator(".cx-rsum")).toContainText("Did not run");
    await expect(page.locator(".cx-rprob")).toContainText("error[E0308]");
    await expect(page.locator(".cx-rbar")).toHaveCount(0);
    await expect(page.locator(".cx-rcmd")).toContainText("compile locally");
});

test("the stage header has the test command with a copy button", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto("/courses/bustub/4a-04");
    await expect(page.locator(".cx-cli code")).toHaveText("anneal course test 4a-04");
    await page.locator(".cx-cli button").click();
    await expect(page.locator(".cx-cli button")).toHaveText("COPIED");
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe("anneal course test 4a-04");
});

test("each tab remembers its scroll position", async ({ page }) => {
    await page.goto("/courses/bustub/4a-04");
    await expect(page.locator(".cx-tabs")).toBeVisible();
    // far enough to matter, but with the tab bar still on screen so that clicking a tab does not scroll the page itself
    await page.evaluate(() => window.scrollTo(0, 300));
    await expect.poll(() => page.evaluate(() => Math.round(window.scrollY))).toBeGreaterThan(250);
    const before = await page.evaluate(() => Math.round(window.scrollY));
    // click in the page: Playwright's own click scrolls the target into view first, which would move the page
    const clickTab = (name: RegExp) => page.getByRole("tab", { name }).evaluate((el) => (el as HTMLElement).click());
    await clickTab(/^Hints/);
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBeLessThan(50);
    await clickTab(/^Instructions/);
    await expect.poll(() => page.evaluate(() => Math.round(window.scrollY))).toBeGreaterThan(before - 40);
});

test("the course page's continue card shows the module ring", async ({ page }) => {
    await page.goto("/courses");
    await expect(page.locator(".cx-cont .cx-ring")).toBeVisible();
    await expect(page.locator(".cx-cont .cx-contb small")).toContainText("·");
});
