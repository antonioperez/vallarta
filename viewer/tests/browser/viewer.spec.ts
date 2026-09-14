import { test, expect, type Page } from "@playwright/test";

async function openViewer(page: Page) {
  await page.goto("./");
  await expect(page.locator("#scene")).toHaveAttribute(
    "data-textures",
    "ready",
    { timeout: 30_000 },
  );
}

test("renders the model and excludes the static document from indexing", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await openViewer(page);
  await expect(page.locator("#scene")).toHaveAttribute("data-ready", "true");
  expect(
    Number(await page.locator("#scene").getAttribute("data-draw-calls")),
  ).toBeGreaterThan(100);
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
    "content",
    /noindex/,
  );
  const html = await (await request.get("./")).text();
  expect(html).toContain(
    'name="robots" content="noindex, nofollow, noimageindex"',
  );
  await page.screenshot({ path: "test-results/exterior.png" });
  await page.getByRole("button", { name: "02 Ground floor" }).click();
  await expect(page.locator("#view-status")).toHaveText(
    "Ground floor · orbit view",
  );
  await page.screenshot({ path: "test-results/ground.png" });
  await page.getByRole("button", { name: "03 Upper floor" }).click();
  await expect(page.locator("#view-status")).toHaveText(
    "Upper floor · orbit view",
  );
  await page.screenshot({ path: "test-results/upper.png" });
  await page.locator("#room").selectOption("U5");
  await expect(page.locator("#scene")).toHaveAttribute("data-mode", "walk");
  await expect(page.locator("#scene-heading")).toHaveText("Primary bedroom");
  await page.screenshot({ path: "test-results/walk.png" });
  await page.keyboard.press("Escape");
  await expect(page.locator("#scene")).toHaveAttribute("data-mode", "orbit");
  expect(errors).toEqual([]);
});

test("keyboard movement stops at the rear wall and room shortcuts work", async ({
  page,
}) => {
  await openViewer(page);
  await expect(page.locator("#scene")).toHaveAttribute("data-ready", "true");
  await page.locator("#room").selectOption("G1");
  const before = await page.locator("#scene").getAttribute("data-position");
  await page.keyboard.down("w");
  await page.waitForTimeout(2500);
  await page.keyboard.up("w");
  const after = (await page.locator("#scene").getAttribute("data-position"))!
    .split(",")
    .map(Number);
  expect(after[2]).toBeGreaterThan(Number(before!.split(",")[2]));
  expect(after[2]).toBeLessThanOrEqual(6.59);
  await page.locator("#room").selectOption("G2");
  await expect(page.locator("#scene-heading")).toHaveText(
    "Front shared full bathroom",
  );
  await page.locator("#orbit").click();
  await page
    .getByRole("button", { name: "Enter Living / dining zone", exact: true })
    .click();
  await expect(page.locator("#scene-heading")).toHaveText(
    "Living / dining zone",
  );
});

test("mobile layout fits and touch navigation moves", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openViewer(page);
  await expect(page.locator("#scene")).toHaveAttribute("data-ready", "true");
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(390);
  await page.screenshot({ path: "test-results/mobile.png", fullPage: true });
  await page.locator("#walk").click();
  const before = await page.locator("#scene").getAttribute("data-position");
  const forward = page.getByRole("button", {
    name: "Move forward",
    exact: true,
  });
  const box = await forward.boundingBox();
  await page.mouse.move(box!.x + box!.width / 2, box!.y + box!.height / 2);
  await page.mouse.down();
  await page.waitForTimeout(400);
  await page.mouse.up();
  expect(await page.locator("#scene").getAttribute("data-position")).not.toBe(
    before,
  );
});

