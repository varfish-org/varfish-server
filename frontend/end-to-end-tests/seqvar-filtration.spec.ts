import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.goto(
    'http://localhost:6006/iframe.html?globals=backgrounds.grid:!false;backgrounds.value:!hex(F8F8F8)&id=seqvars-seqvars-filtration--example',
  )
})

test('modified genotype preset is marked', async ({ page }) => {
  page.locator('button[aria-label="Create query based on dominant"]').click()

  const selectedGenotypePreset = page.locator(
    '[aria-selected="true"]:below(:text("Genotype")):has-text("dominant")',
  )
  await expect(selectedGenotypePreset.first()).toBeVisible()

  const modifiedPreset = selectedGenotypePreset.locator('[data-test-modified]')
  await expect(modifiedPreset).toBeHidden()
  await page.getByRole('button', { name: '1/0' }).first().click()
  await expect(modifiedPreset).toBeVisible()
})

test.describe('genotype', () => {
  test.beforeEach(async ({ page }) => {
    await page
      .locator('button[aria-label="Create query based on de novo"]')
      .click()
  })

  test('any is checked when all types are checked', async ({ page }) => {
    const firstAnyButton = page
      .getByRole('button', { name: 'any' })
      .and(page.locator('[aria-checked]'))
      .first()
    await expect(firstAnyButton).toHaveAttribute('aria-checked', 'false')
    for (const name of ['0/0', '1/0', '1/1']) {
      const button = page.getByRole('button', { name }).first()
      if ((await button.getAttribute('aria-checked')) === 'false') {
        await button.click()
      }
    }
    await expect(firstAnyButton).toHaveAttribute('aria-checked', 'true')
  })
})

test.describe('genotype (recessive)', () => {
  test.beforeEach(async ({ page }) => {
    await page
      .locator('button[aria-label="Create query based on recessive"]')
      .click()
  })

  test('index radios are mutually exclusive', async ({ page }) => {
    await page
      .locator('input[type="radio"][aria-label="Index"]:not(:checked)')
      .first()
      .click()
    await expect(
      page.locator('input[type="radio"][aria-label="Index"]:checked'),
    ).toHaveCount(1)
  })

  test('only two parent radios can be selected', async ({ page }) => {
    const parentRadios = page.locator(
      'input[type="radio"][aria-label="Parent"]',
    )
    expect(await parentRadios.count()).toBe(3)
    for (const parent of await parentRadios.all()) {
      await parent.click()
    }
    await expect(await parentRadios.and(page.locator(':checked'))).toHaveCount(
      2,
    )
  })
})