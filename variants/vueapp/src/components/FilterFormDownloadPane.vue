<script setup>
import { useVuelidate } from '@vuelidate/core'
import { computed, onMounted } from 'vue'
import { displayName } from '@varfish/helpers.js'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  case: Object,
  exportSettings: Object,
})

const emit = defineEmits(['update:exportSettings'])

const declareWrapper = (name) => {
  return computed({
    get() {
      return props.exportSettings[name]
    },
    set(newValue) {
      props.exportSettings[name] = newValue
    },
  })
}

const formState = {
  fileType: declareWrapper('file_type'),
  exportComments: declareWrapper('export_comments'),
  exportFlags: declareWrapper('export_flags'),
}

// Define validation rules.
const rules = {
  fileType: {},
  exportComments: {},
  exportFlags: {},
}

for (const member of Object.values(props.case.pedigree)) {
  formState[`member_${member.name}`] = computed({
    get() {
      return props.exportSettings.export_donors.includes(member.name)
    },
    set(newValue) {
      if (
        props.exportSettings.export_donors.includes(member.name) &&
        !newValue
      ) {
        props.exportSettings.export_donors =
          props.exportSettings.export_donors.filter(
            (name) => name != member.name
          )
      } else if (
        !props.exportSettings.export_donors.includes(member.name) &&
        newValue
      ) {
        props.exportSettings.export_donors.push(member.name)
      }
    },
  })

  rules[`member_${member.name}`] = {}
}
// Define vuelidate object
const v$ = useVuelidate(rules, formState)

onMounted(() => {
  v$.value.$touch()
})

// Define the exposed functions
defineExpose({
  v$,
})
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2 mb-3"
  >
    <i-mdi-information />
    The settings in this tab are only used when using the
    <span class="badge badge-secondary">
      <i-fa-solid-cloud-download-alt />
      Download
    </span>
    button and not when using
    <span class="badge badge-primary">
      <i-mdi-refresh />
      Filter &amp; Display
    </span>
    button below.
  </div>

  <div class="form-group row">
    <label
      class="col-xl-1 col-lg-2 col-3 col-form-label text-nowrap"
      for="download-file-type"
    >
      Download File Type
    </label>
    <div class="col-xl-11 col-lg-10 col-9">
      <!-- TODO: v-model -->
      <select
        v-model="v$.fileType.$model"
        class="custom-select"
        id="download-file-type"
      >
        <option value="xlsx">Excel (.xlsx)</option>
        <option value="tsv">TSV (.tsv)</option>
        <option value="vcf">VCF (.vcf.gz)</option>
      </select>
      <small class="form-text text-muted">
        The VCF file export contains the bare minimum information (genomic
        variant and genotype, coverage, allelic depth, genotype call quality
        score). Most filters work but please note that the HGMD public
        membership filtration is ignored as well as any filters for flags,
        comments, and ClinVar details.
      </small>
    </div>
  </div>

  <div class="form-group row">
    <label class="col-xl-1 col-lg-2 col-3 col-form-label text-nowrap">
      Donors to Export
    </label>
    <div class="col-xl-11 col-lg-10 col-9">
      <!-- TODO: v-model -->
      <div
        v-for="member of props.case.pedigree"
        class="custom-control custom-checkbox"
      >
        <input
          v-model="v$[`member_${member.name}`].$model"
          type="checkbox"
          class="custom-control-input"
          :id="`download-pedigree-${member.name}`"
        />
        <label
          class="custom-control-label"
          :for="`download-pedigree-${member.name}`"
        >
          {{ displayName(member.name) }}
        </label>
      </div>
      <small class="form-text text-muted">
        Select the donors to export. This is useful when you want first filter a
        trio case and then only export the index. For example, MutationTaster
        only allows to analyze a single individual.
      </small>
    </div>
  </div>

  <div class="form-group row">
    <label class="col-xl-1 col-lg-2 col-3 col-form-label text-nowrap">
      Flags &amp; Comments
    </label>
    <div class="col-xl-11 col-lg-10 col-9">
      <div class="custom-control custom-checkbox">
        <input
          v-model="v$.exportFlags.$model"
          type="checkbox"
          class="custom-control-input"
          id="download-pedigree-export_flags"
        />
        <label
          class="custom-control-label"
          for="download-pedigree-export_flags"
        >
          export flags
        </label>
        <small class="form-text text-muted"> Include flags in export. </small>
      </div>
      <div class="custom-control custom-checkbox">
        <input
          v-model="v$.exportComments.$model"
          type="checkbox"
          class="custom-control-input"
          id="download-pedigree-export_comments"
        />
        <label
          class="custom-control-label"
          for="download-pedigree-export_comments"
        >
          export comments
        </label>
        <small class="form-text text-muted">
          Include comments in export.
        </small>
      </div>
    </div>
  </div>
</template>
