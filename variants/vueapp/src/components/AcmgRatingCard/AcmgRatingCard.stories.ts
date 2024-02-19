import AcmgRatingCard from './AcmgRatingCard.vue'
import { Seqvar, SeqvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import type { Meta, StoryObj } from '@storybook/vue3'
import { AcmgRating$Api } from '@variants/api/variantClient'

const projectUuid = 'fake-project-uuid'
const caseUuid = 'fake-case-uuid'
const seqvarExampleBenign: Seqvar = new SeqvarImpl(
  'grch37',
  '1',
  12345,
  'A',
  'T',
)
const seqvarExamplePathogenic: Seqvar = new SeqvarImpl(
  'grch37',
  '1',
  12345,
  'A',
  'T',
)
const seqvarExampleNotOnServer: Seqvar = new SeqvarImpl(
  'grch37',
  '1',
  12345,
  'A',
  'T',
)
const acmgRatingExampleBenign: AcmgRating$Api = {
  release: seqvarExampleBenign.genomeBuild == 'grch37' ? 'GRCh37' : 'GRCh38',
  chromosome: seqvarExampleBenign.chrom,
  start: seqvarExampleBenign.pos,
  end: seqvarExampleBenign.pos + seqvarExampleBenign.del.length - 1,
  reference: seqvarExampleBenign.del,
  alternative: seqvarExampleBenign.ins,
  sodar_uuid: 'fake-acmg-rating-uuid',
  pvs1: 0,
  ps1: 0,
  ps2: 0,
  ps3: 0,
  ps4: 0,
  pm1: 0,
  pm2: 0,
  pm3: 0,
  pm4: 0,
  pm5: 0,
  pm6: 0,
  pp1: 0,
  pp2: 0,
  pp3: 0,
  pp4: 0,
  pp5: 0,
  ba1: 1,
  bs1: 1,
  bs2: 0,
  bs3: 0,
  bs4: 0,
  bp1: 0,
  bp2: 0,
  bp3: 0,
  bp4: 0,
  bp5: 0,
  bp6: 0,
  bp7: 0,
  class_override: undefined,
  class_auto: 3,
}
const acmgRatingExamplePathogenic: AcmgRating$Api = {
  release:
    seqvarExamplePathogenic.genomeBuild == 'grch37' ? 'GRCh37' : 'GRCh38',
  chromosome: seqvarExamplePathogenic.chrom,
  start: seqvarExamplePathogenic.pos,
  end: seqvarExamplePathogenic.pos + seqvarExamplePathogenic.del.length - 1,
  reference: seqvarExamplePathogenic.del,
  alternative: seqvarExamplePathogenic.ins,
  sodar_uuid: 'fake-acmg-rating-uuid',
  pvs1: 1,
  ps1: 1,
  ps2: 0,
  ps3: 0,
  ps4: 0,
  pm1: 0,
  pm2: 0,
  pm3: 0,
  pm4: 0,
  pm5: 0,
  pm6: 0,
  pp1: 0,
  pp2: 0,
  pp3: 0,
  pp4: 0,
  pp5: 0,
  ba1: 0,
  bs1: 0,
  bs2: 0,
  bs3: 0,
  bs4: 0,
  bp1: 0,
  bp2: 0,
  bp3: 0,
  bp4: 0,
  bp5: 0,
  bp6: 0,
  bp7: 0,
  class_override: undefined,
  class_auto: 3,
}

const meta = {
  title: 'Variants / Seqvar ACMG Rating',
  component: AcmgRatingCard,
  tags: ['autodocs'],
  argTypes: {
    seqvar: { control: { type: 'object' } },
    projectUuid: { constrol: { type: 'string' } },
    caseUuid: { constrol: { type: 'string' } },
  },
  args: {
    projectUuid,
    caseUuid,
  },
  parameters: {
    mockAddonConfigs: {
      globalMockData: [],
      ignoreQueryParams: false,
      refreshStoryOnUpdate: true,
      disableUsingOriginal: false,
      disable: false,
    },
  },
} satisfies Meta<typeof AcmgRatingCard>

export default meta

type Story = StoryObj<typeof meta>

export const OnServerPathogenic: Story = {
  args: {
    seqvar: seqvarExamplePathogenic,
  },
  parameters: {
    mockData: [
      {
        url: '/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/',
        method: 'GET',
        status: 200,
        response: {
          next: null,
          previous: null,
          results: [structuredClone(acmgRatingExamplePathogenic)],
        },
      },
      {
        url:
          '/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/' +
          '?release=GRCh37&chromosome=1&start=12345&end=12345&reference=A&alternative=T',
        method: 'GET',
        status: 200,
        response: {
          next: null,
          previous: null,
          results: [structuredClone(acmgRatingExamplePathogenic)],
        },
      },
    ],
  },
}

export const OnServerBenign: Story = {
  args: {
    seqvar: seqvarExampleBenign,
  },
  parameters: {
    mockData: [
      {
        url: '/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/',
        method: 'GET',
        status: 200,
        response: {
          next: null,
          previous: null,
          results: [structuredClone(acmgRatingExampleBenign)],
        },
      },
      {
        url:
          '/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/' +
          '?release=GRCh37&chromosome=1&start=12345&end=12345&reference=A&alternative=T',
        method: 'GET',
        status: 200,
        response: {
          next: null,
          previous: null,
          results: [structuredClone(acmgRatingExampleBenign)],
        },
      },
    ],
  },
}

export const NotOnServer: Story = {
  args: {
    seqvar: seqvarExampleNotOnServer,
  },
  parameters: {
    mockData: [
      {
        url: '/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/',
        method: 'GET',
        status: 200,
        response: {
          next: null,
          previous: null,
          results: [],
        },
      },
      {
        url:
          '/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/' +
          '?release=GRCh37&chromosome=1&start=12345&end=12345&reference=A&alternative=T',
        method: 'GET',
        status: 200,
        response: {
          next: null,
          previous: null,
          results: [],
        },
      },
    ],
  },
}
