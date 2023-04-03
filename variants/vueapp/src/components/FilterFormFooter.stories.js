import { QueryStates } from '../enums'
import FilterFormFooter from './FilterFormFooter.vue'

export default {
  title: 'Variants / Filter Form Footer',
  component: FilterFormFooter,
}

const Template = (args) => ({
  components: { FilterFormFooter },
  setup() {
    return { args }
  },
  template:
    '<FilterFormFooter\n' +
    ':query-state="args.queryState"\n' +
    'v-model:database="args.database"\n' +
    '/>',
})

export const RefSeq = Template.bind({})
RefSeq.args = {
  database: 'refseq',
  queryState: QueryStates.Initial.value,
}

export const Ensembl = Template.bind({})
Ensembl.args = {
  database: 'ensembl',
  queryState: QueryStates.Initial.value,
}

export const Running = Template.bind({})
Running.args = {
  database: 'refseq',
  queryState: QueryStates.Running.value,
}
