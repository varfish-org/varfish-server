<script setup>
/** Simple wrapper around vega for plotting data.
 *
 * The "vue-vega" library has not been updated for a long time.
 */
import * as vega from 'vega'
import vegaEmbed from 'vega-embed'
import { onMounted, computed, ref, watch } from 'vue'

/** Define the props. */
const props = defineProps({
  title: String,
  description: String,
  dataValues: {
    type: Array,
    default: () => [],
  },
  dataName: {
    type: String,
    default: 'dataset',
  },
  encoding: Object,
  params: Object,
  layer: Object,
  width: {
    type: [Number, String],
    default: 300,
  },
  height: {
    type: [Number, String],
    default: 300,
  },
  mark: {
    type: [Boolean, Object],
    default: { type: 'bar' },
  },
  renderer: {
    type: String,
    default: 'canvas',
  },
  transform: Array,
})

/** The <div> with the plot. */
const plotDivRef = ref(null)
/** The vega plot once initialized. */
const vegaViewRef = ref(null)

/** The vega specification. */
const vegaLiteSpec = computed(() => {
  const res = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    title: props.title,
    width: props.width,
    height: props.height,
    description: props.description,
    params: props.params,
    data: {
      values: props.dataValues,
      name: props.dataName,
    },
    encoding: props.encoding,
    transform: props.transform,
  }
  if (props.mark !== undefined && props.mark !== null && props.mark !== false) {
    res.mark = props.mark
  }
  if (props.layer !== undefined && props.layer !== null) {
    res.layer = props.layer
  }
  return res
})

/** Make component reactive to props.data changes. */
watch(
  () => props.dataValues,
  (newValue, _oldValue) => {
    if (vegaViewRef.value !== null) {
      const changeset = vega
        .changeset()
        .remove(() => true)
        .insert(newValue)
      vegaViewRef.value.change(props.dataName, changeset).run()
      vegaViewRef.value.resize()
    }
  },
)

/** `ref` to `vegaEmbed()` result so we can `await` the rendering. */
const vegaEmbedPromiseRef = ref(null)

/** Create vega-embed plot on mounting. */
onMounted(() => {
  const vegaOpts = {
    renderer: props.renderer,
  }
  vegaEmbedPromiseRef.value = vegaEmbed(
    plotDivRef.value,
    vegaLiteSpec.value,
    vegaOpts,
  )
  vegaEmbedPromiseRef.value.then(({ view }) => {
    vegaViewRef.value = view
  })
})

/** Return vegaEmbedPromise. */
const getVegaEmbedPromise = () => vegaEmbedPromiseRef.value

defineExpose({
  // exposed to be used in testing (only)
  getVegaEmbedPromise,
})
</script>

<template>
  <div ref="plotDivRef"></div>
</template>

<style>
.vega-embed summary {
  top: -25px !important;
  left: -5px;
  right: unset !important;
}
.vega-embed.has-actions {
  padding-right: 10px !important;
}
.vega-embed .vega-actions {
  right: unset !important;
  top: 10px !important;
  left: -5px !important;
}
.vega-embed .vega-actions::before {
  left: 5px !important;
  right: unset !important;
}
.vega-embed .vega-actions::after {
  left: 6px !important;
  right: unset !important;
}
</style>
