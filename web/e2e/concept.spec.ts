import { expect, test } from "@playwright/test";

test("code-only cells in a comparison table are highlighted and copyable", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto("/courses/bustub/concept/durability-and-fsync");
    const cell = page.locator(".k-vt td:has(.k-copy) code").first();
    await expect(cell).toBeVisible();
    await expect(page.locator(".k-vt td code span[class^='t-']").first()).toBeVisible();
    const td = cell.locator("xpath=..");
    await td.hover();
    const btn = td.locator(".k-copy");
    await expect(btn).toBeVisible();
    const text = await btn.getAttribute("data-c");
    await btn.click();
    await expect(btn).toHaveText("COPIED");
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(text);
});

test("prose cells in a comparison table stay as they were", async ({ page }) => {
    await page.goto("/courses/bustub/concept/durability-and-fsync");
    const mixed = page.locator(".k-vt td", { hasText: "user-space buffer to the OS" });
    await expect(mixed.locator(".k-copy")).toHaveCount(0);
    await expect(mixed.locator("code")).toHaveCount(1);
    await expect(mixed.locator("code span")).toHaveCount(0);
});

test("code names in a plain table's first column are not broken mid-word", async ({ page }) => {
    await page.goto("/courses/bustub/concept/durability-and-fsync");
    const cells = page.locator(".k-vt:not(:has(.k-copy)) td:first-child code");
    await expect(cells.first()).toBeVisible();
    for (const h of await cells.evaluateAll((els) => els.map((e) => e.getBoundingClientRect().height))) expect(h).toBeLessThan(26);
});
