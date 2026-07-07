<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <RouterLink to="/dashboard" class="brand">
        <span class="brand-mark">M</span>
        <span>MonoReg</span>
      </RouterLink>
      <nav class="nav-stack">
        <RouterLink v-for="item in items" :key="item.path" :to="item.path" class="nav-item">
          <component :is="item.icon" class="nav-icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>
    <section class="admin-main">
      <header class="topbar">
        <div>
          <div class="caption">报名运营</div>
          <h1>{{ title }}</h1>
        </div>
        <div class="topbar-actions">
          <el-input v-model="searchText" placeholder="搜索活动、报名、账号" clearable class="topbar-search" />
          <el-dropdown>
            <button class="user-button">{{ auth.user?.username || 'admin' }}</button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="content">
        <slot />
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Box,
  Calendar,
  HomeFilled,
  Key,
  Message,
  Promotion,
  Setting,
  Tickets
} from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const searchText = ref('')

const items = computed(() => [
  { label: '控制台', path: '/dashboard', icon: HomeFilled },
  { label: '活动管理', path: '/activities', icon: Calendar },
  { label: '报名管理', path: '/registrations', icon: Tickets },
  { label: '账号管理', path: '/accounts', icon: Key },
  { label: '邮件模板', path: '/email-templates', icon: Message },
  { label: '邮件任务', path: '/email-jobs', icon: Promotion },
  { label: '系统设置', path: '/settings', icon: Setting },
  { label: '公开报名', path: '/activities', icon: Box }
])

const title = computed(() => {
  const match = items.value.find((item) => route.path.startsWith(item.path) && item.path !== '/')
  if (route.path.includes('/activities/new')) return '创建活动'
  if (route.path.includes('/edit')) return '编辑活动'
  if (route.path.includes('/form')) return '表单配置'
  return match?.label || 'MonoReg'
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
