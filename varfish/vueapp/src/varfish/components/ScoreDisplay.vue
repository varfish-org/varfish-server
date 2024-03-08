<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    rangeLower: number
    rangeUpper: number
    value: number
    width?: number
    height?: number
    marginX?: number
    marginY?: number
    jitter?: number
    fontSize?: string
    dispTransOffset?: number
    dispTransMult?: number
    benignVeryStrongUpper?: number
    benignStrongUpper?: number
    benignModerateUpper?: number
    benignSupportingUpper?: number
    pathogenicSupportingLower?: number
    pathogenicModerateLower?: number
    pathogenicStrongLower?: number
    pathogenicVeryStrongLower?: number
  }>(),
  {
    width: 100,
    height: 20,
    marginX: 20,
    marginY: 12,
    jitter: 1,
    fontSize: '12px',
    dispTransOffset: 0,
    dispTransMult: 1,
    // benignVeryStrongUpper: undefined,
    // benignStrongUpper: undefined,
    // benignModerateUpper: undefined,
    // benignSupportingUpper: undefined,
    // pathogenicSupportingLower: undefined,
    // pathogenicModerateLower: undefined,
    // pathogenicStrongLower: undefined,
    // pathogenicVeryStrongLower: undefined,
  },
)

const LINE_STROKE = '#303030'
const LINE_STROKE_WIDTH = 2

const FILL_OPACITY = 0.65

const labelTrans = (value: number): string => {
  const tmpNumber = (value - props.dispTransOffset) * props.dispTransMult
  return parseFloat(tmpNumber.toFixed(3)).toPrecision()
}

const xlBenignVeryStrongLower = computed(() => {
  return 0
})

const xuBenignVeryStrongUpper = computed(() => {
  if (props.benignVeryStrongUpper === undefined) {
    return 0
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.benignVeryStrongUpper
    )
  }
})

const xuBenignStrongUpper = computed(() => {
  if (props.benignStrongUpper === undefined) {
    return 0
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.benignStrongUpper
    )
  }
})

const xuBenignModerateUpper = computed(() => {
  if (props.benignModerateUpper === undefined) {
    return 0
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.benignModerateUpper
    )
  }
})

const xuBenignSupportingUpper = computed(() => {
  if (props.benignSupportingUpper === undefined) {
    return 0
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.benignSupportingUpper
    )
  }
})

const xuPathoSupportingLower = computed(() => {
  if (props.pathogenicSupportingLower === undefined) {
    return props.width
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.pathogenicSupportingLower
    )
  }
})

const xuPathoModerateLower = computed(() => {
  if (props.pathogenicModerateLower === undefined) {
    return props.width
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.pathogenicModerateLower
    )
  }
})

const xuPathoStrongLower = computed(() => {
  if (props.pathogenicStrongLower === undefined) {
    return props.width
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.pathogenicStrongLower
    )
  }
})

const xuPathoVeryStrongLower = computed(() => {
  if (props.pathogenicVeryStrongLower === undefined) {
    return props.width
  } else {
    return (
      (props.width / (props.rangeUpper - props.rangeLower)) *
        (0 - props.rangeLower) +
      (props.width / (props.rangeUpper - props.rangeLower)) *
        props.pathogenicVeryStrongLower
    )
  }
})

const xuPathoVeryStrongUpper = computed(() => {
  return props.width
})

/** Compute color between value from 0..1. */
const getColorByValue = (value: number): string => {
  const hue = ((1 - value) * 120).toString(10)
  return `hsl(${hue},100%,50%)`
}

/** Compute color by class name. */
const getColorByName = (name: string): string => {
  switch (name) {
    case 'benignVeryStrong':
      return getColorByValue(0)
    case 'benignStrong':
      return getColorByValue(0.12)
    case 'benignModerate':
      return getColorByValue(0.24)
    case 'benignSupporting':
      return getColorByValue(0.36)
    case 'pathogenicSupporting':
      return getColorByValue(0.64)
    case 'pathogenicModerate':
      return getColorByValue(0.76)
    case 'pathogenicStrong':
      return getColorByValue(0.88)
    case 'pathogenicVeryStrong':
      return getColorByValue(1)
    default:
      throw new Error(`Unknown color name: ${name}`)
  }
}

const circleFill = computed((): string => {
  if (
    props.benignVeryStrongUpper !== undefined &&
    props.value < props.benignVeryStrongUpper
  ) {
    return getColorByName('benignVeryStrong')
  } else if (
    props.benignStrongUpper !== undefined &&
    props.value < props.benignStrongUpper
  ) {
    return getColorByName('benignStrong')
  } else if (
    props.benignModerateUpper !== undefined &&
    props.value < props.benignModerateUpper
  ) {
    return getColorByName('benignModerate')
  } else if (
    props.benignSupportingUpper !== undefined &&
    props.value < props.benignSupportingUpper
  ) {
    return getColorByName('benignSupporting')
  } else if (
    props.pathogenicVeryStrongLower !== undefined &&
    props.value > props.pathogenicVeryStrongLower
  ) {
    return getColorByName('pathogenicVeryStrong')
  } else if (
    props.pathogenicStrongLower !== undefined &&
    props.value > props.pathogenicStrongLower
  ) {
    return getColorByName('pathogenicStrong')
  } else if (
    props.pathogenicModerateLower !== undefined &&
    props.value > props.pathogenicModerateLower
  ) {
    return getColorByName('pathogenicModerate')
  } else if (
    props.pathogenicSupportingLower !== undefined &&
    props.value > props.pathogenicSupportingLower
  ) {
    return getColorByName('pathogenicSupporting')
  } else {
    return 'white'
  }
})
</script>

