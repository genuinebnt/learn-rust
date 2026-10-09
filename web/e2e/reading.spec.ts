import { expect, test } from "@playwright/test";

const stage = "/courses/bustub/4a-04";

test.beforeEach(async ({ page }) => {
    await page.goto(stage);
    await expect(page.locator(".cx-tabs")).toBeVisible();
});

test.describe("sidenotes", () => {
    test("the markers are numbered in order and the notes are listed in the page panel", async ({ page }) => {
        await expect(page.locator(".cx-col .cx-snm")).toHaveCount(2);
        await expect(page.locator(".cx-col .cx-snm").nth(0)).toHaveText("1");
        await expect(page.locator(".cx-col .cx-snm").nth(1)).toHaveText("2");
        await expect(page.locator(".cx-pnote")).toHaveCount(2);
        await expect(page.locator(".cx-pnote").first()).toContainText("An undo log is stored next to the table");
    });

    test("clicking a marker selects its note in the panel, and clicking again lets go", async ({ page }) => {
        await page.locator(".cx-col .cx-snm").nth(1).click();
        await expect(page.locator('.cx-pnote[data-sn="2"]')).toHaveClass(/sel/);
        await page.locator(".cx-col .cx-snm").nth(1).click();
        await expect(page.locator('.cx-pnote[data-sn="2"]')).not.toHaveClass(/sel/);
    });

    test("clicking a note in the panel selects it too", async ({ page }) => {
        await page.locator('.cx-pnote[data-sn="1"]').click();
        await expect(page.locator('.cx-pnote[data-sn="1"]')).toHaveClass(/sel/);
    });

    test("the note for the text in view stands out", async ({ page }) => {
        // nothing is current while the text is still below the reading line; scrolled into view, the last marker above it is
        await expect(page.locator(".cx-pnote.cur")).toHaveCount(0);
        await page.evaluate(() => window.scrollTo(0, 250));
        await expect(page.locator(".cx-pnote.cur")).toHaveCount(1);
        await expect(page.locator('.cx-pnote[data-sn="2"]')).toHaveClass(/cur/);
    });

    test("with the page panel hidden, a marker opens its note under the paragraph", async ({ page }) => {
        await page.getByRole("button", { name: "Hide the page panel" }).click();
        const marker = page.locator(".cx-col .cx-snm").first();
        await marker.click();
        await expect(page.locator(".cx-snb.open")).toContainText("An undo log is stored next to the table");
        await expect(marker).toHaveAttribute("aria-expanded", "true");
        await marker.click();
        await expect(page.locator(".cx-snb.open")).toHaveCount(0);
    });

    test("a marker works from the keyboard", async ({ page }) => {
        await page.getByRole("button", { name: "Hide the page panel" }).click();
        await page.locator(".cx-col .cx-snm").first().focus();
        await page.keyboard.press("Enter");
        await expect(page.locator(".cx-snb.open")).toHaveCount(1);
    });

    test.describe("on a phone", () => {
        test.use({ viewport: { width: 420, height: 880 } });
        test("the note opens under the paragraph", async ({ page }) => {
            await page.locator(".cx-col .cx-snm").first().click();
            await expect(page.locator(".cx-snb.open")).toBeVisible();
        });
    });
});

test.describe("asides", () => {
    test("an aside starts closed, opens on a click and holds code", async ({ page }) => {
        const aside = page.locator("details.cx-k-aside", { hasText: "Why not rebuild the tuple after every log?" });
        await expect(aside).toBeVisible();
        await expect(aside).not.toHaveAttribute("open", "");
        await expect(aside.locator(".cx-co-b")).toBeHidden();
        await aside.locator("summary").click();
        await expect(aside.locator(".cx-co-b")).toBeVisible();
        await expect(aside.locator(".cx-hl")).toBeVisible();
        await expect(aside.locator(".cx-hl")).toContainText("Tuple::new(values, schema)");
        await aside.locator("summary").click();
        await expect(aside.locator(".cx-co-b")).toBeHidden();
    });
});

test.describe("optional sections", () => {
    test("Performance and Learn more are marked optional and shown by default", async ({ page }) => {
        await expect(page.locator(".cx-oh")).toHaveCount(2);
        await expect(page.locator(".cx-obody.shut")).toHaveCount(0);
    });

    test("one can be hidden on its own and shown again", async ({ page }) => {
        const sec = page.locator("#sec-performance");
        await sec.getByRole("button", { name: "HIDE" }).click();
        await expect(sec.locator(".cx-obody")).toHaveClass(/shut/);
        await expect(page.locator("#sec-learn-more .cx-obody")).not.toHaveClass(/shut/);
        await sec.getByRole("button", { name: "SHOW" }).click();
        await expect(sec.locator(".cx-obody")).not.toHaveClass(/shut/);
    });

    test("hide all optional sections is remembered, and going to a hidden one opens it", async ({ page }) => {
        await page.getByRole("button", { name: "HIDE OPTIONAL SECTIONS" }).click();
        await expect(page.locator(".cx-obody.shut")).toHaveCount(2);
        await page.reload();
        await expect(page.locator(".cx-obody.shut")).toHaveCount(2);
        await page.locator(".cx-outline a", { hasText: "Performance" }).click();
        await expect(page.locator("#sec-performance .cx-obody")).not.toHaveClass(/shut/);
        await page.getByRole("button", { name: "SHOW OPTIONAL SECTIONS" }).click();
        await expect(page.locator(".cx-obody.shut")).toHaveCount(0);
    });

    test("hidden content cannot be tabbed into", async ({ page }) => {
        await page.getByRole("button", { name: "HIDE OPTIONAL SECTIONS" }).click();
        expect(await page.locator("#sec-performance div[inert]").count()).toBe(1);
    });
});

test.describe("code blocks", () => {
    test("a long example starts folded; show all unfolds it and the copy button still copies it all", async ({ page, context }) => {
        await context.grantPermissions(["clipboard-read", "clipboard-write"]);
        await page.goto("/courses/bustub/concept/durability-and-fsync");
        // pick the block by its fold button, which stays after it unfolds (".cx-fold" would then match the next block)
        const fig = page.locator(".cx-hl").filter({ has: page.locator(".cx-more") }).first();
        await expect(fig).toBeVisible();
        const lines = await fig.locator(".cx-more").getAttribute("data-lines");
        expect(Number(lines)).toBeGreaterThan(18);
        expect(await fig.locator("pre").evaluate((e) => e.getBoundingClientRect().height)).toBeLessThan(340);
        await fig.locator(".cx-more").click();
        await expect(fig).not.toHaveClass(/cx-fold/);
        await expect(fig.locator(".cx-more")).toHaveText("show less");
        await fig.locator(".cx-copy").click();
        const copied = await page.evaluate(() => navigator.clipboard.readText());
        expect(copied.split("\n").length).toBe(Number(lines));
        await fig.locator(".cx-more").click();
        await expect(fig).toHaveClass(/cx-fold/);
    });

    test("a short example is not folded", async ({ page }) => {
        await expect(page.locator(".cx-hl:not(.cx-fold)").first()).toBeVisible();
        expect(await page.locator(".cx-more").count()).toBe(0);
    });
});
