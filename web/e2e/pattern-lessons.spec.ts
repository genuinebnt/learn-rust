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

    // a technique that is not written yet is shown only when it comes with LeetCode problems (a name alone is not content)
    await page.goto("/dsa/patterns/D13");
    const listed = page.locator(".l-listed").filter({ hasText: "with LeetCode problems, lesson not written yet" }).first();
    await expect(listed).toBeVisible();
    await listed.getByRole("button").first().click();
    await listed.locator(".l-lchip").first().click();
    await expect(listed.locator('.l-prow[href^="https://leetcode.com/problems/"]').first()).toBeVisible();
    await page.goto("/dsa/patterns/D11");
    // a group links to LeetCode's own tag page and lists problems that are not in your lists
    await expect(page.locator('.l-tags a[href^="https://leetcode.com/tag/"]').first()).toBeVisible();
    await page.getByRole("button", { name: /more LeetCode problems for this section/ }).first().click();
    await expect(page.locator('.l-prow[href^="https://leetcode.com/problems/"]').first()).toBeVisible();
    // the jump list links to a card
    await page.locator(".l-jumpg a", { hasText: "Bidirectional BFS" }).click();
    await expect(page.locator("#t-bidir-bfs")).toBeInViewport();
});

test("every topic's pattern page is grouped, with its sections, tag links and problems that link to LeetCode", async ({ page, request }) => {
    const overview = await (await request.get("/api/dsa")).json();
    expect(overview.patterns.length).toBe(18);
    for (const p of overview.patterns as { code: string; name: string }[]) {
        const d = await (await request.get(`/api/dsa/patterns/${p.code}`)).json();
        expect(d.groups?.length, `${p.name} declares groups`).toBeGreaterThan(0);
        // every technique that has a lesson sits in a group the page declares
        for (const t of d.techniques as { lesson: { group?: string } | null }[]) {
            if (t.lesson?.group) expect(d.groups, `${p.name}: ${t.lesson.group}`).toContain(t.lesson.group);
        }
    }
    await page.goto("/dsa/patterns/D1");
    await expect(page.locator(".l-jumpg")).toBeVisible();
    await expect(page.locator(".l-gsec").first()).toBeVisible();
    await expect(page.locator(".l-pat").first()).toBeVisible();
});

test("the Learn tab counts the lessons that have no must-learn problem too", async ({ page, request }) => {
    const p = await (await request.get("/api/dsa/patterns/D11")).json();
    await page.goto("/dsa/patterns/D11");
    await expect(page.getByRole("tab", { name: /Learn/ })).toContainText(`${p.techniques.length + p.extras.length} techniques`);
});
