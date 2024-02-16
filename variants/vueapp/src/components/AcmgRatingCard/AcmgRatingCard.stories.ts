import AcmgRatingCard from './AcmgRatingCard.vue'
import { Seqvar, SeqvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import type { Meta, StoryObj } from '@storybook/vue3'
import { AcmgRating$Api } from '@variants/api/variantClient'

const projectUuid = "fake-project-uuid"
const caseUuid = "fake-case-uuid"
const seqvarExample: Seqvar = new SeqvarImpl(
  "grch37",
  "1",
  12345,
  "A",
  "T"
)
const acmgRatingExample: AcmgRating$Api = {
  release: seqvarExample.genomeBuild == "grch37" ? "GRCh37" : "GRCh38",
  chromosome: seqvarExample.chrom,
  start: seqvarExample.pos,
  end: seqvarExample.pos + seqvarExample.del.length - 1,
  reference: seqvarExample.del,
  alternative: seqvarExample.ins,
  sodar_uuid: "fake-acmg-rating-uuid",
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
  class_auto: 3
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
    seqvar: seqvarExample,
    projectUuid,
    caseUuid
  }
} satisfies Meta<typeof AcmgRatingCard>

export default meta

type Story = StoryObj<typeof meta>

export const Example: Story = {
  args: {
    seqvar: seqvarExample
  },
  parameters: {
    fetchMock: {
      mocks: [
        {
          matcher: {
            name: 'searchSuccess',
            url: 'path:/variants/ajax/acmg-criteria-rating/list-create/fake-case-uuid/',
          },
          response: {
            status: 200,
            body: [
              structuredClone(acmgRatingExample),
            ]
          }
        }
      ]
    }
  }
}
