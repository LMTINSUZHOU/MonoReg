<template>
  <AdminLayout>
    <section class="panel form-page">
      <div class="panel-header">
        <h2 class="panel-title">{{ isEdit ? '编辑活动' : '创建活动' }}</h2>
      </div>
      <div class="panel-body">
        <el-form :model="form" label-position="top" class="activity-form">
          <div class="grid grid-2">
            <el-form-item label="活动名称">
              <el-input v-model="form.title" />
            </el-form-item>
            <el-form-item label="报名地址标识">
              <el-input v-model="form.slug" />
            </el-form-item>
          </div>
          <el-form-item label="报名页简介">
            <div class="description-tools">
              <el-upload
                accept=".md,.markdown,text/markdown,text/plain"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="importMarkdownIntro"
              >
                <el-button>导入 Markdown</el-button>
              </el-upload>
              <span class="caption">支持标题、列表、引用、链接、图片和代码块。</span>
            </div>
            <el-input v-model="form.description" type="textarea" :rows="8" placeholder="可直接输入 Markdown 格式简介" />
          </el-form-item>
          <div class="grid grid-2">
            <el-form-item label="开始时间">
              <el-date-picker v-model="form.start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" />
            </el-form-item>
            <el-form-item label="结束时间">
              <el-date-picker v-model="form.end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" />
            </el-form-item>
          </div>
          <div class="grid grid-2">
            <el-form-item label="状态">
              <el-select v-model="form.status">
                <el-option v-for="status in activityStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="最大报名人数">
              <el-input-number v-model="form.max_registrations" :min="0" controls-position="right" />
            </el-form-item>
          </div>
          <div class="switch-grid">
            <el-checkbox v-model="form.need_account">需要账号</el-checkbox>
            <el-checkbox v-model="form.auto_generate_account">报名后自动生成账号</el-checkbox>
            <el-checkbox v-model="form.send_confirm_email">发送报名确认邮件</el-checkbox>
            <el-checkbox v-model="form.send_account_email_immediately">提交后立即发送账号邮件</el-checkbox>
          </div>
          <el-form-item label="登录地址">
            <el-input v-model="form.login_url" placeholder="https://oj.example.com" />
          </el-form-item>
          <div class="form-actions">
            <el-button @click="router.push('/activities')">取消</el-button>
            <el-button type="primary" :loading="loading" @click="save">保存</el-button>
          </div>
        </el-form>
      </div>
    </section>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type UploadFile } from 'element-plus'
import AdminLayout from '../components/layout/AdminLayout.vue'
import { createActivity, getActivity, updateActivity } from '../api/activities'
import { activityStatusOptions } from '../utils/labels'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const isEdit = computed(() => Boolean(route.params.id))
const form = reactive({
  title: '',
  slug: '',
  description: '',
  status: 'draft',
  start_time: '',
  end_time: '',
  max_registrations: undefined as number | undefined,
  need_account: false,
  auto_generate_account: false,
  send_confirm_email: false,
  send_account_email_immediately: false,
  login_url: ''
})

async function load() {
  if (!isEdit.value) return
  const activity = await getActivity(Number(route.params.id))
  Object.assign(form, activity)
}

async function importMarkdownIntro(file: UploadFile) {
  if (!file.raw) return
  if (!/\.(md|markdown|txt)$/i.test(file.name)) {
    ElMessage.error('请选择 Markdown 文件')
    return
  }
  form.description = await file.raw.text()
  ElMessage.success('Markdown 简介已导入')
}

async function save() {
  loading.value = true
  try {
    const payload = { ...form }
    if (payload.max_registrations === 0) payload.max_registrations = undefined
    if (isEdit.value) {
      await updateActivity(Number(route.params.id), payload)
      ElMessage.success('活动已更新')
    } else {
      await createActivity(payload)
      ElMessage.success('活动已创建')
    }
    router.push('/activities')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.activity-form {
  max-width: 840px;
}

.description-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 24px;
  margin-bottom: 18px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
