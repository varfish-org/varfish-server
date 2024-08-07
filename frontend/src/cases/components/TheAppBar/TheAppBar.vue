<script setup lang="ts">
import VarFishLogo from '@/varfish/components/VarFishLogo.vue'
import 'iconify-icon'

const navbarHidden = defineModel('navbarHidden', {
  type: Boolean,
  default: true,
})
</script>

<template>
  <v-app-bar color="primary" density="compact">
    <template #prepend>
      <v-btn
        rounded="xl"
        icon=""
        @click="navbarHidden = !navbarHidden"
        :title="`${navbarHidden ? 'Show' : 'Hide'} the left sidebar.`"
      >
        <iconify-icon
          :icon="`material-symbols:left-panel-${navbarHidden ? 'open' : 'close'}`"
          style="font-size: 24px"
        ></iconify-icon>
      </v-btn>
    </template>

    <v-app-bar-title>
      <div class="d-flex">
        <VarFishLogo />
        <div class="pl-2">VarFish</div>
      </div>
    </v-app-bar-title>
  </v-app-bar>
</template>
