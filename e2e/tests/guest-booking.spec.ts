import { test, expect } from '@playwright/test';

test.describe('Guest Booking Flow', () => {
  test('search for available rooms', async ({ page }) => {
    await page.goto('/');

    // Fill search form
    await page.getByLabel(/check.?in/i).fill('2026-05-01');
    await page.getByLabel(/check.?out/i).fill('2026-05-05');
    await page.getByLabel(/guests/i).fill('2');

    // Submit search
    await page.getByRole('button', { name: /search/i }).click();

    // Expect room cards to be visible on results page
    await expect(page).toHaveURL(/\/search/);
    await expect(page.locator('[data-testid="room-card"], .room-card').first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test('view room details', async ({ page }) => {
    await page.goto('/search?checkIn=2026-05-01&checkOut=2026-05-05&guests=2');

    // Wait for results to load
    await page.waitForSelector('[data-testid="room-card"], .room-card', { timeout: 10_000 });

    // Click first room card
    await page.locator('[data-testid="room-card"], .room-card').first().click();

    // Expect room detail page with pricing info
    await expect(page.getByText(/per night/i).or(page.getByText(/total/i))).toBeVisible({
      timeout: 10_000,
    });
  });

  test('complete booking from search to confirmation', async ({ page }) => {
    // Start from search results
    await page.goto('/search?checkIn=2026-05-01&checkOut=2026-05-05&guests=2');

    // Wait for and select first room
    await page.waitForSelector('[data-testid="room-card"], .room-card', { timeout: 10_000 });
    await page.locator('[data-testid="room-card"], .room-card').first().click();

    // Select room / proceed to booking
    await page.getByRole('button', { name: /book|select|reserve/i }).click();

    // Fill guest details (step 2)
    await page.getByLabel(/first name/i).fill('Test');
    await page.getByLabel(/last name/i).fill('Guest');
    await page.getByLabel(/email/i).fill('testguest@example.com');
    await page.getByLabel(/phone/i).fill('+1234567890');
    await page.getByRole('button', { name: /next|continue/i }).click();

    // Fill payment (step 3)
    await page.getByLabel(/card number/i).fill('4242424242424242');
    await page.getByLabel(/expir/i).fill('12/28');
    await page.getByLabel(/cvv|cvc/i).fill('123');
    await page.getByRole('button', { name: /pay|confirm|submit/i }).click();

    // Expect confirmation
    await expect(
      page.getByTestId('confirmation-number').or(page.getByText(/HB-[A-Z0-9]{6}/)),
    ).toBeVisible({ timeout: 15_000 });
  });

  test('register and login', async ({ page }) => {
    await page.goto('/register');

    await page.getByLabel(/first name/i).fill('E2E');
    await page.getByLabel(/last name/i).fill('Tester');
    await page.getByLabel(/email/i).fill(`e2e-${Date.now()}@example.com`);
    await page.getByLabel(/password/i).first().fill('testpass123');

    // Some forms have confirm password
    const confirmField = page.getByLabel(/confirm/i);
    if (await confirmField.isVisible()) {
      await confirmField.fill('testpass123');
    }

    await page.getByRole('button', { name: /register|sign up|create/i }).click();

    // Expect redirect to home or dashboard
    await expect(page).toHaveURL(/^\/$|\/dashboard|\/search/, { timeout: 10_000 });
  });
});
