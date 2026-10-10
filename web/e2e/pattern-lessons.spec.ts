import { expect, test } from "@playwright/test";

test("a grouped pattern page shows its groups, version tabs, example-only lessons and listed techniques", async ({ page }) => {
    await page.goto("/dsa/patterns/D11");
    await expect(page.getByRole("heading", { name: "Traversal", level: 2 })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Topological sort and dependencies", level: 2 })).toBeVisible();

    // one card, two versions of the template
    const dfs = page.locator("#t-dfs");
    await expect(dfs).toContainText("EXAMPLES");
    await expect(dfs.locator("pre").first()).toContainText("def dfs_recursive");
    await dfs.getByRole("tab", { name: "ITERATIVE (EXPLICIT STACK)" }).click();
    await expect(dfs.locator("pre").first()).toContainText("def dfs_iterative");
    await expect(dfs.getByRole("tab", { name: "ITERATIVE (EXPLICIT STACK)" })).toHaveAttribute("aria-selected", "true");

    // its examples are problems from the lists and open the problem page
    await expect(dfs.locator(".l-prow")).toHaveCount(4);
    await expect(dfs.locator(".d-bdg.ex").first()).toHaveText("EXAMPLE");

    // techniques that are known and not written are listed, not hidden
    await expect(page.locator(".l-listed").first()).toContainText("LESSON NOT WRITTEN YET");
    // the jump list links to a card
    await page.locator(".l-jumpg a", { hasText: "Bidirectional BFS" }).click();
    await expect(page.locator("#t-bidir-bfs")).toBeInViewport();
});

test("a pattern without groups keeps the flat page", async ({ page }) => {
    await page.goto("/dsa/patterns/D1");
    await expect(page.locator(".l-jumpg")).toHaveCount(0);
    await expect(page.locator(".l-pat").first()).toBeVisible();
});

test("the Learn tab counts the lessons that have no must-learn problem too", async ({ page, request }) => {
    const p = await (await request.get("/api/dsa/patterns/D11")).json();
    await page.goto("/dsa/patterns/D11");
    await expect(page.getByRole("tab", { name: /Learn/ })).toContainText(`${p.techniques.length + p.extras.length} techniques`);
});
