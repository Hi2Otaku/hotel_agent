import { test, expect } from '@playwright/test';

test.describe('Staff Check-in/out Flow', () => {
  // Staff frontend runs on port 5174
  test.use({ baseURL: 'http://localhost:5174' });

  test('staff login', async ({ page }) => {
    await page.goto('/');

    // Fill login form
    await page.getByLabel(/email/i).fill('admin@hotel.local');
    await page.getByLabel(/password/i).fill('admin123');

    // Submit
    await page.getByRole('button', { name: /sign in|log in|login/i }).click();

    // Expect redirect to dashboard/overview
    await expect(page.getByText(/overview|dashboard|welcome/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test('view reservations list', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.getByLabel(/email/i).fill('admin@hotel.local');
    await page.getByLabel(/password/i).fill('admin123');
    await page.getByRole('button', { name: /sign in|log in|login/i }).click();
    await expect(page.getByText(/overview|dashboard|welcome/i)).toBeVisible({
      timeout: 10_000,
    });

    // Navigate to reservations
    await page.getByRole('link', { name: /reservation/i }).click();

    // Expect reservation list with cards or table rows
    await expect(
      page.locator('[data-testid="reservation-card"], .reservation-card, table tbody tr').first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  test('check in a guest', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.getByLabel(/email/i).fill('admin@hotel.local');
    await page.getByLabel(/password/i).fill('admin123');
    await page.getByRole('button', { name: /sign in|log in|login/i }).click();
    await expect(page.getByText(/overview|dashboard|welcome/i)).toBeVisible({
      timeout: 10_000,
    });

    // Navigate to reservations
    await page.getByRole('link', { name: /reservation/i }).click();

    // Find a confirmed booking and click check-in
    const checkInButton = page.getByRole('button', { name: /check.?in/i }).first();
    await expect(checkInButton).toBeVisible({ timeout: 10_000 });
    await checkInButton.click();

    // Dialog should appear - select room if dropdown exists
    const roomSelect = page.locator('select, [role="combobox"]').first();
    if (await roomSelect.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await roomSelect.selectOption({ index: 1 });
    }

    // Confirm check-in
    const confirmButton = page.getByRole('button', { name: /confirm|check.?in|submit/i }).last();
    await confirmButton.click();

    // Expect status change indication
    await expect(
      page.getByText(/checked.?in/i).or(page.getByText(/success/i)),
    ).toBeVisible({ timeout: 10_000 });
  });
});
