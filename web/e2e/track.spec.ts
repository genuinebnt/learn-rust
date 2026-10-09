import { expect, test } from "@playwright/test";

const rows = ".tbl-co > .tr:not(.th):not(.tr-empty)";

test.beforeEach(async ({ page }) => {
    await page.goto("/t/l1-ownership-moves");
    await expect(page.locator(rows).first()).toBeVisible();
});

test("the filter box narrows the table and clearing it brings every row back", async ({ page }) => {
    const all = await page.locator(rows).count();
    expect(all).toBeGreaterThan(5);
    await page.getByLabel("Filter problems").fill("clone");
    const some = await page.locator(rows).count();
    expect(some).toBeGreaterThan(0);
    expect(some).toBeLessThan(all);
    for (const text of await page.locator(rows).allInnerTexts()) expect(text.toLowerCase()).toContain("clone");
    await expect(page.locator(".fcount")).toHaveText(`${some} of ${all}`);
    await page.getByLabel("Filter problems").fill("");
    await expect(page.locator(rows)).toHaveCount(all);
});

test("a no-match filter says so and offers to clear it", async ({ page }) => {
    await page.getByLabel("Filter problems").fill("zzzz-no-such-problem");
    await expect(page.locator(".tr-empty")).toContainText("No problem matches that filter");
    await page.getByRole("button", { name: "CLEAR IT" }).click();
    await expect(page.locator(rows).first()).toBeVisible();
});

test("/ focuses the filter box and Escape leaves it", async ({ page }) => {
    await page.keyboard.press("/");
    await expect(page.getByLabel("Filter problems")).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.getByLabel("Filter problems")).not.toBeFocused();
});

test("clicking a header sorts, again reverses, a third time restores the recommended order", async ({ page }) => {
    const titles = async () => (await page.locator(`${rows} .pt`).allInnerTexts()).map((t) => t.trim());
    const original = await titles();
    const header = page.locator(".th .sorth", { hasText: "Problem" });
    await header.click();
    const asc = await titles();
    expect(asc).toEqual([...original].sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase())).map((t) => t));
    await expect(header).toHaveAttribute("aria-sort", "ascending");
    await header.click();
    expect(await titles()).toEqual([...asc].reverse());
    await header.click();
    expect(await titles()).toEqual(original);
    await expect(header).toHaveAttribute("aria-sort", "none");
});

test("j and k move a row highlight and Enter opens a ready problem", async ({ page }) => {
    await page.keyboard.press("j");
    await expect(page.locator(`${rows}.kb`)).toHaveCount(1);
    await expect(page.locator(rows).nth(0)).toHaveClass(/kb/);
    await page.keyboard.press("j");
    await expect(page.locator(rows).nth(1)).toHaveClass(/kb/);
    await page.keyboard.press("k");
    await expect(page.locator(rows).nth(0)).toHaveClass(/kb/);
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/\/p\//);
});

test("every row has a status icon and its word", async ({ page }) => {
    const n = await page.locator(rows).count();
    await expect(page.locator(`${rows} svg.sicon`)).toHaveCount(2 * n);
    await expect(page.locator(`${rows} .best.stat`).first()).toContainText(/not started|in progress|solved|not written/);
});

test("keys are ignored while typing in the filter box", async ({ page }) => {
    await page.getByLabel("Filter problems").fill("");
    await page.getByLabel("Filter problems").press("j");
    await expect(page.locator(`${rows}.kb`)).toHaveCount(0);
});
