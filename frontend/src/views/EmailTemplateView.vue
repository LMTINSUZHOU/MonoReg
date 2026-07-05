<template>
  <AdminLayout>
    <PageToolbar>
      <template #left>
        <el-select v-model="filters.activity_id" placeholder="活动" clearable style="width: 220px">
          <el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" />
        </el-select>
        <el-select v-model="filters.type" placeholder="模板类型" clearable style="width: 190px">
          <el-option v-for="type in templateTypeOptions" :key="type.value" :label="type.label" :value="type.value" />
        </el-select>
        <el-button @click="load">筛选</el-button>
      </template>
      <el-button type="primary" @click="openCreate">创建模板</el-button>
    </PageToolbar>

    <section class="panel">
      <div class="panel-body">
        <el-table :data="items" v-loading="loading" empty-text="暂无邮件模板">
          <el-table-column prop="name" label="模板名称" min-width="180" />
          <el-table-column label="类型" min-width="160">
            <template #default="{ row }">{{ templateTypeLabel(row.type) }}</template>
          </el-table-column>
          <el-table-column prop="subject" label="主题" min-width="220" />
          <el-table-column label="启用" width="90">
            <template #default="{ row }">{{ row.enabled ? '是' : '否' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button text @click="openEdit(row)">编辑</el-button>
              <el-button text @click="openPreview(row)">预览</el-button>
              <el-button text @click="openTest(row)">测试</el-button>
              <el-button text @click="remove(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>

    <el-dialog v-model="editorVisible" :title="editingId ? '编辑模板' : '创建模板'" width="760px">
      <el-form :model="editor" label-position="top">
        <div class="grid grid-2">
          <el-form-item label="活动">
            <el-select v-model="editor.activity_id" clearable style="width: 100%">
              <el-option v-for="activity in activities" :key="activity.id" :label="activity.title" :value="activity.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="editor.type" style="width: 100%">
              <el-option v-for="type in templateTypeOptions" :key="type.value" :label="type.label" :value="type.value" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="名称"><el-input v-model="editor.name" /></el-form-item>
        <el-form-item label="主题"><el-input v-model="editor.subject" /></el-form-item>
        <el-form-item label="正文">
          <el-input v-model="editor.body" type="textarea" :rows="10" />
        </el-form-item>
        <div class="variable-strip">
          <span v-for="variable in variables" :key="variable">{{ variable }}</span>
        </div>
        <el-checkbox v-model="editor.enabled">启用模板</el-checkbox>
      </el-form>
      <template #footer>
        <el-button @click="editorVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewVisible" title="模板预览" width="720px">
      <el-form label-position="top">
        <el-form-item label="报名 ID（可选）">
          <el-input-number v-model="previewRegistrationId" :min="1" />
        </el-form-item>
      </el-form>
      <el-button @click="submitPreview">生成预览</el-button>
      <div v-if="previewResult" class="preview-box">
        <strong>{{ previewResult.subject }}</strong>
        <pre>{{ previewResult.body }}</pre>
        <div v-if="previewResult.missing_variables.length" class="muted">缺失变量：{{ previewResult.missing_variables.join(', ') }}</div>
      </div>
    </el-dialog>

    <el-dialog v-model="testVisible" title="发送测试邮件" width="480px">
      <el-form label-position="top">
        <el-form-item label="收件邮箱"><el-input v-model="testEmail" /></el-form-item>
        <el-form-item label="报名 ID（可选）"><el-input-number v-model="testRegistrationId" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="testVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTest">发送</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '../components/layout/AdminLayout.vue'
import PageToolbar from '../components/common/PageToolbar.vue'
import { listActivities } from '../api/activities'
import { createTemplate, deleteTemplate, listTemplates, previewTemplate, sendTestEmail, updateTemplate } from '../api/emails'
import type { Activity, EmailTemplate } from '../api/types'
import { templateTypeLabel, templateTypeOptions } from '../utils/labels'

const loading = ref(false)
const activities = ref<Activity[]>([])
const items = ref<EmailTemplate[]>([])
const filters = reactive({ activity_id: undefined as number | undefined, type: '' })
const variables = ['{{活动名称}}', '{{姓名}}', '{{邮箱}}', '{{手机号}}', '{{报名时间}}', '{{账号}}', '{{密码}}', '{{登录地址}}', '{{报名状态}}']
const editorVisible = ref(false)
const editingId = ref<number>()
const editor = reactive({
  activity_id: undefined as number | undefined,
  name: '',
  type: 'registration_confirm',
  subject: '',
  body: '',
  enabled: true
})
const previewVisible = ref(false)
const previewTemplateId = ref<number>()
const previewRegistrationId = ref<number>()
const previewResult = ref<{ subject: string; body: string; missing_variables: string[] } | null>(null)
const testVisible = ref(false)
const testTemplateId = ref<number>()
const testEmail = ref('')
const testRegistrationId = ref<number>()

async function load() {
  loading.value = true
  try {
    items.value = await listTemplates(filters)
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  const data = await listActivities({ page_size: 200 })
  activities.value = data.items
}

function openCreate() {
  editingId.value = undefined
  Object.assign(editor, { activity_id: filters.activity_id, name: '', type: 'registration_confirm', subject: '', body: '', enabled: true })
  editorVisible.value = true
}

function openEdit(row: EmailTemplate) {
  editingId.value = row.id
  Object.assign(editor, row)
  editorVisible.value = true
}

async function save() {
  if (editingId.value) {
    await updateTemplate(editingId.value, editor)
    ElMessage.success('模板已更新')
  } else {
    await createTemplate(editor)
    ElMessage.success('模板已创建')
  }
  editorVisible.value = false
  load()
}

async function remove(id: number) {
  await ElMessageBox.confirm('确认删除该邮件模板？', '删除模板')
  await deleteTemplate(id)
  ElMessage.success('模板已删除')
  load()
}

function openPreview(row: EmailTemplate) {
  previewTemplateId.value = row.id
  previewResult.value = null
  previewVisible.value = true
}

async function submitPreview() {
  if (!previewTemplateId.value) return
  previewResult.value = await previewTemplate(previewTemplateId.value, previewRegistrationId.value)
}

function openTest(row: EmailTemplate) {
  testTemplateId.value = row.id
  testVisible.value = true
}

async function submitTest() {
  if (!testTemplateId.value || !testEmail.value) return
  await sendTestEmail({ template_id: testTemplateId.value, to_email: testEmail.value, registration_id: testRegistrationId.value })
  testVisible.value = false
  ElMessage.success('测试邮件已发送')
}

onMounted(() => {
  loadMeta()
  load()
})
</script>

<style scoped>
.variable-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.variable-strip span {
  padding: 4px 8px;
  border: 1px solid var(--mono-gray-300);
  border-radius: var(--radius-sm);
  background: var(--mono-gray-50);
  font-size: 12px;
}

.preview-box {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--mono-gray-200);
  border-radius: var(--radius-sm);
  background: var(--mono-gray-50);
}

.preview-box pre {
  white-space: pre-wrap;
}
</style>
