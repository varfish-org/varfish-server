import FilterFormPriotizationPane from '@variants/components/FilterFormPrioritizationPane.vue'

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

            for (let item of items) {
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
    '    :csrf-token="args.csrfToken"\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :exomiser-enabled="args.exomiserEnabled"\n' +
    '    :cadd-enabled="args.caddEnabled"\n' +
    '    v-model:prio-enabled="args.prioEnabled"\n' +
    '    v-model:prio-algorithm="args.prioAlgorithm"\n' +
    '    v-model:prio-hpo-terms="args.prioHpoTerms"\n' +
    '    v-model:patho-enabled="args.pathoEnabled"\n' +
    '    v-model:patho-score="args.pathoScore"\n' +
    '/>',
})

export const Prefilled = Template.bind({})
Prefilled.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: false,
  exomiserEnabled: true,
  caddEnabled: true,
  prioEnabled: true,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: ['HP:0000245'],
  pathoEnabled: true,
  pathoScore: 'cadd',
}

export const PrefilledWithHelp = Template.bind({})
PrefilledWithHelp.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: true,
  exomiserEnabled: true,
  caddEnabled: true,
  prioEnabled: true,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: ['HP:0000245'],
  pathoEnabled: true,
  pathoScore: 'cadd',
}

export const PrefilledWithWarning = Template.bind({})
PrefilledWithWarning.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: false,
  exomiserEnabled: true,
  caddEnabled: true,
  prioEnabled: false,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: ['HP:0000245'],
  pathoEnabled: true,
  pathoScore: 'cadd',
}

export const Empty = Template.bind({})
Empty.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: false,
  exomiserEnabled: false,
  caddEnabled: false,
  prioEnabled: false,
  prioAlgorith: 'hiphive-human',
  prioHpoTerms: [],
  pathoEnabled: false,
  pathoScore: 'mutationtaster',
}
