<template>
    <PageToolbar>
      <template #left>
        <el-select v-model="filters.activity_id" placeholder="活动" clearable style="width: 220px">
          <el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 140px">
          <el-option v-for="status in emailJobStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
        </el-select>
        <el-button :loading="loading" @click="load">筛选</el-button>
      </template>
    </PageToolbar>

    <section class="panel">
      <div class="panel-body">
        <el-table :data="items" v-loading="loading" element-loading-text="加载邮件任务中" empty-text="暂无邮件任务">
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
              <el-button text :loading="actionLoading === `retry-${row.id}`" :disabled="Boolean(actionLoading)" @click="retry(row.id)">重试失败</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <StateBlock
              :title="loadError ? '邮件任务加载失败' : '暂无邮件任务'"
              :description="loadError || '创建批量邮件任务后，可在这里查看发送进度和失败原因。'"
              :action-label="loadError ? '重试' : '刷新列表'"
              :mark="loadError ? '!' : ''"
              :tone="loadError ? 'error' : 'empty'"
              @action="load"
            />
          </template>
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
      <el-table :data="detail?.logs || []" v-loading="detailLoading" element-loading-text="加载日志中" max-height="480" empty-text="暂无日志">
        <el-table-column prop="to_email" label="收件人" min-width="180" />
        <el-table-column prop="subject" label="主题" min-width="220" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }"><StatusTag :status="row.status" :label="emailJobStatusLabel(row.status)" /></template>
        </el-table-column>
        <el-table-column prop="retry_count" label="重试" width="70" />
        <el-table-column prop="error_message" label="失败原因" min-width="220" />
        <template #empty>
          <StateBlock title="暂无日志" description="该任务还没有可展示的邮件发送日志。" />
        </template>
      </el-table>
    </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageToolbar from '../components/common/PageToolbar.vue'
import StatusTag from '../components/common/StatusTag.vue'
import StateBlock from '../components/common/StateBlock.vue'
import { listActivities } from '../api/activities'
import { getEmailJob, listEmailJobs, retryFailedJob } from '../api/emails'
import type { Activity, EmailJob } from '../api/types'
import { emailJobStatusLabel, emailJobStatusOptions, templateTypeLabel } from '../utils/labels'
import { debounce } from '../utils/timing'

const loading = ref(false)
const detailLoading = ref(false)
const actionLoading = ref('')
const loadError = ref('')
const activities = ref<Activity[]>([])
const items = ref<EmailJob[]>([])
const detail = ref<EmailJob | null>(null)
const detailVisible = ref(false)
const total = ref(0)
const filters = reactive({ activity_id: undefined as number | undefined, status: '', page: 1, page_size: 20 })
const debouncedLoad = debounce(() => {
  filters.page = 1
  load()
}, 260)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const data = await listEmailJobs(filters)
    items.value = data.items
    total.value = data.total
  } catch (error) {
    items.value = []
    total.value = 0
    loadError.value = '请检查筛选条件或后端服务状态，然后重试。'
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  const data = await listActivities({ page_size: 200 })
  activities.value = data.items
}

async function openDetail(id: number) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await getEmailJob(id)
  } finally {
    detailLoading.value = false
  }
}

async function retry(id: number) {
  if (actionLoading.value) return
  await ElMessageBox.confirm('确认重试该任务中的失败邮件？', '重试失败邮件')
  actionLoading.value = `retry-${id}`
  try {
    const result = await retryFailedJob(id)
    if (result.enqueued === false) {
      ElMessage.warning('失败邮件已标记重试，但任务未入队')
    } else {
      ElMessage.success('失败邮件已重新入队')
    }
    await load()
  } finally {
    actionLoading.value = ''
  }
}

onMounted(() => {
  loadMeta()
  load()
})

watch(() => [filters.activity_id, filters.status], debouncedLoad)
</script>

<style scoped>
.table-pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
