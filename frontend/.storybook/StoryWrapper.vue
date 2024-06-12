<template>
  <v-app :theme="themeName" :full-height="false">
    <v-main class="pa-3">
      <slot name="story"></slot>
    </v-main>
  </v-app>
</template>

<script>
export default {
  props: {
    themeName: String
  }
}
</script>
