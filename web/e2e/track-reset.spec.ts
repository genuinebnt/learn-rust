import { expect, test } from "@playwright/test";

test("a track page can forget its progress after you type reset", async ({ page, request }) => {
    const track = await (await request.get("/api/tracks")).json();
    const slug: string = (Array.isArray(track) ? track : track.tracks).find((t: { ready: number }) => t.ready > 0).slug;
    await page.goto(`/t/${slug}`);
    await page.getByRole("button", { name: "Reset progress" }).click();
    const panel = page.getByRole("group", { name: "Reset progress" });
    const go = panel.getByRole("button", { name: "Reset progress" });
    await expect(go).toBeDisabled();
    await panel.getByPlaceholder("reset").fill("reset");
    await go.click();
    await expect(page.locator("text=Progress reset").first()).toBeVisible();
    await expect(panel).toHaveCount(0);
});

test("a DSA pattern page can forget its progress too", async ({ page }) => {
    await page.goto("/dsa/patterns/D1");
    await page.getByRole("button", { name: "Reset progress" }).click();
    const panel = page.getByRole("group", { name: "Reset progress" });
    const go = panel.getByRole("button", { name: "Reset progress" });
    await expect(go).toBeDisabled();
    await panel.getByPlaceholder("reset").fill("reset");
    await go.click();
    await expect(panel).toHaveCount(0);
});
