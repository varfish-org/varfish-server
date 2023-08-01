import HpoTermInput from '@variants/components/HpoTermInput.vue'

export default {
  title: 'Variants / HPO Term Input',
  component: HpoTermInput,
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
  components: { HpoTermInput },
  setup() {
    return { args }
  },
  template:
    '<HpoTermInput\n' +
    '    api-endpoint="/api/"\n' +
    '    :csrf-token="args.csrfToken"\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    v-model="args.hpoTerms"\n' +
    '/>',
})

export const Prefilled = Template.bind({})
Prefilled.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: false,
  hpoTerms: ['HP:0000245', 'HP:0000418'],
}

export const PrefilledWithHelp = Template.bind({})
PrefilledWithHelp.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: true,
  hpoTerms: ['HP:0000245', 'HP:0000418'],
}

export const Empty = Template.bind({})
Empty.args = {
  csrfToken: 'fake token',
  showFiltrationInlineHelp: false,
  hpoTerms: [],
}
