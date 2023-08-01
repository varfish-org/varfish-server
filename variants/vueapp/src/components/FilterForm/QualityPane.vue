<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import FilterFormQualityPaneRow from '@variants/components/FilterForm/QualityPaneRow.vue'
import { rules } from '@variants/components/FilterForm/QualityPane.values'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  caseObj: Object,
  querySettings: Object,
})

const tplValues = reactive({
  qualMinDpHet: 10,
  qualMinDpHom: 5,
  qualMinAb: 0.2,
  qualMinGq: 10,
  qualMinAd: 3,
  qualMaxAd: null,
  qualFail: 'drop-variant',
})
const keyMap = {
  qualMinDpHet: 'dp_het',
  qualMinDpHom: 'dp_hom',
  qualMinAb: 'ab',
  qualMinGq: 'gq',
  qualMinAd: 'ad',
  qualMaxAd: 'ad_max',
  qualFail: 'fail',
}

const v$ = useVuelidate(rules, tplValues)

const membersWithGtEntries = props.caseObj.pedigree.filter(
  (member) => member.has_gt_entries,
)

const childRefs = ref([])

onMounted(() => {
  v$.value.$touch()
})

defineExpose({ v$ })
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2 mb-2"
  >
    <p class="mb-1">
      <i-mdi-information />
      Use this tab to fine-tune the quality settings.
      <strong> min DP het. </strong>- minimal depth at heterozygous and
      hemizygous sites. <strong> min DP hom. </strong> - minimal depth at
      homozygous sites. <strong> min AB </strong> - minimal allelic balance
      (alt. reads divided by depth of coverage). <strong> min GQ </strong> -
      minimal genotype quality. <strong> min AD </strong> - minimal alternate
      allele depth. <strong> on FAIL </strong> - action to perform when genotype
      fails the the quality criteria.
    </p>
    <p class="mb-0">
      <strong>
        In most cases, it will be sufficient to use the quality presets instead.
      </strong>
    </p>
  </div>

  <table
    class="table table-striped table-hover sodar-card-table compact-form-groups"
  >
    <thead>
      <tr>
        <th class="text-muted" style="width: 10px">#</th>
        <th>Family</th>
        <th>Individual</th>
        <th>Father</th>
        <th>Mother</th>
        <th style="width: 100px">min DP het.</th>
        <th style="width: 100px">min DP hom.</th>
        <th style="width: 100px">min AB</th>
        <th style="width: 100px">min GQ</th>
        <th style="width: 100px">min AD</th>
        <th style="width: 100px">max AD</th>
        <th style="width: 150px">on FAIL</th>
      </tr>
    </thead>
    <tbody>
      <FilterFormQualityPaneRow
        v-for="(member, index) in membersWithGtEntries"
        :case-name="caseObj.name"
        :index="index + 1"
        :member="member"
        ref="childRefs"
        v-model:qual-min-dp-het="querySettings.quality[member.name].dp_het"
        v-model:qual-min-dp-hom="querySettings.quality[member.name].dp_hom"
        v-model:qual-min-ab="querySettings.quality[member.name].ab"
        v-model:qual-min-gq="querySettings.quality[member.name].gq"
        v-model:qual-min-ad="querySettings.quality[member.name].ad"
        v-model:qual-max-ad="querySettings.quality[member.name].ad_max"
        v-model:qual-fail="querySettings.quality[member.name].fail"
      />
    </tbody>
  </table>
</template>
