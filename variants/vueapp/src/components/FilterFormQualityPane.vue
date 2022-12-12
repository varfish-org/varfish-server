<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import FilterFormQualityPaneRow from './FilterFormQualityPaneRow.vue'
import {
  numericKeys,
  failValues,
  rules,
  allKeys,
  floatKeys,
  intKeys,
} from './FilterFormQualityPane.values.js'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  caseObj: Object,
  querySettings: Object,
})

const tplValues = reactive({
  qualMinDpHet: '10',
  qualMinDpHom: '5',
  qualMinAb: '0.2',
  qualMinGq: '10',
  qualMinAd: '3',
  qualMaxAd: '',
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

const applyToWhich = ref('all')

const v$ = useVuelidate(rules, tplValues)

const applySettings = () => {
  for (const member of props.caseObj.pedigree) {
    if (
      member.has_gt_entries &&
      (applyToWhich.value === 'all' ||
        (applyToWhich.value === 'affected' && member.affected === 2) ||
        (applyToWhich.value === 'unaffected' && member.affected !== 2))
    ) {
      for (const theKey of allKeys) {
        let tplValue = v$.value[theKey].$model
        if (tplValue !== null) {
          if (intKeys.includes(tplValue)) {
            tplValue = parseInt(tplValue)
          } else if (floatKeys.includes(tplValue)) {
            tplValue = parseFloat(tplValue)
          }
          props.querySettings.quality[member.name][keyMap[theKey]] = tplValue
        }
      }
    }
  }
}

const membersWithGtEntries = props.caseObj.pedigree.filter(
  (member) => member.has_gt_entries
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
      <tr>
        <td class="text-muted text-center" colspan="5">
          <div class="form-inline">
            <span class="ml-auto"> Template Settings </span>
            <a
              href="#"
              class="btn btn-sm btn-secondary ml-auto"
              @click.prevent="applySettings()"
            >
              Apply
              <i-mdi-arrow-down-circle />
            </a>
            <select
              v-model="applyToWhich"
              class="custom-select custom-select-sm ml-3"
            >
              <option value="all">to all</option>
              <option value="unaffected">to affected</option>
              <option value="affected">to unaffected</option>
            </select>
          </div>
        </td>
        <td v-for="key in numericKeys">
          <input
            type="text"
            v-model="v$[key].$model"
            class="form-control form-control-sm"
            :class="{
              // 'is-valid': !v$[key].$error,
              'is-invalid': v$[key].$error,
            }"
          />
          <div
            v-for="error of v$[key].$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <select
            v-model="v$.qualFail.$model"
            :class="{
              // 'is-valid': !v$.qualFail.$error,
              'is-invalid': v$.qualFail.$error,
            }"
            class="custom-select custom-select-sm"
          >
            <option v-for="(label, value) in failValues" :value="value">
              {{ label }}
            </option>
          </select>
        </td>
      </tr>
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
