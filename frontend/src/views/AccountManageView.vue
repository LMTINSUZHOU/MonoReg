<template>
    <PageToolbar>
      <template #left>
        <el-select v-model="filters.activity_id" placeholder="活动" clearable style="width: 220px">
          <el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" />
        </el-select>
        <el-input v-model="filters.keyword" placeholder="搜索账号 / 邮箱 / 姓名" clearable @keyup.enter="load" />
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 130px">
          <el-option v-for="status in accountStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
        </el-select>
        <el-button :loading="loading" @click="load">筛选</el-button>
      </template>
      <el-button :disabled="Boolean(operationLoading)" @click="generateDialog = true">按 ID 生成账号</el-button>
      <el-button :disabled="Boolean(operationLoading)" @click="importDialog = true">导入账号</el-button>
      <el-button :disabled="!selection.length || Boolean(operationLoading)" :loading="operationLoading === 'reset'" @click="resetSelected">重置密码</el-button>
      <el-button type="primary" :disabled="!selection.length || Boolean(operationLoading)" @click="sendAccountMail">发送账号邮件</el-button>
    </PageToolbar>

    <Transition name="batch-bar">
      <div v-if="selection.length" class="batch-bar">
        <div class="batch-bar__main">
          <span>已选择 <strong>{{ selection.length }}</strong> 个账号</span>
          <span class="batch-bar__hint">可重置密码或创建账号邮件任务</span>
          <span v-if="accountActivityMixed" class="batch-bar__warning">包含多个活动</span>
        </div>
        <div class="batch-bar__actions">
          <el-button size="small" @click="clearSelection">清空选择</el-button>
        </div>
      </div>
    </Transition>

    <section class="panel">
      <div class="panel-body">
        <el-table ref="tableRef" :data="items" v-loading="loading" element-loading-text="加载账号中" empty-text="暂无账号" @selection-change="selection = $event">
          <el-table-column type="selection" width="44" />
          <el-table-column prop="username" label="账号" min-width="160" />
          <el-table-column label="报名用户" min-width="180">
            <template #default="{ row }">{{ row.registration?.name || '-' }} · {{ row.registration?.email }}</template>
          </el-table-column>
          <el-table-column label="账号状态" width="120">
            <template #default="{ row }"><StatusTag :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="sent_at" label="发送时间" min-width="170" />
          <template #empty>
            <StateBlock
              :title="loadError ? '账号加载失败' : '暂无账号'"
              :description="loadError || '选择报名记录生成账号，或导入已有账号数据。'"
              :action-label="loadError ? '重试' : '按 ID 生成账号'"
              :mark="loadError ? '!' : ''"
              :tone="loadError ? 'error' : 'empty'"
              @action="loadError ? load() : (generateDialog = true)"
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

    <el-dialog v-model="generateDialog" title="按报名 ID 生成账号" width="560px">
      <el-form :model="generateForm" label-position="top">
        <el-form-item label="活动"><el-select v-model="generateForm.activity_id" style="width: 100%"><el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" /></el-select></el-form-item>
        <el-form-item label="报名 ID（一行或逗号分隔）"><el-input v-model="registrationIdsText" type="textarea" :rows="4" /></el-form-item>
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
        <el-button type="primary" :loading="operationLoading === 'generate'" @click="submitGenerate">生成</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialog" title="导入账号" width="480px">
      <el-form label-position="top">
        <el-form-item label="活动"><el-select v-model="importActivityId" style="width: 100%"><el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" /></el-select></el-form-item>
        <el-upload :auto-upload="false" :limit="1" :on-change="onFileChange">
          <el-button>选择 CSV / XLSX</el-button>
        </el-upload>
        <el-checkbox v-model="importOverwrite">覆盖已有账号</el-checkbox>
      </el-form>
      <template #footer>
        <el-button @click="importDialog = false">取消</el-button>
        <el-button type="primary" :loading="operationLoading === 'import'" @click="submitImport">导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="mailDialog" title="发送账号邮件" width="480px">
      <el-select v-model="accountTemplateId" placeholder="选择账号邮件模板" style="width: 100%">
        <el-option v-for="template in accountTemplates" :key="template.id" :label="template.name" :value="template.id" />
      </el-select>
      <template #footer>
        <el-button @click="mailDialog = false">取消</el-button>
        <el-button type="primary" :loading="operationLoading === 'mail'" @click="submitAccountMail">创建任务</el-button>
      </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import PageToolbar from '../components/common/PageToolbar.vue'
import StatusTag from '../components/common/StatusTag.vue'
import StateBlock from '../components/common/StateBlock.vue'
import { listActivities } from '../api/activities'
import { generateAccounts, importAccounts, listAccounts, resetPasswords } from '../api/accounts'
import { listTemplates, sendBatchEmail } from '../api/emails'
import type { Account, Activity, EmailTemplate } from '../api/types'
import { accountStatusOptions } from '../utils/labels'
import { debounce } from '../utils/timing'

