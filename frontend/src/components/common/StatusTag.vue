<template>
  <span class="status-tag" :data-status="status">{{ label || statusLabel(status) }}</span>
</template>

<script setup lang="ts">
import { statusLabel } from '../../utils/labels'

defineProps<{ status: string; label?: string }>()
</script>
