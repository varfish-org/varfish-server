import FilterFormPriotizationPane from '@/variants/components/FilterForm/PrioritizationPane.vue'

export default {
  title: 'Variants / Filter Form Prioritization',
  component: FilterFormPriotizationPane,
  parameters: {
    fetchMock: {
      mocks: [
        {
          matcher: {
            name: 'matchAll',
            method: 'GET',
            url: '*',
          },
          response: (url, _options, _request) => {
            const decodedUrl = decodeURIComponent(url)
            const items = [
              {
                id: 'HP:0000245',
                name: 'Abnormality of the paranasal sinuses',
              },
              { id: 'HP:0000418', name: 'Narrow nasal ridge' },
              { id: 'HP:0000419', name: 'Abnormality of the nasal septum' },
            ]

            for (const item of items) {
              if (decodedUrl.endsWith(item.id)) {
                return {
                  status: 200,
                  body: [item],
                }
              }
            }
            return {
              status: 200,
              body: items,
            }
          },
        },
      ],
    },
  },
}

const Template = (args) => ({
  components: { FilterFormPriotizationPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormPriotizationPane\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :exomiser-enabled="args.exomiserEnabled"\n' +
    '    :cadd-enabled="args.caddEnabled"\n' +
    '    :cada-enabled="args.cadaEnabled"\n' +
    '    v-model:prio-enabled="args.prioEnabled"\n' +
    '    v-model:prio-algorithm="args.prioAlgorithm"\n' +
    '    v-model:prio-hpo-terms="args.prioHpoTerms"\n' +
    '    v-model:patho-enabled="args.pathoEnabled"\n' +
    '    v-model:gm-enabled="args.gmEnabled"\n' +
    '    v-model:pedia-enabled="args.pediaEnabled"\n' +
    '    v-model:patho-score="args.pathoScore"\n' +
    '    v-model:prio-gm="args.prioGm"\n' +
    '    v-model:photo-file="args.photoFile"\n' +
    '/>',
})

export const Prefilled = Template.bind({})
Prefilled.args = {
  showFiltrationInlineHelp: false,
  exomiserEnabled: true,
  caddEnabled: true,
  cadaEnabled: true,
  prioEnabled: true,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: ['HP:0000245'],
  prioGm: '',
  photoFile: '',
  pathoEnabled: true,
  gmEnabled: true,
  pediaEnabled: true,
  pathoScore: 'cadd',
}

export const PrefilledWithHelp = Template.bind({})
PrefilledWithHelp.args = {
  showFiltrationInlineHelp: true,
  exomiserEnabled: true,
  caddEnabled: true,
  cadaEnabled: true,
  prioEnabled: true,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: ['HP:0000245'],
  prioGm: '',
  photoFile: '',
  pathoEnabled: true,
  gmEnabled: true,
  pediaEnabled: true,
  pathoScore: 'cadd',
}

export const PrefilledWithWarning = Template.bind({})
PrefilledWithWarning.args = {
  showFiltrationInlineHelp: false,
  exomiserEnabled: true,
  caddEnabled: true,
  cadaEnabled: true,
  prioEnabled: false,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: ['HP:0000245'],
  prioGm: '',
  photoFile: '',
  pathoEnabled: true,
  gmEnabled: true,
  pediaEnabled: true,
  pathoScore: 'cadd',
}

export const Empty = Template.bind({})
Empty.args = {
  showFiltrationInlineHelp: false,
  exomiserEnabled: false,
  caddEnabled: false,
  cadaEnabled: false,
  prioEnabled: false,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: [],
  prioGm: '',
  photoFile: '',
  pathoEnabled: false,
  gmEnabled: false,
  pediaEnabled: false,
  pathoScore: 'mutationtaster',
}
