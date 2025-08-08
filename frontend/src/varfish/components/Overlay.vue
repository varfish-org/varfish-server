<script setup>
/** Helpful component that allows to show a spinner and optionally some text in front of the sibling components.
 *
 * Note that you should wrap the outer component and the Overlay into a <div class="position-relative" /> so
 * only the component and not the whole screen is overlayed.
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  message: String,
})
</script>

<template>
  <div class="varfish-overlay position-absolute" style="inset: 0; z-index: 10">
    <div
      class="position-absolute bg-light"
      style="inset: 0; opacity: 0.85; backdrop-filter: blur(2px)"
    ></div>
    <div
      class="position-absolute"
      style="top: 50%; left: 50%; transform: translateX(-50%) translateY(-50%)"
    >
      <div class="text-center text-muted">
        <span aria-hidden="true" class="spinner-border"></span>
        <br />
        <template v-if="message"> {{ message }} </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
