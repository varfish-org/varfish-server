<script setup lang="ts">
/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  flag?: string
}>()
</script>

<template>
  <span>
    <i-fa-solid-star v-if="flag === 'flag_bookmarked'" />
    <i-mdi-dice-5 v-else-if="flag === 'flag_incidental'" />
    <i-fa-solid-flask v-else-if="flag === 'flag_for_validation'" />
    <i-fa-solid-heart v-else-if="flag === 'flag_candidate'" />
    <i-fa-solid-flag-checkered v-else-if="flag === 'flag_final_causative'" />
    <i-cil-link-broken v-else-if="flag === 'flag_no_disease_association'" />
    <i-fa-solid-thumbs-up v-else-if="flag === 'flag_segregates'" />
    <i-fa-solid-thumbs-down v-else-if="flag === 'flag_doesnt_segregate'" />
    <template v-else>NO FLAG</template>
  </span>
</template>
