<script setup>
const props = defineProps({
  flag: String,
})
</script>

<template>
  <span>
    <i-fa-solid-star v-if="flag === 'flag_bookmarked'" />
    <i-fa-solid-flask v-else-if="flag === 'flag_for_validation'" />
    <i-fa-solid-heart v-else-if="flag === 'flag_candidate'" />
    <i-fa-solid-flag-checkered v-else-if="flag === 'flag_final_causative'" />
    <i-cil-link-broken v-else-if="flag === 'flag_no_disease_association'" />
    <i-fa-solid-thumbs-up v-else-if="flag === 'flag_segregates'" />
    <i-fa-solid-thumbs-down v-else-if="flag === 'flag_doesnt_segregate'" />
    <template v-else>NO FLAG</template>
  </span>
</template>
