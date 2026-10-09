import { expect, test } from "@playwright/test";

const stage = "/courses/bustub/4a-04";

test.beforeEach(async ({ page }) => {
    await page.goto(stage);
    await expect(page.locator(".k-tabs")).toBeVisible();
});

test.describe("sidenotes", () => {
    test("the markers are numbered in order and the notes are listed in the page panel", async ({ page }) => {
        await expect(page.locator(".k-read2 .k-snm")).toHaveCount(2);
        await expect(page.locator(".k-read2 .k-snm").nth(0)).toHaveText("1");
        await expect(page.locator(".k-read2 .k-snm").nth(1)).toHaveText("2");
        await expect(page.locator(".k-pnote")).toHaveCount(2);
        await expect(page.locator(".k-pnote").first()).toContainText("An undo log is stored next to the table");
    });

    test("clicking a marker selects its note in the panel, and clicking again lets go", async ({ page }) => {
        await page.locator(".k-read2 .k-snm").nth(1).click();
        await expect(page.locator('.k-pnote[data-sn="2"]')).toHaveClass(/k-sel/);
        await page.locator(".k-read2 .k-snm").nth(1).click();
        await expect(page.locator('.k-pnote[data-sn="2"]')).not.toHaveClass(/k-sel/);
    });

    test("clicking a note in the panel selects it too", async ({ page }) => {
        await page.locator('.k-pnote[data-sn="1"] .k-pb2').click();
        await expect(page.locator('.k-pnote[data-sn="1"]')).toHaveClass(/k-sel/);
    });

    test("the note for the text in view stands out", async ({ page }) => {
        // at the top the first paragraph's note is current; scrolled on, the next paragraph's is
        await expect(page.locator('.k-pnote[data-sn="1"]')).toHaveClass(/k-cur/);
        await page.evaluate(() => window.scrollTo(0, 250));
        await expect(page.locator('.k-pnote[data-sn="2"]')).toHaveClass(/k-cur/);
    });

    test("a note in the panel can show its place in the text", async ({ page }) => {
        await page.locator('.k-pnote[data-sn="2"] [data-show]').click();
        await expect(page.locator('.k-read2 .k-sn[data-sn="2"]')).toHaveClass(/k-open/);
    });

    test("with the page panel hidden, a marker opens its note under the paragraph", async ({ page }) => {
        await page.getByRole("button", { name: "Hide sidebar" }).click();
        const marker = page.locator(".k-read2 .k-snm").first();
        await marker.click();
        await expect(page.locator(".k-sn.k-open")).toContainText("An undo log is stored next to the table");
        await expect(marker).toHaveAttribute("aria-expanded", "true");
        await marker.click();
        await expect(page.locator(".k-sn.k-open")).toHaveCount(0);
    });

    test("a marker works from the keyboard", async ({ page }) => {
        await page.getByRole("button", { name: "Hide sidebar" }).click();
        await page.locator(".k-read2 .k-snm").first().focus();
        await page.keyboard.press("Enter");
        await expect(page.locator(".k-sn.k-open")).toHaveCount(1);
    });

    test.describe("on a phone", () => {
        test.use({ viewport: { width: 420, height: 880 } });
        test("the note opens under the paragraph", async ({ page }) => {
            await page.locator(".k-read2 .k-snm").first().click();
            await expect(page.locator(".k-sn.k-open")).toBeVisible();
        });
    });
});

test.describe("asides", () => {
    test("an aside starts closed, opens on a click and holds code", async ({ page }) => {
        const aside = page.locator(".k-asd", { hasText: "Why not rebuild the tuple after every log?" });
        await expect(aside).toBeVisible();
        await expect(aside).not.toHaveClass(/k-open/);
        await expect(aside.locator(".k-ah")).toHaveAttribute("aria-expanded", "false");
        await aside.locator(".k-ah").click();
        await expect(aside).toHaveClass(/k-open/);
        await expect(aside.locator(".k-in3")).toBeVisible();
        await expect(aside.locator(".k-code")).toContainText("Tuple::new(values, schema)");
        await aside.locator(".k-ah").click();
        await expect(aside).not.toHaveClass(/k-open/);
    });
});

