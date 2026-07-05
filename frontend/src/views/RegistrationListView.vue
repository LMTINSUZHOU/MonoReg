<template>
  <AdminLayout>
    <PageToolbar>
      <template #left>
        <el-select v-model="filters.activity_id" placeholder="活动" clearable style="width: 220px">
          <el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" />
        </el-select>
        <el-input v-model="filters.keyword" placeholder="搜索姓名 / 邮箱 / 手机" clearable @keyup.enter="load" />
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 150px">
          <el-option v-for="status in registrationStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
        </el-select>
        <el-button @click="load">筛选</el-button>
      </template>
      <el-button @click="exportFile('csv')">导出 CSV</el-button>
      <el-button @click="exportFile('xlsx')">导出 Excel</el-button>
      <el-button @click="openBatchStatus">批量状态</el-button>
      <el-button @click="openGenerate">生成账号</el-button>
      <el-button type="primary" @click="openSendMail">批量发送邮件</el-button>
    </PageToolbar>

    <section class="panel">
      <div class="panel-body">
        <el-table :data="items" v-loading="loading" empty-text="暂无报名数据" @selection-change="selection = $event">
          <el-table-column type="selection" width="44" />
          <el-table-column prop="name" label="姓名" min-width="100" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="phone" label="手机号" min-width="130" />
          <el-table-column label="状态" width="130">
            <template #default="{ row }"><StatusTag :status="row.status" /></template>
          </el-table-column>
          <el-table-column label="账号" min-width="160">
            <template #default="{ row }">{{ row.account?.username || '-' }}</template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="报名时间" min-width="180" />
          <el-table-column label="操作" width="110" fixed="right">
            <template #default="{ row }">
              <RouterLink class="mono-link" :to="`/registrations/${row.id}`">详情</RouterLink>
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

    <el-dialog v-model="statusDialog" title="批量修改状态" width="420px">
      <el-select v-model="batchStatus" placeholder="目标状态" style="width: 100%">
        <el-option v-for="status in registrationStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
      </el-select>
      <template #footer>
        <el-button @click="statusDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBatchStatus">确认修改</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="generateDialog" title="批量生成账号" width="520px">
      <el-form :model="generateForm" label-position="top">
        <div class="grid grid-2">
          <el-form-item label="前缀"><el-input v-model="generateForm.prefix" /></el-form-item>
          <el-form-item label="起始编号"><el-input-number v-model="generateForm.start_number" :min="1" /></el-form-item>
          <el-form-item label="编号位数"><el-input-number v-model="generateForm.digits" :min="1" /></el-form-item>
          <el-form-item label="密码长度"><el-input-number v-model="generateForm.password_length" :min="8" /></el-form-item>
        </div>
        <el-checkbox v-model="generateForm.overwrite">覆盖已有账号</el-checkbox>
      </el-form>
      <template #footer>
        <el-button @click="generateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitGenerate">生成</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="mailDialog" title="批量发送邮件" width="520px">
      <el-form label-position="top">
        <el-form-item label="邮件模板">
          <el-select v-model="mailTemplateId" style="width: 100%">
            <el-option v-for="template in templates" :key="template.id" :label="`${template.name} · ${templateTypeLabel(template.type)}`" :value="template.id" />
          </el-select>
        </el-form-item>
        <el-checkbox v-model="skipSent">跳过已发送账号邮件</el-checkbox>
      </el-form>
      <template #footer>
        <el-button @click="mailDialog = false">取消</el-button>
        <el-button type="primary" @click="submitSendMail">创建任务</el-button>
      </template>
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
import { generateAccounts } from '../api/accounts'
import { listTemplates, sendBatchEmail } from '../api/emails'
import { batchUpdateRegistrationStatus, exportRegistrations, listRegistrations } from '../api/registrations'
import type { Activity, EmailTemplate, Registration } from '../api/types'
import { registrationStatusOptions, statusLabel, templateTypeLabel } from '../utils/labels'

const loading = ref(false)
const activities = ref<Activity[]>([])
const templates = ref<EmailTemplate[]>([])
const items = ref<Registration[]>([])
const selection = ref<Registration[]>([])
const total = ref(0)
const filters = reactive({ activity_id: undefined as number | undefined, page: 1, page_size: 20, keyword: '', status: '' })
const statusDialog = ref(false)
const batchStatus = ref('approved')
const generateDialog = ref(false)
const mailDialog = ref(false)
const mailTemplateId = ref<number>()
const skipSent = ref(true)
const generateForm = reactive({
  prefix: 'acm2026_',
  start_number: 1,
  digits: 4,
  password_length: 12,
  avoid_ambiguous_chars: true,
  overwrite: false
})

function selectedIds() {
  return selection.value.map((item) => item.id)
}

function ensureSelection() {
  if (!selection.value.length) {
    ElMessage.error('请先选择报名记录')
    return false
  }
  return true
}

async function load() {
  loading.value = true
  try {
    const data = await listRegistrations(filters)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  const [activityPage, templateData] = await Promise.all([listActivities({ page_size: 200 }), listTemplates({})])
  activities.value = activityPage.items
  templates.value = templateData
}

function openBatchStatus() {
  if (ensureSelection()) statusDialog.value = true
}

async function submitBatchStatus() {
  await ElMessageBox.confirm(`确认将 ${selection.value.length} 条报名改为 ${statusLabel(batchStatus.value)}？`, '批量修改状态')
  await batchUpdateRegistrationStatus(selectedIds(), batchStatus.value)
  statusDialog.value = false
  ElMessage.success('状态已更新')
  load()
}

function openGenerate() {
  if (!filters.activity_id) {
    ElMessage.error('请先选择活动')
    return
  }
  if (ensureSelection()) generateDialog.value = true
}

async function submitGenerate() {
  await ElMessageBox.confirm(`确认给 ${selection.value.length} 条报名生成账号？`, '批量生成账号')
  await generateAccounts({ ...generateForm, activity_id: filters.activity_id, registration_ids: selectedIds() })
  generateDialog.value = false
  ElMessage.success('账号生成完成')
  load()
}

function openSendMail() {
  if (!filters.activity_id) {
    ElMessage.error('请先选择活动')
    return
  }
  if (ensureSelection()) mailDialog.value = true
}

async function submitSendMail() {
  if (!mailTemplateId.value || !filters.activity_id) return
  await ElMessageBox.confirm(`确认创建 ${selection.value.length} 封邮件的发送任务？`, '批量发送邮件')
  const result = await sendBatchEmail({
    activity_id: filters.activity_id,
    template_id: mailTemplateId.value,
    registration_ids: selectedIds(),
    skip_sent: skipSent.value
  })
  mailDialog.value = false
  ElMessage.success(`邮件任务已创建：#${result.job_id}`)
}

async function exportFile(format: 'csv' | 'xlsx') {
  if (!filters.activity_id) {
    ElMessage.error('导出前请选择活动')
    return
  }
  const response = await exportRegistrations({ ...filters, format })
  const url = URL.createObjectURL(response.data)
  const link = document.createElement('a')
  link.href = url
  link.download = `registrations.${format}`
  link.click()
  URL.revokeObjectURL(url)
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
