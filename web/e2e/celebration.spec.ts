import { readFileSync } from "node:fs";
import { expect, test, type APIRequestContext } from "@playwright/test";

const passing = (n: number) => ({
    stage_id: "4a-05",
    tests: Array.from({ length: n }, (_, i) => ({ name: `case_${i}`, ok: true, detail: "" })),
    commit: "abc1234f",
    duration_ms: 1500,
});
const report = (request: APIRequestContext, n = 4) => request.post("/api/courses/bustub/runs", { data: passing(n) });

test("a passing run opens the popup with the stats and the next stage; Stay here closes it", async ({ page, request }) => {
    await page.goto("/courses/bustub/4a-05");
    await expect(page.locator(".k-tabs")).toBeVisible();
    await report(request);
    const dialog = page.getByRole("dialog", { name: "Stage passed" });
    await expect(dialog).toBeVisible({ timeout: 15_000 });
    await expect(dialog).toContainText("4/4");
    await expect(dialog).toContainText("NEXT STAGE");
    await expect(dialog.getByRole("button", { name: /Go to next stage/ })).toBeFocused();
    await dialog.getByRole("button", { name: "Stay here" }).click();
    await expect(dialog).toBeHidden();
    await expect(page).toHaveURL(/\/courses\/bustub\/4a-05/);
});

test("Escape and a click outside close it, and focus returns to the page", async ({ page, request }) => {
    await page.goto("/courses/bustub/4a-05");
    await report(request, 5);
    const dialog = page.getByRole("dialog", { name: "Stage passed" });
    await expect(dialog).toBeVisible({ timeout: 15_000 });
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await report(request, 6);
    await expect(dialog).toBeVisible({ timeout: 15_000 });
    await page.mouse.click(5, 5);
    await expect(dialog).toBeHidden();
});

test("Go to next stage moves on", async ({ page, request }) => {
    await page.goto("/courses/bustub/4a-05");
    await report(request, 7);
    const dialog = page.getByRole("dialog", { name: "Stage passed" });
    await expect(dialog).toBeVisible({ timeout: 15_000 });
    await dialog.getByRole("button", { name: /Go to next stage/ }).click();
    await expect(page).toHaveURL(/\/courses\/bustub\/4a-06/);
});

test("Tab stays inside the popup", async ({ page, request }) => {
    await page.goto("/courses/bustub/4a-05");
    await report(request, 8);
    const dialog = page.getByRole("dialog", { name: "Stage passed" });
    await expect(dialog).toBeVisible({ timeout: 15_000 });
    for (let i = 0; i < 12; i++) {
        await page.keyboard.press("Tab");
        expect(await dialog.evaluate((d) => d.contains(document.activeElement))).toBe(true);
    }
});

test("with \"don't show again\" on, the next pass is a toast and the choice survives a reload", async ({ page, request }) => {
    await page.goto("/courses/bustub/4a-05");
    await report(request, 9);
    const dialog = page.getByRole("dialog", { name: "Stage passed" });
    await expect(dialog).toBeVisible({ timeout: 15_000 });
    await dialog.getByRole("switch", { name: "Don't show this again" }).click();
    await dialog.getByRole("button", { name: "Stay here" }).click();
    await page.reload();
    await expect(page.locator(".k-tabs")).toBeVisible();
    await report(request, 10);
    await expect(page.locator(".k-tt.k-ok")).toContainText("Tests passed", { timeout: 15_000 });
    await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("a failing run does not open the popup", async ({ page, request }) => {
    await page.goto("/courses/bustub/4a-03");
    await request.post("/api/courses/bustub/runs", { data: { stage_id: "4a-03", tests: [{ name: "x", ok: false, detail: "no" }], commit: "f00", duration_ms: 100 } });
    await expect(page.locator(".k-tt.k-er")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("the Rust workspace celebrates a solving Submit and offers the next problem", async ({ page, request }) => {
    test.setTimeout(180_000);
    const code = readFileSync("../content/tracks/l1-ownership-moves/problems/fix-use-after-move/solution.rs", "utf8");
    await request.put("/api/problems/l1-fix-use-after-move/draft", { data: { code } });
    await page.goto("/p/l1-fix-use-after-move");
    await expect(page.locator(".tstrip")).toBeVisible();
    await page.getByRole("button", { name: "Submit", exact: true }).click();
    const dialog = page.getByRole("dialog", { name: "Problem solved" });
    await expect(dialog).toBeVisible({ timeout: 150_000 });
    await expect(dialog).toContainText("hints");
    await dialog.getByRole("button", { name: "Next problem" }).click();
    await expect(page).toHaveURL(/\/p\/(?!l1-fix-use-after-move)/);
    await request.delete("/api/problems/l1-fix-use-after-move/draft");
});
