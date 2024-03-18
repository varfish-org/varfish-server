<script setup>
import useClipboard from 'vue-clipboard3'
import { computed, ref } from 'vue'

const props = defineProps({
  querySettings: Object,
})
const emit = defineEmits(['update:querySettings'])
const { toClipboard } = useClipboard()
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
  set: (value) => {
    try {
      emit('update:querySettings', JSON.parse(value))
    } catch (e) {
      console.warn(e)
    }
  },
})
const editSettings = ref(false)
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
        rows="5"
        v-model="settingsValue"
        :readonly="!editSettings"
      />
      <div class="form-inline">
        <div class="btn-group">
          <button class="btn btn-primary" @click="copyToClipboard">
            <i-mdi-content-copy />
            Copy to Clipboard
          </button>
          <button class="btn btn-secondary" @click="downloadJson">
            <i-mdi-download />
            Export as JSON
          </button>
        </div>
        <div class="custom-control custom-switch ml-2">
          <input
            type="checkbox"
            class="custom-control-input"
            id="customSwitch1"
            @click="editSettings = !editSettings"
          />
          <label class="custom-control-label" for="customSwitch1"
            >Enable Edit Mode</label
          >
        </div>
      </div>
    </div>
  </div>
</template>
