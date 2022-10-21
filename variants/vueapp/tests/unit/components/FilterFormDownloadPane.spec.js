import FilterFormDownloadPane from '@variants/components/FilterFormDownloadPane.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import singletonCaseData from '../../data/case-singleton.json'
import trioCaseData from '../../data/case-trio.json'

describe('FilterFormDownloadPane.vue', () => {
  test('export singleton with help', async () => {
    const wrapper = shallowMount(FilterFormDownloadPane, {
      props: {
        showFiltrationInlineHelp: true,
        case: singletonCaseData,
        exportSettings: {
          file_type: 'tsv',
          export_flags: true,
          export_comments: true,
          export_donors: [],
        },
      },
    })

    const downloadFileType = wrapper.find('#download-file-type')
    const downloadPedigreeA = wrapper.find(
      '#download-pedigree-NA12878-N1-DNA1-WES1'
    )
    const downloadPedigreeExportFlags = wrapper.find(
      '#download-pedigree-export_flags'
    )
    const downloadPedigreeExportComments = wrapper.find(
      '#download-pedigree-export_comments'
    )

    await downloadFileType.setValue('xlsx')
    await downloadPedigreeA.setValue()
    await downloadPedigreeExportFlags.setValue()
    await downloadPedigreeExportComments.setValue()

    expect(downloadFileType.element.value).toBe('xlsx')
    expect(downloadPedigreeA.element.checked).toBeTruthy()
    expect(downloadPedigreeExportFlags.element.checked).toBeTruthy()
    expect(downloadPedigreeExportComments.element.checked).toBeTruthy()
  })

  test('export trio only only two donors no flags no comments', async () => {
    const wrapper = shallowMount(FilterFormDownloadPane, {
      props: {
        showFiltrationInlineHelp: false,
        case: trioCaseData,
        exportSettings: {
          file_type: 'tsv',
          export_flags: true,
          export_comments: true,
          export_donors: ['NA12878-N1-DNA1-WES1'],
        },
      },
    })

    const downloadFileType = wrapper.find('#download-file-type')
    const downloadPedigreeA = wrapper.find(
      '#download-pedigree-NA12878-N1-DNA1-WES1'
    )
    const downloadPedigreeB = wrapper.find(
      '#download-pedigree-NA12891-N1-DNA1-WES1'
    )
    const downloadPedigreeC = wrapper.find(
      '#download-pedigree-NA12892-N1-DNA1-WES1'
    )
    const downloadPedigreeExportFlags = wrapper.find(
      '#download-pedigree-export_flags'
    )
    const downloadPedigreeExportComments = wrapper.find(
      '#download-pedigree-export_comments'
    )

    await downloadFileType.setValue('xlsx')
    await downloadPedigreeA.setValue(false)
    await downloadPedigreeB.setValue()
    await downloadPedigreeC.setValue()
    await downloadPedigreeExportFlags.setValue(false)
    await downloadPedigreeExportComments.setValue(false)

    expect(downloadFileType.element.value).toBe('xlsx')
    expect(downloadPedigreeA.element.checked).toBeFalsy()
    expect(downloadPedigreeB.element.checked).toBeTruthy()
    expect(downloadPedigreeC.element.checked).toBeTruthy()
    expect(downloadPedigreeExportFlags.element.checked).toBeFalsy()
    expect(downloadPedigreeExportComments.element.checked).toBeFalsy()
  })
})
