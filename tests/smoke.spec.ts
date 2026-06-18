import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL || "https://pcbisolation.com";

test("homepage loads with correct title", async ({ page }) => {
  await page.goto(BASE);
  await expect(page).toHaveTitle(/PCB Isolation/);
  await expect(page.locator("nav")).toBeVisible();
});

test("blog index lists posts", async ({ page }) => {
  await page.goto(`${BASE}/blog/`);
  const posts = page.locator("article, .post-entry");
  const count = await posts.count();
  expect(count).toBeGreaterThan(10);
});

test("post with table renders a Markdown table", async ({ page }) => {
  await page.goto(`${BASE}/blog/led-strip-current-and-power/`);
  const table = page.locator("table");
  await expect(table.first()).toBeVisible();
  const rows = page.locator("table tr");
  const rowCount = await rows.count();
  expect(rowCount).toBeGreaterThan(2);
});

test("post with gallery shows images", async ({ page }) => {
  await page.goto(
    `${BASE}/blog/waterproof-sound-proof-generator-enclosure/`
  );
  const gallery = page.locator(".figure-gallery img");
  await expect(gallery.first()).toBeVisible();
});

test("Remark42 comment widget loads on a post", async ({ page }) => {
  await page.goto(`${BASE}/blog/led-strip-current-and-power/`);
  const remark = page.locator("#remark42");
  await expect(remark).toBeVisible({ timeout: 10000 });
});

test("www redirects to apex HTTPS", async ({ page }) => {
  const response = await page.goto("http://www.pcbisolation.com/");
  expect(response?.url()).toBe(`${BASE}/`);
  expect(response?.status()).toBe(200);
});

test("known image returns 200", async ({ page }) => {
  const response = await page.goto(
    `${BASE}/wp-content/uploads/2021/08/generator-enclosure-14.jpg`
  );
  expect(response?.status()).toBe(200);
});

test("non-existent page returns 404", async ({ page }) => {
  const response = await page.goto(`${BASE}/this-page-does-not-exist/`);
  expect(response?.status()).toBe(404);
});
