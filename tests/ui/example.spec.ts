import { test, expect } from '@playwright/test';

test('sesion autenticada reutilizada (storageState)', async ({ page }) => {
  await page.goto('/secure');
  await expect(page.locator('.flash.success')).toContainText(/logged into a secure area/i);
});

test('logout funciona', async ({ page }) => {
  await page.goto('/secure');
  await page.getByRole('link', { name: /logout/i }).click();
  await expect(page.locator('.flash.success')).toContainText(/logged out/i);
});
