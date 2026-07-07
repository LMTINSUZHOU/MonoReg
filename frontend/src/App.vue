<template>
  <RouterView v-slot="{ Component, route }">
    <component v-if="route.meta.public" :is="Component" :key="route.fullPath" />
    <AdminLayout v-else>
      <Transition name="page-fade-up" mode="out-in">
        <div :key="route.fullPath" class="content-page">
          <component :is="Component" />
        </div>
      </Transition>
    </AdminLayout>
  </RouterView>
</template>

<script setup lang="ts">
import AdminLayout from './components/layout/AdminLayout.vue'
</script>
