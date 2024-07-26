<script setup lang="ts">
import { Query } from '@/seqvars/types'

const model = defineModel<Query>({ required: true })
</script>

<template>
  <v-radio-group>
    <v-radio label="Gene list" value="one"></v-radio>
    <v-radio label="Genomic regions" value="two"></v-radio>
  </v-radio-group>
</template>
