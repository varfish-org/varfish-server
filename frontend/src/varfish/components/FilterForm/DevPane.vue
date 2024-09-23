<script setup>
import { computed, ref } from 'vue'
import useClipboard from 'vue-clipboard3'

const props = defineProps({
  querySettings: Object,
})

const emit = defineEmits(['update:querySettings'])

const { toClipboard } = useClipboard()

const rawFilterCriteriaRef = ref(null)
const editSettingsRef = ref(false)

const copyToClipboard = async () => {
  try {
    await toClipboard(JSON.stringify(props.querySettings, null, 2))
  } catch (e) {
    console.error(e)
  }
}

const downloadJson = () => {
  const data = JSON.stringify(props.querySettings, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'varfish_query_settings.json'
  a.click()
  window.URL.revokeObjectURL(url)
}

const settingsValue = computed({
  get: () => {
    return JSON.stringify(props.querySettings, null, 2)
  },
})

const applySettings = () => {
  try {
    emit('update:querySettings', JSON.parse(rawFilterCriteriaRef.value.value))
  } catch (e) {
    console.warn(e)
  }
}

const toggleEditMode = () => {
  editSettingsRef.value = !editSettingsRef.value
  if (!editSettingsRef.value) {
    applySettings()
  }
}
</script>

<template>
  <div style="position: relative" class="mr-2 mt-2">
    <div class="alert alert-secondary small p-2 m-2 mb-0">
      <p class="mb-1">
        <i-mdi-information />
        Use this field to export your settings in case a developer asks for it.
      </p>
    </div>

    <div>
      <textarea
        class="form-control"
        rows="20"
        ref="rawFilterCriteriaRef"
        v-model="settingsValue"
        :readonly="!editSettingsRef"
      />
      <div class="form-inline">
        <div class="btn-group">
          <button class="btn btn-primary" @click.prevent="copyToClipboard">
            <i-mdi-content-copy />
            Copy to Clipboard
          </button>
          <button class="btn btn-secondary" @click.prevent="downloadJson">
            <i-mdi-download />
            Export as JSON
          </button>
        </div>
        <div class="custom-control custom-switch ml-2">
          <input
            type="checkbox"
            class="custom-control-input"
            id="customSwitch1"
            @click="toggleEditMode"
          />
          <label class="custom-control-label" for="customSwitch1">
            Toggle Edit Mode &mdash; <u class="ml-1 mr-1">enable</u> to modify
            settings &mdash; <u class="ml-1 mr-1">disable</u> to apply settings
          </label>
        </div>
      </div>
    </div>
  </div>
</template>