const loading = ref(false)
const operationLoading = ref('')
const loadError = ref('')
const activities = ref<Activity[]>([])
const templates = ref<EmailTemplate[]>([])
const items = ref<Account[]>([])
const selection = ref<Account[]>([])
const tableRef = ref()
const total = ref(0)
const filters = reactive({ activity_id: undefined as number | undefined, keyword: '', status: '', page: 1, page_size: 20 })
const generateDialog = ref(false)
const importDialog = ref(false)
const mailDialog = ref(false)
const registrationIdsText = ref('')
const selectedFile = ref<UploadFile | null>(null)
const importActivityId = ref<number>()
const importOverwrite = ref(false)
const accountTemplateId = ref<number>()
const generateForm = reactive({
  activity_id: undefined as number | undefined,
  prefix: 'acm2026_',
  start_number: 1,
  digits: 4,
  password_length: 12,
  avoid_ambiguous_chars: true,
  overwrite: false
})

const accountTemplates = computed(() => templates.value.filter((item) => item.type === 'account_info'))
const accountActivityMixed = computed(() => new Set(selection.value.map((item) => item.activity_id)).size > 1)
const debouncedLoad = debounce(() => {
  filters.page = 1
  load()
}, 260)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const data = await listAccounts(filters)
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
  const [activityPage, templateData] = await Promise.all([listActivities({ page_size: 200 }), listTemplates({})])
  activities.value = activityPage.items
  templates.value = templateData
}

function idsFromText() {
  return registrationIdsText.value.split(/[\n,，\s]+/).map((item) => Number(item)).filter(Boolean)
}

async function submitGenerate() {
  if (operationLoading.value) return
  const registration_ids = idsFromText()
  if (!generateForm.activity_id || !registration_ids.length) {
    ElMessage.error('请选择活动并填写报名 ID')
    return
  }
  await ElMessageBox.confirm(`确认生成 ${registration_ids.length} 个账号？`, '生成账号')
  operationLoading.value = 'generate'
  try {
    await generateAccounts({ ...generateForm, registration_ids })
    generateDialog.value = false
    ElMessage.success('账号生成完成')
    await load()
  } finally {
    operationLoading.value = ''
  }
}

function onFileChange(file: UploadFile) {
  selectedFile.value = file
}

async function submitImport() {
  if (operationLoading.value) return
  if (!selectedFile.value?.raw || !importActivityId.value) {
    ElMessage.error('请选择活动和导入文件')
    return
  }
  const form = new FormData()
  form.append('file', selectedFile.value.raw)
  form.append('activity_id', String(importActivityId.value))
  form.append('overwrite', String(importOverwrite.value))
  operationLoading.value = 'import'
  try {
    await importAccounts(form)
    importDialog.value = false
    selectedFile.value = null
    ElMessage.success('账号导入完成')
    await load()
  } finally {
    operationLoading.value = ''
  }
}

async function resetSelected() {
  if (operationLoading.value) return
  if (!selection.value.length) {
    ElMessage.error('请先选择账号')
    return
  }
  await ElMessageBox.confirm(`确认重置 ${selection.value.length} 个账号的密码？`, '重置密码')
  operationLoading.value = 'reset'
  try {
    await resetPasswords(selection.value.map((item) => item.id), 12)
    clearSelection()
    ElMessage.success('密码已重置')
    await load()
  } finally {
    operationLoading.value = ''
  }
}

function sendAccountMail() {
  if (!selection.value.length) {
    ElMessage.error('请先选择账号')
    return
  }
  if (accountActivityMixed.value) {
    ElMessage.error('请选择同一活动下的账号')
    return
  }
  mailDialog.value = true
}

async function submitAccountMail() {
  const first = selection.value[0]
  if (!first || !accountTemplateId.value) return
  if (operationLoading.value) return
  await ElMessageBox.confirm(`确认创建 ${selection.value.length} 封账号邮件任务？`, '发送账号邮件')
  operationLoading.value = 'mail'
  try {
    const result = await sendBatchEmail({
      activity_id: first.activity_id,
      template_id: accountTemplateId.value,
      registration_ids: selection.value.map((item) => item.registration_id),
      skip_sent: true
    })
    mailDialog.value = false
    clearSelection()
    if (result.enqueued === false) {
      ElMessage.warning(`邮件任务已创建但未入队：#${result.job_id}`)
    } else {
      ElMessage.success(`邮件任务已创建：#${result.job_id}`)
    }
  } finally {
    operationLoading.value = ''
  }
}

function clearSelection() {
  tableRef.value?.clearSelection()
  selection.value = []
}

onMounted(() => {
  loadMeta()
  load()
})

watch(() => [filters.activity_id, filters.keyword, filters.status], debouncedLoad)
</script>

<style scoped>
.table-pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
