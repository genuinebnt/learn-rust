import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
    await page.goto("/kit");
    await expect(page.getByRole("heading", { name: "Every control, one kit." })).toBeVisible();
});

test("a slider fills as it moves and shows its value", async ({ page }) => {
    const input = page.locator(".k-rng input").first();
    await input.fill("90");
    await expect(page.locator(".k-rng b").first()).toHaveText("90 min");
    expect(await input.evaluate((e) => (e as HTMLElement).style.getPropertyValue("--v"))).toBe("100%");
});

test("Submit before a passing run shakes and says why; after one it opens the popup", async ({ page }) => {
    await page.locator(".k-acts2").getByRole("button", { name: /^Submit/ }).click();
    await expect(page.locator(".k-tt")).toContainText("Run the tests first");
    await page.locator(".k-acts2").getByRole("button", { name: /^Run tests/ }).click();
    await expect(page.locator(".k-big")).toHaveText("5 of 5 passed", { timeout: 10_000 });
    await page.locator(".k-acts2").getByRole("button", { name: /^Submit/ }).click();
    await expect(page.getByRole("dialog", { name: "Stage passed" })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("the popover opens and a click outside closes it", async ({ page }) => {
    await page.getByRole("button", { name: /Popover menu/ }).click();
    await expect(page.locator(".k-pop.k-on")).toBeVisible();
    await page.mouse.click(5, 300);
    await expect(page.locator(".k-pop.k-on")).toHaveCount(0);
});

test("a toast appears, and can be closed", async ({ page }) => {
    await page.getByRole("button", { name: "Success toast" }).click();
    await expect(page.locator(".k-tt.k-ok")).toBeVisible();
});
