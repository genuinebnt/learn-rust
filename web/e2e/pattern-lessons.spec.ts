import { expect, test } from "@playwright/test";

// docs/DSA_LEARN_PAGE_SPEC.md: the Learn page of a pattern.

test("a technique card has its implementation on the left and its problems, in the lists or not, on the right", async ({ page }) => {
    await page.goto("/dsa/patterns/D11");
    await expect(page.getByRole("heading", { name: "Traversal", level: 2 })).toBeVisible();

    // one card, two versions of the template, each tab its own code
    const dfs = page.locator("#t-dfs");
    await expect(dfs.locator(".l-lft pre").first()).toContainText("def dfs_recursive");
    await dfs.getByRole("tab", { name: "ITERATIVE (EXPLICIT STACK)" }).click();
    await expect(dfs.locator(".l-lft pre").first()).toContainText("def dfs_iterative");
    // the traps are part of the implementation side, the problems are the right side only
    await expect(dfs.locator(".l-lft .l-pit")).toBeVisible();
    await expect(dfs.locator(".l-rgt .l-pit")).toHaveCount(0);
    expect(await dfs.locator(".l-rgt .pl").count()).toBeGreaterThanOrEqual(3);
});

test("every problem row carries difficulty, priority, the narrowest list (none outside the lists), companies and topics", async ({ page, request }) => {
    // a card that has problems outside the NeetCode lists
    const d = await (await request.get("/api/dsa/patterns/D2")).json();
    const withOutside = d.techniques.find((t: { problems: { list_tag: string | null }[] }) => t.problems.some((p) => p.list_tag === null));
    expect(withOutside, "Two Pointers has a technique with a problem outside the lists").toBeTruthy();
    await page.goto("/dsa/patterns/D2");
    const card = page.locator(`#t-${withOutside.id.split(":")[1]}`);
    const out = card.locator(".pl.pl-out").first();
    await expect(out).toBeVisible();
    await expect(out.locator(".d-lv")).toBeVisible();
    await expect(out.locator(".d-bdg").filter({ hasText: /^(MUST|STRONG|PRACTICE|WARM-UP)$/ })).toHaveCount(1);
    await expect(out.locator(".d-bdg.lst")).toHaveCount(0); // no list tag outside the lists
    expect(await out.locator(".pl-sub .d-co").count()).toBeGreaterThan(0);
    await expect(out.locator(".pl-topics")).not.toBeEmpty();
    // a list problem has exactly one list tag, the narrowest
    const inList = card.locator(".pl:not(.pl-out)").first();
    await expect(inList.locator(".d-bdg.lst")).toHaveCount(1);
});

test("a problem row opens the site's problem page, which links to LeetCode", async ({ page, request }) => {
    const d = await (await request.get("/api/dsa/patterns/D2")).json();
    const outside = d.techniques.flatMap((t: { problems: { list_tag: string | null; slug: string; title: string }[] }) => t.problems).find((p: { list_tag: string | null }) => p.list_tag === null);
    await page.goto("/dsa/patterns/D2");
    await page.locator(`.pl a[href="/d/${outside.slug}"]`).first().click();
    await expect(page).toHaveURL(new RegExp(`/d/${outside.slug}$`));
    await expect(page.getByRole("heading", { name: outside.title })).toBeVisible();
    await expect(page.locator(`a[href="https://leetcode.com/problems/${outside.slug}/"]`).first()).toBeVisible();
});

test("a technique with no problem is only named, at the bottom", async ({ page }) => {
    await page.goto("/dsa/patterns/D11");
    await expect(page.locator(".l-listed")).toHaveCount(0);
    const other = page.locator(".l-other");
    await expect(other).toBeVisible();
    await other.getByRole("button").click();
    await expect(other.locator(".l-onames li").first()).toBeVisible();
    // names only: nothing in it opens or links
    await expect(other.locator("a, button.l-lchip")).toHaveCount(0);
});

test("every problem of the site has companies and topic tags; the list tag is the narrowest list", async ({ request }) => {
    const o = await (await request.get("/api/dsa")).json();
    const problems = o.problems as { id: string; companies: unknown[]; tags: string[]; lists: string[]; list_tag: string | null; priority: string }[];
    // the only exceptions are the NeetCode-list problems no company of the site's set asks (content/dsa/no_company.txt)
    const noCompany = problems.filter((p) => p.companies.length === 0);
    expect(noCompany.length).toBeLessThanOrEqual(22);
    expect(noCompany.every((p) => p.lists.some((l) => l !== "practice")), "only list problems may lack a company").toBe(true);
    expect(problems.filter((p) => p.tags.length === 0)).toHaveLength(0);
    for (const p of problems) {
        const narrowest = (["blind75", "neetcode150", "neetcode250", "all"] as const).find((l) => p.lists.includes(l)) ?? null;
        expect(p.list_tag, p.id).toBe(narrowest);
        expect(["must", "strong", "practice", "warmup"]).toContain(p.priority);
    }
});

test("every topic's pattern page is grouped, and every technique shown has an implementation", async ({ request }) => {
    const overview = await (await request.get("/api/dsa")).json();
    expect(overview.patterns.length).toBe(18);
    for (const p of overview.patterns as { code: string; name: string }[]) {
        const d = await (await request.get(`/api/dsa/patterns/${p.code}`)).json();
        expect(d.groups?.length, `${p.name} declares sections`).toBeGreaterThan(0);
        for (const t of d.techniques as { id: string; lesson: { group?: string } | null; problems: unknown[] }[]) {
            // L4: a technique that has problems has an implementation
            if (t.problems.length > 0) expect(t.lesson, `${t.id} has problems, so it needs an implementation`).not.toBeNull();
            if (t.lesson?.group) expect(d.groups, `${p.name}: ${t.lesson.group}`).toContain(t.lesson.group);
        }
        // L5: no problem hangs off a section
        expect(d.group_problems).toBeUndefined();
        expect(d.group_tags).toBeUndefined();
    }
});

test("the Learn tab counts the techniques that are not taught by a NeetCode problem too", async ({ page, request }) => {
    const p = await (await request.get("/api/dsa/patterns/D11")).json();
    await page.goto("/dsa/patterns/D11");
    await expect(page.getByRole("tab", { name: /Learn/ })).toContainText(`${p.techniques.length + p.extras.length} techniques`);
});
