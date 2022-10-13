import FilterResultsTableClinvar from './FilterResultsTableClinvar.vue'

export default {
  title: 'Variants / Result Table Cell ClinVar',
  component: FilterResultsTableClinvar,
}

const Template = (args) => ({
  components: { FilterResultsTableClinvar },
  setup() {
    return { args }
  },
  template:
    '<FilterResultsTableClinvar \n' + '    :params="args.params"\n' + '/>',
})

export const PracticeGuideline = Template.bind({})
PracticeGuideline.args = {
  params: {
    data: {
      summary_pathogenicity_label: 'pathogenic',
      summary_review_status_label: 'practice guideline',
      summary_gold_stars: 4,
    },
  },
}

export const ExpertPanel = Template.bind({})
ExpertPanel.args = {
  params: {
    data: {
      summary_pathogenicity_label: 'likely pathogenic',
      summary_review_status_label: 'expert panel',
      summary_gold_stars: 3,
    },
  },
}

export const MultipleSubmitters = Template.bind({})
MultipleSubmitters.args = {
  params: {
    data: {
      summary_pathogenicity_label: 'uncertain significance',
      summary_review_status_label:
        'criteria provided, multiple submitters, no conflicts',
      summary_gold_stars: 2,
    },
  },
}

export const SingleSubmitter = Template.bind({})
SingleSubmitter.args = {
  params: {
    data: {
      summary_pathogenicity_label: 'likely benign',
      summary_review_status_label: 'criteria provided, single submitter',
      summary_gold_stars: 1,
    },
  },
}

export const NoAssertionCriteria = Template.bind({})
NoAssertionCriteria.args = {
  params: {
    data: {
      summary_pathogenicity_label: 'benign',
      summary_review_status_label: 'no assertion criteria provided',
      summary_gold_stars: 0,
    },
  },
}
