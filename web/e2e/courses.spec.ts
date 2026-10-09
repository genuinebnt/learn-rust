import { expect, test, type Page } from "@playwright/test";

const rows = ".k-mod .k-row";

/** Closes every module: from a partly open course the button first reads "expand all". */
async function collapseAll(page: Page) {
    if (await page.getByRole("button", { name: "EXPAND ALL" }).count()) await page.getByRole("button", { name: "EXPAND ALL" }).click();
    await page.getByRole("button", { name: "COLLAPSE ALL" }).click();
    await expect(page.locator(".k-mod.k-open")).toHaveCount(0);
}

test.beforeEach(async ({ page }) => {
    await page.goto("/courses");
    await expect(page.locator(".k-map")).toBeVisible();
});

test("modules that are being rewritten carry a PLANNED tag and the finished ones do not", async ({ page }) => {
    const course = await (await page.request.get("/api/courses/bustub")).json();
    const modules: { code: string; planned: boolean }[] = course.projects.flatMap((p: { modules: { code: string; planned: boolean }[] }) => p.modules);
    await page.goto("/courses/bustub");
    await expect(page.locator(".k-mod").first()).toBeVisible();
    for (const m of modules) {
        const tag = page.locator(`#mod-${m.code} .k-planned`);
        if (m.planned) await expect(tag).toHaveText("PLANNED");
        else await expect(tag).toHaveCount(0);
    }
    // the first module is finished and stays untagged
    await expect(page.locator("#mod-1a .k-planned")).toHaveCount(0);
});

test("the map has a button for every module and opens the one you click", async ({ page }) => {
    const n = await page.locator(".k-node").count();
    expect(n).toBeGreaterThanOrEqual(25);
    const header = page.locator("#mod-4a .k-mh");
    await expect(header).toHaveAttribute("aria-expanded", "false");
    await page.locator(".k-node", { hasText: "4A" }).click();
    await expect(header).toHaveAttribute("aria-expanded", "true");
    await expect(page.locator("#mod-4a .k-row").first()).toBeVisible();
});

test("only the module you are in starts open, and Expand all opens the rest", async ({ page }) => {
    const open = page.locator(".k-mod.k-open");
    await expect(open).toHaveCount(1);
    await expect(open.first()).toHaveAttribute("id", /mod-/);
    await page.getByRole("button", { name: "EXPAND ALL" }).click();
    const all = await page.locator(".k-mod").count();
    await expect(page.locator(".k-mod.k-open")).toHaveCount(all);
    await page.getByRole("button", { name: "COLLAPSE ALL" }).click();
    await expect(page.locator(".k-mod.k-open")).toHaveCount(0);
});

test("collapsed rows cannot be tabbed into", async ({ page }) => {
    await collapseAll(page);
    expect(await page.locator("#mod-1b div[inert]").count()).toBe(1);
    await page.locator("#mod-1b .k-mh").click();
    expect(await page.locator("#mod-1b div[inert]").count()).toBe(0);
});

test("an open module is remembered after a reload", async ({ page }) => {
    await collapseAll(page);
    await page.locator("#mod-2b .k-mh").click();
    await expect(page.locator("#mod-2b")).toHaveClass(/k-open/);
    await page.reload();
    await expect(page.locator("#mod-2b")).toHaveClass(/k-open/);
    await expect(page.locator("#mod-1a")).not.toHaveClass(/k-open/);
});

test("find narrows to matching stages and opens their modules; clearing restores the choice", async ({ page }) => {
    await page.getByLabel("Find a stage").fill("watermark");
    await expect(page.locator(rows)).toHaveCount(1);
    await expect(page.locator(rows).first()).toContainText("watermark");
    await expect(page.locator(".k-mod.k-open")).toHaveCount(1);
    await page.getByLabel("Find a stage").fill("zzzz-no-stage");
    await expect(page.locator(".k-none")).toContainText("No stage matches");
    await page.getByRole("button", { name: "Clear it" }).click();
    await expect(page.locator(".k-none")).toHaveCount(0);
    await expect(page.locator(".k-mod.k-open")).toHaveCount(1);
});

test("the boss filter shows only BusTub test stages", async ({ page }) => {
    await page.getByRole("button", { name: "boss", exact: true }).click();
    await expect(page.getByRole("button", { name: "boss", exact: true })).toHaveAttribute("aria-pressed", "true");
    const n = await page.locator(rows).count();
    expect(n).toBeGreaterThan(5);
    await expect(page.locator(`${rows} .k-boss`)).toHaveCount(n);
    await page.getByRole("button", { name: "all", exact: true }).click();
    expect(await page.locator(".k-mod.k-open .k-row").count()).toBeGreaterThan(0);
});

test("the to-do and passed filters split the stages", async ({ page }) => {
    await page.getByRole("button", { name: "to do", exact: true }).click();
    const todo = await page.locator(rows).count();
    await page.getByRole("button", { name: "passed", exact: true }).click();
    const done = await page.locator(rows).count().catch(() => 0);
    expect(todo).toBeGreaterThan(100);
    const total = (await (await page.request.get("/api/courses/bustub")).json()).total;
    expect(todo + done).toBe(total);
});

test("/ focuses the find box, and Escape leaves it", async ({ page }) => {
    await page.keyboard.press("/");
    await expect(page.getByLabel("Find a stage")).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.getByLabel("Find a stage")).not.toBeFocused();
});

test("each get-started command has its own copy button", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await expect(page.locator(".k-cmd")).toHaveCount(4);
    const second = page.locator(".k-cmd").nth(1);
    await second.getByRole("button").click();
    await expect(second.getByRole("button")).toHaveText("COPIED");
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe("cd bustub-rs");
});

test("a project's progress bar opens that project's first module", async ({ page }) => {
    await collapseAll(page);
    await page.locator(".k-pr", { hasText: "Project 2" }).click();
    await expect(page.locator("#mod-2a")).toHaveClass(/k-open/);
});

test("a link to a planned Rust track lands on a planned page, not an error", async ({ page }) => {
    await page.goto("/t/c1-threads-shared-state");
    await expect(page.getByTestId("planned-track")).toContainText("C1 · Threads & shared state");
    await expect(page.getByTestId("planned-track")).toContainText("planned");
});
