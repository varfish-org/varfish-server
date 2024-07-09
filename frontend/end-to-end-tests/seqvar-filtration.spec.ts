import { expect, test } from '@playwright/test'

test('sets genotype preset', async ({ page }) => {
  await page.goto(
    'http://localhost:6006/?path=/story/seqvars-seqvars-filtration--example',
  )
  const frame = page.frameLocator('iframe[title="storybook-preview-iframe"]')

  await frame
    .locator('button[aria-label="Create query based on dominant"]')
    .click()

  await frame.locator('button:text("dominant")').first().click()

  await expect(
    frame.locator('[aria-selected="true"]:below(:text("Genotype"))').first(),
  ).toHaveText('dominant')
})