<template>
  <svg
    :width="`${props.width + 2 * props.marginX}px`"
    :height="`${props.height + 2 * props.marginY}px`"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      v-if="
        xlBenignVeryStrongLower !== null && xuBenignVeryStrongUpper !== null
      "
      :x="props.marginX + xlBenignVeryStrongLower"
      :y="props.marginY"
      :width="xuBenignVeryStrongUpper - xlBenignVeryStrongLower"
      :height="props.height"
      :fill="getColorByName('benignVeryStrong')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="benignVeryStrong"
      stroke="none"
    />
    <rect
      v-if="xuBenignVeryStrongUpper !== null && xuBenignStrongUpper !== null"
      :x="props.marginX + xuBenignVeryStrongUpper"
      :y="props.marginY"
      :width="xuBenignStrongUpper - xuBenignVeryStrongUpper"
      :height="props.height"
      :fill="getColorByName('benignStrong')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="benignStrong"
      stroke="none"
    />
    <rect
      v-if="xuBenignStrongUpper !== null && xuBenignModerateUpper !== null"
      :x="props.marginX + xuBenignStrongUpper"
      :y="props.marginY"
      :width="xuBenignModerateUpper - xuBenignStrongUpper"
      :height="props.height"
      :fill="getColorByName('benignModerate')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="benignModerate"
      stroke="none"
    />
    <rect
      v-if="xuBenignModerateUpper !== null && xuBenignSupportingUpper !== null"
      :x="props.marginX + xuBenignModerateUpper"
      :y="props.marginY"
      :width="xuBenignSupportingUpper - xuBenignModerateUpper"
      :height="props.height"
      :fill="getColorByName('benignSupporting')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="benignSupporting"
      stroke="none"
    />

    <rect
      v-if="xuPathoSupportingLower !== null && xuPathoModerateLower !== null"
      :x="props.marginX + xuPathoSupportingLower"
      :y="props.marginY"
      :width="xuPathoModerateLower - xuPathoSupportingLower"
      :height="props.height"
      :fill="getColorByName('pathogenicSupporting')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="pathogenicSupporting"
      stroke="none"
    />
    <rect
      v-if="xuPathoModerateLower !== null && xuPathoStrongLower !== null"
      :x="props.marginX + xuPathoModerateLower"
      :y="props.marginY"
      :width="xuPathoStrongLower - xuPathoModerateLower"
      :height="props.height"
      :fill="getColorByName('pathogenicModerate')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="pathogenicModerate"
      stroke="none"
    />
    <rect
      v-if="xuPathoStrongLower !== null && xuPathoVeryStrongLower !== null"
      :x="props.marginX + xuPathoStrongLower"
      :y="props.marginY"
      :width="xuPathoVeryStrongLower - xuPathoStrongLower"
      :height="props.height"
      :fill="getColorByName('pathogenicStrong')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="pathogenicStrong"
      stroke="none"
    />
    <rect
      v-if="xuPathoVeryStrongLower !== null && xuPathoVeryStrongUpper !== null"
      :x="props.marginX + xuPathoVeryStrongLower"
      :y="props.marginY"
      :width="xuPathoVeryStrongUpper - xuPathoVeryStrongLower"
      :height="props.height"
      :fill="getColorByName('pathogenicVeryStrong')"
      :fill-opacity="FILL_OPACITY"
      data-x-name="pathogenicVeryStrong"
      stroke="none"
    />

    <path
      :stroke="LINE_STROKE"
      :stroke-width="LINE_STROKE_WIDTH"
      :d="`M ${props.marginX} ${props.marginY} l 0 ${props.height} m 0 -${
        props.height / 2
      } l ${width} 0 m 0 -${props.height / 2} l 0 ${props.height}`"
    />
    <circle
      :cx="
        props.marginX +
        (props.width * (0 - props.rangeLower)) /
          (props.rangeUpper - props.rangeLower) +
        (props.width * props.value) / (props.rangeUpper - props.rangeLower)
      "
      :cy="props.marginY + props.height / 2"
      :r="height / 8"
      :fill="circleFill"
      :stroke="LINE_STROKE"
      :stroke-width="LINE_STROKE_WIDTH"
    />

    <text
      :x="
        props.marginX +
        (props.width * (0 - props.rangeLower)) /
          (props.rangeUpper - props.rangeLower) +
        (props.width / (props.rangeUpper - props.rangeLower)) * value
      "
      :y="props.marginY - props.jitter"
      :style="{ textAnchor: 'middle', fontSize: props.fontSize }"
    >
      {{ labelTrans(props.value) }}
    </text>

    <text
      :x="props.marginX"
      :y="props.marginY + props.height + props.jitter"
      :style="{
        textAnchor: 'middle',
        dominantBaseline: 'hanging',
        fontSize: props.fontSize,
      }"
    >
      {{ labelTrans(props.rangeLower) }}
    </text>

    <text
      :x="props.marginX + props.width"
      :y="props.marginY + props.height + props.jitter"
      :style="{
        textAnchor: 'middle',
        dominantBaseline: 'hanging',
        fontSize: props.fontSize,
      }"
    >
      {{ labelTrans(props.rangeUpper) }}
    </text>
  </svg>
</template>

<style scoped></style>
