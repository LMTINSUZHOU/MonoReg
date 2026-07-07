<template>
  <div class="state-block" :data-tone="tone" role="status" aria-live="polite">
    <div v-if="mark" class="state-block__mark">{{ mark }}</div>
    <div class="state-block__title">{{ title }}</div>
    <p v-if="description" class="state-block__description">{{ description }}</p>
    <div v-if="actionLabel || $slots.default" class="state-block__actions">
      <el-button v-if="actionLabel" size="small" @click="$emit('action')">{{ actionLabel }}</el-button>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    description?: string
    actionLabel?: string
    mark?: string
    tone?: 'empty' | 'error' | 'info'
  }>(),
  {
    description: '',
    actionLabel: '',
    mark: '',
    tone: 'empty'
  }
)

defineEmits<{
  action: []
}>()
</script>
