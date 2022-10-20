<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  params: Object,
})

/** The global router object. */
const router = useRouter()

/** Navigate to the case detail. */
const navigate = () => {
  router.push(`/detail/${props.params.data.sodar_uuid}`)
}
</script>

<template>
  <a href="#" @click.prevent="navigate">{{ params.data.name }}</a>
</template>
