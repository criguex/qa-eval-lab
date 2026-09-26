import { test as setup, expect } from '@playwright/test';

const authFile = '.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');

  if (process.env.MANUAL_LOGIN) {
    // Modo "el login lo haces tú": corre headed y logueate a mano.
    // npx playwright test --project=setup --headed
    console.log('👉 Inicia sesion manualmente. Tienes hasta 5 min…');
    await page.waitForSelector('.flash.success, [data-testid="post-login"]', { timeout: 300000 });
  } else {
    await page.getByLabel('Username').fill('tomsmith');
    await page.getByLabel('Password').fill('SuperSecretPassword!');
    await page.getByRole('button', { name: /login/i }).click();
    await expect(page.locator('.flash.success')).toBeVisible();
  }

  await page.context().storageState({ path: authFile });
});
