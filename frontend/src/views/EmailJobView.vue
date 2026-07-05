<template>
  <AdminLayout>
    <PageToolbar>
      <template #left>
        <el-select v-model="filters.activity_id" placeholder="活动" clearable style="width: 220px">
          <el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 140px">
          <el-option v-for="status in emailJobStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
        </el-select>
        <el-button @click="load">筛选</el-button>
      </template>
    </PageToolbar>

    <section class="panel">
      <div class="panel-body">
        <el-table :data="items" v-loading="loading" empty-text="暂无邮件任务">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column label="类型" min-width="160">
            <template #default="{ row }">{{ templateTypeLabel(row.job_type) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }"><StatusTag :status="row.status" :label="emailJobStatusLabel(row.status)" /></template>
          </el-table-column>
          <el-table-column label="成功 / 失败 / 总数" width="180">
            <template #default="{ row }">{{ row.success_count }} / {{ row.failed_count }} / {{ row.total_count }}</template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180" />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button text @click="openDetail(row.id)">详情</el-button>
              <el-button text @click="retry(row.id)">重试失败</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          layout="total, sizes, prev, pager, next"
          :total="total"
          class="table-pagination"
          @change="load"
        />
      </div>
    </section>

    <el-dialog v-model="detailVisible" title="邮件任务详情" width="900px">
      <el-table :data="detail?.logs || []" max-height="480" empty-text="暂无日志">
        <el-table-column prop="to_email" label="收件人" min-width="180" />
        <el-table-column prop="subject" label="主题" min-width="220" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }"><StatusTag :status="row.status" :label="emailJobStatusLabel(row.status)" /></template>
        </el-table-column>
        <el-table-column prop="retry_count" label="重试" width="70" />
        <el-table-column prop="error_message" label="失败原因" min-width="220" />
      </el-table>
    </el-dialog>
  </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '../components/layout/AdminLayout.vue'
import PageToolbar from '../components/common/PageToolbar.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { listActivities } from '../api/activities'
import { getEmailJob, listEmailJobs, retryFailedJob } from '../api/emails'
import type { Activity, EmailJob } from '../api/types'
import { emailJobStatusLabel, emailJobStatusOptions, templateTypeLabel } from '../utils/labels'

const loading = ref(false)
const activities = ref<Activity[]>([])
const items = ref<EmailJob[]>([])
const detail = ref<EmailJob | null>(null)
const detailVisible = ref(false)
const total = ref(0)
const filters = reactive({ activity_id: undefined as number | undefined, status: '', page: 1, page_size: 20 })

async function load() {
  loading.value = true
  try {
    const data = await listEmailJobs(filters)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  const data = await listActivities({ page_size: 200 })
  activities.value = data.items
}

async function openDetail(id: number) {
  detail.value = await getEmailJob(id)
  detailVisible.value = true
}

async function retry(id: number) {
  await ElMessageBox.confirm('确认重试该任务中的失败邮件？', '重试失败邮件')
  await retryFailedJob(id)
  ElMessage.success('失败邮件已重新入队')
  load()
}

onMounted(() => {
  loadMeta()
  load()
})
</script>

<style scoped>
.table-pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
