import { expect, test } from "@playwright/test";

test("the header shows the area you are in and the pages of that area", async ({ page }) => {
    await page.goto("/courses");
    const areas = page.getByRole("navigation", { name: "Areas" }).first();
    await expect(areas.getByRole("link", { name: /Courses/ })).toHaveAttribute("aria-current", "page");
    await expect(page.locator(".hd-tabs a.on")).toHaveText("BusTub");
    await expect(page.locator(".hd-crumb")).toHaveCount(0); // the tab already says where you are
    await areas.getByRole("link", { name: /DSA/ }).click();
    await expect(page).toHaveURL(/\/dsa$/);
    await expect(page.locator(".hd-tabs a", { hasText: "Mock interview" })).toBeVisible();
    await expect(page.locator(".hd-tabs a.on")).toHaveText(/Problems/);
});

test("a stage page adds a crumb to the area", async ({ page }) => {
    await page.goto("/courses/bustub/1a-01");
    await expect(page.locator(".hd-crumb")).toContainText("1a-01");
});

test("search opens with Ctrl+K, filters by name, opens a result with Enter and closes with Escape", async ({ page }) => {
    await page.goto("/dsa");
    await page.keyboard.press("Control+k");
    const box = page.getByRole("dialog", { name: "Search" });
    await expect(box).toBeVisible();
    await box.getByRole("textbox").fill("3i-04");
    await expect(box.getByRole("option").first()).toContainText("3i-04");
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/\/courses\/bustub\/3i-04$/);
    await page.keyboard.press("Control+k");
    await expect(box).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(box).toHaveCount(0);
});

test("the page width option widens the main screens and is remembered; reading screens keep their width", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 900 });
    await page.goto("/courses");
    const main = page.locator(".k-wrap").first();
    const narrow = (await main.boundingBox())!.width;
    expect(narrow).toBeLessThanOrEqual(1240);
    await page.locator(".acct .av").click();
    await page.getByRole("radio", { name: "Wide" }).click();
    await expect.poll(async () => (await main.boundingBox())!.width).toBeGreaterThan(narrow + 200);
    await page.reload();
    await expect.poll(async () => (await page.locator(".k-wrap").first().boundingBox())!.width).toBeGreaterThan(narrow + 200);
    // a reading screen keeps its measure
    await page.goto("/courses/bustub/1a-01");
    const read = page.locator(".k-read2").first();
    await expect(read).toBeVisible();
    expect((await read.boundingBox())!.width).toBeLessThanOrEqual(1040);
    await page.locator(".acct .av").click();
    await page.getByRole("radio", { name: "Narrow" }).click();
    await page.goto("/courses");
    await expect.poll(async () => (await page.locator(".k-wrap").first().boundingBox())!.width).toBeLessThanOrEqual(1240);
});

test("on a phone the areas are a bar at the bottom", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 800 });
    await page.goto("/courses");
    const dock = page.locator(".hd-dock");
    await expect(dock).toBeVisible();
    await expect(dock.getByRole("link", { name: /Courses/ })).toHaveAttribute("aria-current", "page");
    await expect(page.locator(".hd-areas")).toBeHidden();
});
