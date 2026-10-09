import { expect, test, type Page } from "@playwright/test";

const stage = "/courses/bustub/4a-04";
const width = async (page: Page, sel: string) => Math.round((await page.locator(sel).boundingBox())!.width);

test.beforeEach(async ({ page }) => {
    await page.goto(stage);
    await expect(page.locator(".cx-tabs")).toBeVisible();
});

test("the panels start wide: the course panel about 320px, the page panel about 300px", async ({ page }) => {
    expect(await width(page, ".cx-side")).toBeGreaterThan(300);
    expect(await width(page, ".cx-side")).toBeLessThan(345);
    expect(await width(page, ".cx-toc")).toBeGreaterThan(280);
    expect(await width(page, ".cx-toc")).toBeLessThan(325);
});

test("the tree opens on the current stage and scrolls it into view", async ({ page }) => {
    await expect(page.locator(".cx-leaf.cur")).toBeVisible();
    await expect(page.locator(".cx-leaf.cur")).toHaveAttribute("aria-current", "page");
});

test("dragging the edge resizes a panel, it is remembered, and a double-click resets it", async ({ page }) => {
    const handle = page.locator(".cx-rz.l");
    const box = (await handle.boundingBox())!;
    await page.mouse.move(box.x + 4, box.y + 200);
    await page.mouse.down();
    await page.mouse.move(box.x + 4 + 70, box.y + 200, { steps: 6 });
    await page.mouse.up();
    await expect.poll(() => width(page, ".cx-side")).toBeGreaterThan(375);
    await page.reload();
    await expect(page.locator(".cx-side")).toBeVisible();
    expect(await width(page, ".cx-side")).toBeGreaterThan(375);
    await page.locator(".cx-rz.l").dblclick();
    await expect.poll(() => width(page, ".cx-side")).toBeLessThan(345);
});

test("a panel never gets narrower than its minimum", async ({ page }) => {
    const box = (await page.locator(".cx-rz.l").boundingBox())!;
    await page.mouse.move(box.x + 4, box.y + 200);
    await page.mouse.down();
    await page.mouse.move(box.x - 400, box.y + 200, { steps: 8 });
    await page.mouse.up();
    expect(await width(page, ".cx-side")).toBeGreaterThanOrEqual(258);
});

test("the course panel collapses to a rail of stage dots and comes back; the choice survives a reload", async ({ page }) => {
    await page.getByRole("button", { name: "Collapse the course panel" }).click();
    await expect(page.locator(".cx-side.rail")).toBeVisible();
    await expect.poll(() => width(page, ".cx-side")).toBeLessThan(90);
    await expect(page.locator(".cx-rdot")).toHaveCount(9);
    await page.reload();
    await expect(page.locator(".cx-side.rail")).toBeVisible();
    await page.getByRole("button", { name: "Show the course panel" }).click();
    await expect(page.locator(".cx-side.rail")).toHaveCount(0);
    await expect.poll(() => width(page, ".cx-side")).toBeGreaterThan(300);
});

test("the page panel hides and a button in the header brings it back", async ({ page }) => {
    await page.getByRole("button", { name: "Hide the page panel" }).click();
    await expect(page.locator(".cx-toc")).toBeHidden();
    await page.getByRole("button", { name: "Show the page panel" }).click();
    await expect(page.locator(".cx-toc")).toBeVisible();
});

test("Ctrl+B and Ctrl+. toggle the panels", async ({ page }) => {
    await page.keyboard.press("Control+b");
    await expect(page.locator(".cx-side.rail")).toBeVisible();
    await page.keyboard.press("Control+b");
    await expect(page.locator(".cx-side.rail")).toHaveCount(0);
    await page.keyboard.press("Control+.");
    await expect(page.locator(".cx-toc")).toBeHidden();
});

test("filtering the tree shows only the matching stages, with their modules open", async ({ page }) => {
    await page.getByLabel("Filter stages").fill("watermark");
    await expect(page.locator(".cx-leaf")).toHaveCount(1);
    await expect(page.locator(".cx-leaf")).toContainText("watermark");
    await page.getByLabel("Filter stages").fill("zzzz-nothing");
    await expect(page.locator(".cx-snone")).toBeVisible();
});

test("a module row opens and closes its stages", async ({ page }) => {
    const row = page.locator(".cx-mrow", { hasText: "1A" });
    await expect(row).toHaveAttribute("aria-expanded", "false");
    await row.click();
    await expect(row).toHaveAttribute("aria-expanded", "true");
    await expect(page.locator(".cx-leaf", { hasText: "Open the database file" })).toBeVisible();
});

test("the page panel lists the concepts and links to them", async ({ page }) => {
    const first = page.locator(".cx-toc a.cx-crow").first();
    await expect(first).toContainText("min read");
    await first.click();
    await expect(page).toHaveURL(/\/courses\/bustub\/concept\//);
});

test("the stage card shows the command, the last run and the hints used", async ({ page }) => {
    const card = page.locator(".cx-card", { hasText: "THIS STAGE" });
    await expect(card).toContainText("anneal course test 4a-04");
    await expect(card).toContainText("Last run");
    await expect(card).toContainText("Hints used");
});

test.describe("on a phone", () => {
    test.use({ viewport: { width: 420, height: 880 } });

    test("the panels are drawers: hidden, opened from the bar, closed by Escape or the backdrop", async ({ page }) => {
        await expect(page.locator(".cx-side")).toBeHidden();
        await expect(page.locator(".cx-toc")).toBeHidden();
        await page.getByRole("button", { name: /Stages/ }).click();
        await expect(page.locator(".cx-side")).toBeVisible();
        await page.keyboard.press("Escape");
        await expect(page.locator(".cx-side")).toBeHidden();
        await page.getByRole("button", { name: /This page/ }).click();
        await expect(page.locator(".cx-toc")).toBeVisible();
        await expect(page.locator(".cx-focus")).toBeVisible();
        await page.mouse.click(10, 400);
        await expect(page.locator(".cx-toc")).toBeHidden();
    });

    test("choosing a stage in the drawer goes there and closes it", async ({ page }) => {
        await page.getByRole("button", { name: /Stages/ }).click();
        await page.locator(".cx-leaf", { hasText: "Scanning with versions" }).click();
        await expect(page).toHaveURL(/4a-08/);
        await expect(page.locator(".cx-side")).toBeHidden();
    });

    test("there is no horizontal scroll", async ({ page }) => {
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
    });
});

test("the tree's project rows keep their own look, not the course map's buttons", async ({ page }) => {
    const row = page.locator(".cx-tree a.cx-node").first();
    await expect(row).toBeVisible();
    expect(await row.evaluate((e) => getComputedStyle(e).borderTopWidth)).toBe("0px");
    expect(await row.evaluate((e) => Math.round(e.getBoundingClientRect().height))).toBeLessThan(40);
});