test("interior depth cues toggle and the latest spaces render", async ({
  page,
}) => {
  // Allow software WebGL time for the multi-room screenshot tour on CI.
  test.setTimeout(process.env.CI ? 120_000 : 30_000);
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await openViewer(page);
  await expect(page.locator(".edition")).toContainText("CONCEPT 14");
  for (const room of ["G5", "G2", "G6", "U5"]) {
    await page.locator("#room").selectOption(room);
    await expect(page.locator("#scene")).toHaveAttribute("data-depth", "true");
    await page.screenshot({ path: `test-results/interior-${room}.png` });
  }
  await page.locator("#depth").uncheck();
  await expect(page.locator("#scene")).toHaveAttribute("data-depth", "false");
  await page.screenshot({ path: "test-results/depth-off.png" });
  await page.locator("#depth").check();
  await expect(page.locator("#scene")).toHaveAttribute("data-depth", "true");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "test-results/mobile-interior.png",
    fullPage: true,
  });
  await page.locator("#furniture").uncheck();
  await page.locator("#room").selectOption("G6");
  await page.screenshot({ path: "test-results/doors-without-furniture.png" });
  expect(errors).toEqual([]);
});

test("selected roofs, sliding gate and proposed drainage controls coordinate", async ({
  page,
}) => {
  // Match the interior tour's budget for multiple software-WebGL screenshots.
  test.setTimeout(process.env.CI ? 120_000 : 30_000);
  await openViewer(page);
  await expect(page.locator("#scene")).toHaveAttribute("data-ready", "true");
  await page.getByLabel("Vehicle gate open").uncheck();
  await expect(page.locator("#scene")).toHaveAttribute("data-gate", "closed");
  await page.screenshot({ path: "test-results/gate-closed.png" });
  await page.getByLabel("Vehicle gate open").check();
  await expect(page.locator("#scene")).toHaveAttribute("data-gate", "open");
  await page.getByLabel("Proposed drainage", { exact: true }).check();
  await expect(page.locator("#drainage-legend")).toBeVisible();
  await page.screenshot({ path: "test-results/drainage-front.png" });
  await page.getByRole("button", { name: "Show rear exterior" }).click();
  await page.screenshot({ path: "test-results/drainage-rear.png" });
  await page.getByLabel("Proposed drainage", { exact: true }).uncheck();
  await page.screenshot({ path: "test-results/rear.png" });
  await page.getByLabel("Proposed drainage", { exact: true }).check();
  await page.getByLabel("Exterior roof", { exact: true }).uncheck();
  await expect(page.locator("#scene")).toHaveAttribute(
    "data-drainage",
    "false",
  );
  await expect(page.locator("#drainage-legend")).toBeHidden();
  await page.getByRole("button", { name: "02 Ground floor" }).click();
  await page.locator("#room").selectOption("G4");
  await expect(page.locator("#view-label")).toContainText("G4 reference zone");
  await page.screenshot({ path: "test-results/kitchen.png" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "test-results/mobile-kitchen.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.locator("#room").selectOption("U2");
  await page.screenshot({ path: "test-results/upper-bathroom.png" });
});

test("realistic finishes load locally and switch back to simple materials", async ({
  page,
}) => {
  // Switching mapped materials compiles additional programs on software WebGL.
  test.setTimeout(process.env.CI ? 120_000 : 30_000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await openViewer(page);
  await expect(
    page.getByLabel("Realistic materials", { exact: true }),
  ).toBeChecked();
  await page.locator("#room").selectOption("G5");
  await page.screenshot({ path: "test-results/materials-realistic.png" });
  await page.getByLabel("Realistic materials", { exact: true }).uncheck();
  await expect(page.locator("#scene")).toHaveAttribute(
    "data-materials",
    "simple",
  );
  await page.screenshot({ path: "test-results/materials-simple.png" });
  await page.getByLabel("Realistic materials", { exact: true }).check();
  await expect(page.locator("#scene")).toHaveAttribute(
    "data-materials",
    "realistic",
  );
  expect(errors).toEqual([]);
});

test("a missing texture set keeps the house navigable with fallback materials", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route("**/textures/wood-*.jpg", (route) => route.abort());
  await page.goto("./");
  await expect(page.locator("#scene")).toHaveAttribute(
    "data-textures",
    "partial",
    { timeout: 30_000 },
  );
  await expect(page.locator("#material-status")).toContainText(
    "Some finishes could not load",
  );
  await page.locator("#room").selectOption("G4");
  await expect(page.locator("#scene")).toHaveAttribute("data-mode", "walk");
  expect(errors).toEqual([]);
});
