import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.goto(
    'http://localhost:6006/iframe.html?globals=backgrounds.grid:!false;backgrounds.value:!hex(F8F8F8)&id=seqvars-seqvars-filtration--example',
  )
})

test('preset values are set correctly,', async ({ page }) => {
  await page.getByLabel('Create query based on de novo').click()

  // genotype
  await expect(
    page.locator(
      '[aria-label="Genotype presets"] [aria-selected="true"]:has-text("de novo")',
    ),
  ).toBeVisible()
  await expect(
    page.locator(
      '.v-select:has(label:has-text("recessive")):has-text("disabled")',
    ),
  ).toBeVisible()

  await expect(page.locator('#index')).toBeChecked()
  await expect(
    page.locator(
      'fieldset:has(legend:has-text("index")) [aria-checked="true"]',
    ),
  ).toContainText(['1/0', '1/1'])

  await expect(page.locator('#father')).toBeChecked()
  await expect(
    page.locator(
      'fieldset:has(legend:has-text("father")) [aria-checked="true"]',
    ),
  ).toContainText('0/0')

  await expect(page.locator('#mother')).toBeChecked()
  await expect(
    page.locator(
      'fieldset:has(legend:has-text("mother")) [aria-checked="true"]',
    ),
  ).toContainText('0/0')

  // frequency
  await expect(
    page.locator(
      '[aria-label="Frequency presets"] [aria-selected="true"]:has-text("dominant strict")',
    ),
  ).toBeVisible()
  await expect(page.locator("[id='gnomAd exomes']")).toBeChecked()
  await expect(page.locator("[id='gnomAd genomes']")).toBeChecked()
  await expect(page.locator("[id='gnomAd mitochondrial']")).toBeChecked({
    checked: false,
  })
  await expect(page.locator("[id='in-house DB']")).toBeChecked()
  await expect(page.locator('#HelixMTdb')).toBeChecked({ checked: false })

  // effects
  await expect(
    page.locator(
      '[aria-label="Effects presets"] [aria-selected="true"]:has-text("AA change + splicing")',
    ),
  ).toBeVisible()
  await expect(page.locator('input[aria-label="non-coding"]')).toBeChecked({
    checked: false,
  })
  await expect(page.locator('input[aria-label="missense"]')).toBeChecked()

  // quality
  await expect(
    page.locator(
      '[aria-label="Quality presets"] [aria-selected="true"]:has-text("super strict")',
    ),
  ).toBeVisible()
  const section = await page.locator('[aria-label="Quality"]')
  for (const loc of await section.locator('[aria-label="min DP het"]').all()) {
    await expect(loc).toHaveValue('10')
  }
  for (const loc of await section.locator('[aria-label="max DP hom"]').all()) {
    await expect(loc).toHaveValue('5')
  }
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
      .locator('button[title="Create query based on recessive"]')
      .click()
  })

  test('index selects are mutually exclusive', async ({ page }) => {
    await expect(page.locator('input[value="index"]')).toHaveCount(1)
    await page.locator('.v-select:has-text("father")').first().click()
    await page.locator('.v-list-item-title:has-text("index")').click()
    await expect(page.locator('input[value="index"]')).toHaveCount(1)
  })
})
