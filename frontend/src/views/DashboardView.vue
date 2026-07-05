<template>
  <AdminLayout>
    <div class="grid grid-4">
      <section v-for="metric in metrics" :key="metric.label" class="metric panel">
        <div class="metric-label">{{ metric.label }}</div>
        <div class="metric-value">{{ metric.value }}</div>
      </section>
    </div>

    <div class="grid grid-2 dashboard-grid">
      <section class="panel">
        <div class="panel-header">
          <h2 class="panel-title">最近报名</h2>
          <RouterLink class="mono-link" to="/registrations">查看全部</RouterLink>
        </div>
        <div class="panel-body">
          <el-table :data="registrations" v-loading="loading" empty-text="暂无报名数据">
            <el-table-column prop="name" label="姓名" width="82" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column label="状态" width="96">
              <template #default="{ row }"><StatusTag :status="row.status" :label="statusLabel(row.status)" /></template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h2 class="panel-title">最近邮件任务</h2>
          <RouterLink class="mono-link" to="/email-jobs">查看全部</RouterLink>
        </div>
        <div class="panel-body">
          <el-table :data="jobs" v-loading="loading" empty-text="暂无邮件任务">
            <el-table-column label="类型">
              <template #default="{ row }">{{ templateTypeLabel(row.job_type) }}</template>
            </el-table-column>
            <el-table-column label="进度" width="78">
              <template #default="{ row }">{{ row.success_count }}/{{ row.total_count }}</template>
            </el-table-column>
            <el-table-column label="状态" width="88">
              <template #default="{ row }"><StatusTag :status="row.status" :label="emailJobStatusLabel(row.status)" /></template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { listActivities } from '../api/activities'
import { listRegistrations } from '../api/registrations'
import { listAccounts } from '../api/accounts'
import { listEmailJobs } from '../api/emails'
import type { Activity, EmailJob, Registration } from '../api/types'
import { emailJobStatusLabel, statusLabel, templateTypeLabel } from '../utils/labels'

const loading = ref(false)
const activities = ref<Activity[]>([])
const registrations = ref<Registration[]>([])
const jobs = ref<EmailJob[]>([])
const accountTotal = ref(0)
const registrationTotal = ref(0)

const metrics = computed(() => [
  { label: '活动总数', value: activities.value.length },
  { label: '开放活动', value: activities.value.filter((item) => item.status === 'open').length },
  { label: '报名总人数', value: registrationTotal.value },
  { label: '待发送账号', value: accountTotal.value }
])

async function load() {
  loading.value = true
  try {
    const [activityPage, registrationPage, accountPage, jobPage] = await Promise.all([
      listActivities({ page_size: 100 }),
      listRegistrations({ page_size: 8 }),
      listAccounts({ page_size: 1, status: 'ready' }),
      listEmailJobs({ page_size: 8 })
    ])
    activities.value = activityPage.items
    registrations.value = registrationPage.items
    registrationTotal.value = registrationPage.total
    accountTotal.value = accountPage.total
    jobs.value = jobPage.items
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.dashboard-grid {
  margin-top: 16px;
}
</style>
