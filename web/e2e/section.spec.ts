import { expect, test } from "@playwright/test";

// The section page shared by the Rust area; the DSA home is its own page.
for (const area of ["rust"] as const) {
    test.describe(`/${area}`, () => {
        test.beforeEach(async ({ page }) => {
            await page.goto(`/${area}`);
            await expect(page.locator(".tcard").first()).toBeVisible();
        });

        test("the numbers count up to the real ones", async ({ page }) => {
            const tracks = page.locator(".cat-stats b").first();
            const cards = await page.locator(".tcard").count();
            await expect(tracks).toHaveText(String(cards), { timeout: 5000 });
            await expect(page.locator(".cat-stats b").nth(1)).not.toHaveText("0");
            await expect(page.locator(".cat-stats b").nth(2)).toHaveText(/^~\d/);
        });

        test("the cards and the page rise in and end fully visible", async ({ page }) => {
            const first = page.locator(".tcard").first();
            expect(await first.evaluate((e) => getComputedStyle(e).animationName)).toBe("cat-rise");
            await expect.poll(() => first.evaluate((e) => getComputedStyle(e).opacity), { timeout: 5000 }).toBe("1");
            await expect.poll(() => page.locator(".tcard").last().evaluate((e) => getComputedStyle(e).opacity), { timeout: 8000 }).toBe("1");
        });

        test("the view toggle has a thumb that slides to list and back", async ({ page }) => {
            const seg = page.locator(".seg.slide");
            expect(await seg.evaluate((e) => getComputedStyle(e).getPropertyValue("--i").trim())).toBe("0");
            await seg.getByRole("button", { name: /list/ }).click();
            await expect(page.locator(".tlist").first()).toBeVisible();
            expect(await seg.evaluate((e) => getComputedStyle(e).getPropertyValue("--i").trim())).toBe("1");
            await seg.getByRole("button", { name: /grid/ }).click();
            await expect(page.locator(".tgrid").first()).toBeVisible();
        });

        test("a card gets a light that follows the pointer", async ({ page }) => {
            const card = page.locator(".tcard:not(.planned)").first();
            await card.scrollIntoViewIfNeeded();
            const box = (await card.boundingBox())!;
            await page.mouse.move(box.x + 40, box.y + 30);
            await page.mouse.move(box.x + 120, box.y + 60);
            await expect.poll(() => card.evaluate((e) => (e as HTMLElement).style.getPropertyValue("--mx"))).toMatch(/^1[12]\dpx$|^\d+(\.\d+)?px$/);
            expect(await card.evaluate((e) => getComputedStyle(e, "::after").opacity)).not.toBe("");
        });

        test("search narrows the cards, the empty state offers a way back, and / focuses the box", async ({ page }) => {
            await page.keyboard.press("/");
            await expect(page.getByLabel("Search tracks")).toBeFocused();
            const all = await page.locator(".tcard").count();
            await page.getByLabel("Search tracks").fill("zzzz-nothing-here");
            await expect(page.getByText("No tracks match")).toBeVisible();
            await page.getByRole("button", { name: /clear/i }).first().click();
            await expect(page.locator(".tcard")).toHaveCount(all);
        });

        test("a filter chip shows only its tracks and the all chip restores them", async ({ page }) => {
            const all = await page.locator(".tcard").count();
            const chips = page.locator(".fchip");
            const n = await chips.count();
            expect(n).toBeGreaterThan(2);
            await chips.nth(1).click();
            await expect(chips.nth(1)).toHaveAttribute("aria-pressed", "true");
            expect(await page.locator(".tcard").count()).toBeLessThanOrEqual(all);
            await chips.first().click();
            await expect(page.locator(".tcard")).toHaveCount(all);
        });

        test("pressing a card's button spreads a ripple", async ({ page }) => {
            const go = page.locator(".tc-go").first();
            await go.scrollIntoViewIfNeeded();
            await page.evaluate(() => document.addEventListener("click", (e) => e.preventDefault(), true)); // stay on the page
            await go.dispatchEvent("pointerdown", { clientX: 5, clientY: 5, bubbles: true });
            await expect(go.locator(".fx-rip")).toHaveCount(1);
        });
    });
}

test.describe("reduced motion", () => {
    test.use({ contextOptions: { reducedMotion: "reduce" } });
    test("nothing animates and the numbers are final at once", async ({ page }) => {
        await page.goto("/rust");
        const card = page.locator(".tcard").first();
        await expect(card).toBeVisible();
        expect(await card.evaluate((e) => getComputedStyle(e).animationName)).toBe("none");
        const cards = await page.locator(".tcard").count();
        await expect(page.locator(".cat-stats b").first()).toHaveText(String(cards), { timeout: 1000 });
    });
});
