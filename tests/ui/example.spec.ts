import { test, expect } from '@playwright/test';

test('sesion autenticada reutilizada (storageState)', async ({ page }) => {
  await page.goto('/secure');
  await expect(page).toHaveURL(/\/secure$/);
  await expect(page.getByRole('heading', { name: 'Secure Area', exact: true })).toBeVisible();
});

test('logout funciona', async ({ page }) => {
  await page.goto('/secure');
  await page.getByRole('link', { name: /logout/i }).click();
  await expect(page.locator('.flash.success')).toContainText(/logged out/i);
});
