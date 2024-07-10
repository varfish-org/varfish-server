<script setup lang="ts">
import VarFishLogo from '@/varfish/components/VarFishLogo.vue'

const navbarHidden = defineModel('navbarHidden', {
  type: Boolean,
  default: true,
})
</script>

<template>
  <v-app-bar color="primary" density="compact">
    <template #prepend>
      <v-app-bar-nav-icon
        @click="navbarHidden = !navbarHidden"
      ></v-app-bar-nav-icon>
    </template>

    <v-app-bar-title>
      <div class="d-flex">
        <VarFishLogo />
        <div class="pl-2">VarFish</div>
      </div>
    </v-app-bar-title>
  </v-app-bar>
</template>
