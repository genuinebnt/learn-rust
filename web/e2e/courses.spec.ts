import { expect, test, type Page } from "@playwright/test";

const rows = ".cx-mod .cx-srow";

/** Closes every module: from a partly open course the button first reads "expand all". */
async function collapseAll(page: Page) {
    if (await page.getByRole("button", { name: "EXPAND ALL" }).count()) await page.getByRole("button", { name: "EXPAND ALL" }).click();
    await page.getByRole("button", { name: "COLLAPSE ALL" }).click();
    await expect(page.locator(".cx-mod.open")).toHaveCount(0);
}

test.beforeEach(async ({ page }) => {
    await page.goto("/courses");
    await expect(page.locator(".cx-map")).toBeVisible();
});

test("the map has a button for every module and opens the one you click", async ({ page }) => {
    const n = await page.locator(".cx-node").count();
    expect(n).toBeGreaterThanOrEqual(25);
    const header = page.locator("#mod-4a .cx-mh");
    await expect(header).toHaveAttribute("aria-expanded", "false");
    await page.locator(".cx-node", { hasText: "4A" }).click();
    await expect(header).toHaveAttribute("aria-expanded", "true");
    await expect(page.locator("#mod-4a .cx-srow").first()).toBeVisible();
});

test("only the module you are in starts open, and Expand all opens the rest", async ({ page }) => {
    const open = page.locator(".cx-mod.open");
    await expect(open).toHaveCount(1);
    await expect(open.first()).toHaveAttribute("id", /mod-/);
    await page.getByRole("button", { name: "EXPAND ALL" }).click();
    const all = await page.locator(".cx-mod").count();
    await expect(page.locator(".cx-mod.open")).toHaveCount(all);
    await page.getByRole("button", { name: "COLLAPSE ALL" }).click();
    await expect(page.locator(".cx-mod.open")).toHaveCount(0);
});

test("collapsed rows cannot be tabbed into", async ({ page }) => {
    await collapseAll(page);
    expect(await page.locator("#mod-1b div[inert]").count()).toBe(1);
    await page.locator("#mod-1b .cx-mh").click();
    expect(await page.locator("#mod-1b div[inert]").count()).toBe(0);
});

test("an open module is remembered after a reload", async ({ page }) => {
    await collapseAll(page);
    await page.locator("#mod-2b .cx-mh").click();
    await expect(page.locator("#mod-2b")).toHaveClass(/open/);
    await page.reload();
    await expect(page.locator("#mod-2b")).toHaveClass(/open/);
    await expect(page.locator("#mod-1a")).not.toHaveClass(/open/);
});

test("find narrows to matching stages and opens their modules; clearing restores the choice", async ({ page }) => {
    await page.getByLabel("Find a stage").fill("watermark");
    await expect(page.locator(rows)).toHaveCount(1);
    await expect(page.locator(rows).first()).toContainText("watermark");
    await expect(page.locator(".cx-mod.open")).toHaveCount(1);
    await page.getByLabel("Find a stage").fill("zzzz-no-stage");
    await expect(page.locator(".cx-none")).toContainText("No stage matches");
    await page.getByRole("button", { name: "Clear it" }).click();
    await expect(page.locator(".cx-none")).toHaveCount(0);
    await expect(page.locator(".cx-mod.open")).toHaveCount(1);
});

test("the boss filter shows only BusTub test stages", async ({ page }) => {
    await page.getByRole("button", { name: "boss", exact: true }).click();
    await expect(page.getByRole("button", { name: "boss", exact: true })).toHaveAttribute("aria-pressed", "true");
    const n = await page.locator(rows).count();
    expect(n).toBeGreaterThan(5);
    await expect(page.locator(`${rows} em`)).toHaveCount(n);
    await page.getByRole("button", { name: "all", exact: true }).click();
    expect(await page.locator(".cx-mod.open .cx-srow").count()).toBeGreaterThan(0);
});

test("the to-do and passed filters split the stages", async ({ page }) => {
    await page.getByRole("button", { name: "to do", exact: true }).click();
    const todo = await page.locator(rows).count();
    await page.getByRole("button", { name: "passed", exact: true }).click();
    const done = await page.locator(rows).count().catch(() => 0);
    expect(todo).toBeGreaterThan(100);
    expect(todo + done).toBe(163);
});

test("/ focuses the find box, and Escape leaves it", async ({ page }) => {
    await page.keyboard.press("/");
    await expect(page.getByLabel("Find a stage")).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.getByLabel("Find a stage")).not.toBeFocused();
});

test("each get-started command has its own copy button", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await expect(page.locator(".cx-cmd")).toHaveCount(4);
    const second = page.locator(".cx-cmd").nth(1);
    await second.getByRole("button").click();
    await expect(second.getByRole("button")).toHaveText("COPIED");
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe("cd bustub-rs");
});

test("a project's progress bar opens that project's first module", async ({ page }) => {
    await collapseAll(page);
    await page.locator(".rmeter.link", { hasText: "Project 2" }).click();
    await expect(page.locator("#mod-2a")).toHaveClass(/open/);
});