test.describe("optional sections", () => {
    test("Performance and Learn more are marked optional and shown by default", async ({ page }) => {
        await expect(page.locator(".k-opt .k-oh")).toHaveCount(2);
        await expect(page.locator(".k-opt.k-hid")).toHaveCount(0);
    });

    test("one opens on its own and closes again", async ({ page }) => {
        const sec = page.locator("#sec-performance");
        await expect(sec).not.toHaveClass(/k-open/);
        await sec.locator(".k-oh").click();
        await expect(sec).toHaveClass(/k-open/);
        await expect(page.locator("#sec-learn-more")).not.toHaveClass(/k-open/);
        await sec.locator(".k-oh").click();
        await expect(sec).not.toHaveClass(/k-open/);
    });

    test("hide all optional sections is remembered, and going to a hidden one opens it", async ({ page }) => {
        await page.getByRole("button", { name: "Hide optional sections" }).click();
        await expect(page.locator(".k-opt.k-hid")).toHaveCount(2);
        await page.reload();
        await expect(page.locator(".k-opt.k-hid")).toHaveCount(2);
        await page.locator("#toc a", { hasText: "Performance" }).click();
        await expect(page.locator("#sec-performance")).not.toHaveClass(/k-hid/);
        await expect(page.locator("#sec-performance")).toHaveClass(/k-open/);
        await page.getByRole("button", { name: "Show optional sections" }).click();
        await expect(page.locator(".k-opt.k-hid")).toHaveCount(0);
    });

    test("closed content cannot be tabbed into", async ({ page }) => {
        expect(await page.locator("#sec-performance div[inert]").count()).toBeGreaterThan(0);
        await page.locator("#sec-performance .k-oh").click();
        await expect(page.locator("#sec-performance .k-ob > div")).not.toHaveAttribute("inert", "");
    });
});

test.describe("code blocks", () => {
    test("a long example starts folded; show all unfolds it and the copy button still copies it all", async ({ page, context }) => {
        await context.grantPermissions(["clipboard-read", "clipboard-write"]);
        await page.goto("/courses/bustub/concept/durability-and-fsync");
        const fig = page.locator(".k-code.k-folded").first();
        await expect(fig).toBeVisible();
        const lines = await fig.locator(".k-more").getAttribute("data-lines");
        expect(Number(lines)).toBeGreaterThan(12);
        expect(await fig.locator(".k-cb").evaluate((e) => e.getBoundingClientRect().height)).toBeLessThan(340);
        await fig.locator(".k-more").click();
        await expect(fig.locator(".k-cb")).not.toHaveClass(/k-fold/);
        await expect(fig.locator(".k-more")).toContainText("SHOW LESS");
        await fig.locator(".k-ch .k-copy").click();
        const copied = await page.evaluate(() => navigator.clipboard.readText());
        expect(copied.split("\n").length).toBe(Number(lines));
        await fig.locator(".k-more").click();
        await expect(fig.locator(".k-cb")).toHaveClass(/k-fold/);
    });

    test("line numbers are a column next to the code, one number per line", async ({ page }) => {
        await page.goto("/courses/bustub/concept/durability-and-fsync");
        const cb = page.locator(".k-cb").first();
        const [numbers, lines, gutter, code] = await cb.evaluate((el) => [
            el.querySelectorAll(".k-ln span").length,
            el.querySelectorAll("pre .k-l, pre .k-hl, pre .k-del").length,
            el.querySelector(".k-ln")!.getBoundingClientRect().height,
            el.querySelector("pre")!.getBoundingClientRect().height,
        ]);
        expect(numbers).toBe(lines);
        expect(numbers).toBeGreaterThan(2);
        expect(Math.abs(gutter - code)).toBeLessThan(30); // the same height: the numbers do not run together in one line
    });

    test("a short example is not folded", async ({ page }) => {
        await expect(page.locator(".k-code:not(.k-folded)").first()).toBeVisible();
        expect(await page.locator(".k-more").count()).toBe(0);
    });
});

test.describe("check yourself and the steps aside", () => {
    test("a question hides its answer until you click it, and nudges come one at a time", async ({ page }) => {
        await page.goto("/courses/bustub/1a-02");
        const box = page.locator(".k-rev2").first();
        await expect(box).toBeVisible();
        const spoil = box.locator(".k-spoil");
        await expect(spoil).toHaveAttribute("aria-pressed", "false");
        await box.getByRole("button", { name: /Need a nudge/ }).click();
        await expect(box.locator(".k-nudge")).toContainText("delete_page");
        await expect(box.locator(".k-st2.k-on")).toHaveCount(1);
        await box.getByRole("button", { name: /Another nudge/ }).click();
        await expect(box.locator(".k-st2.k-on")).toHaveCount(2);
        await spoil.click();
        await expect(spoil).toHaveAttribute("aria-pressed", "true");
        await expect(spoil).toContainText("the file does not grow");
    });

    test("a task's steps are in a closed aside, with the contract above them", async ({ page }) => {
        await page.goto("/courses/bustub/2c-04");
        const aside = page.locator(".k-asd", { hasText: "if you would rather not work them out" });
        await expect(aside).toBeVisible();
        await expect(aside).not.toHaveClass(/k-open/);
        await expect(page.locator(".k-task", { hasText: "two leaves hold the same pairs" })).toBeVisible();
        await aside.locator(".k-ah").click();
        await expect(aside.locator("ol li")).toHaveCount(4);
    });
});
