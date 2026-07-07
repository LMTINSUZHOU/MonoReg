<template>
    <div class="grid grid-2">
      <section class="panel">
        <div class="panel-header"><h2 class="panel-title">系统配置</h2></div>
        <div class="panel-body">
          <dl class="settings-list">
            <dt>后端健康检查</dt>
            <dd><a class="mono-link" href="/api/health" target="_blank" rel="noreferrer"><code>/api/health</code></a></dd>
            <dt>Swagger 文档</dt>
            <dd><a class="mono-link" href="/docs" target="_blank" rel="noreferrer"><code>/docs</code></a></dd>
            <dt>ReDoc 文档</dt>
            <dd><a class="mono-link" href="/redoc" target="_blank" rel="noreferrer"><code>/redoc</code></a></dd>
            <dt>OpenAPI JSON</dt>
            <dd><a class="mono-link" href="/openapi.json" target="_blank" rel="noreferrer"><code>/openapi.json</code></a></dd>
            <dt>初始化管理员</dt>
            <dd><code>python -m app.scripts.create_admin</code></dd>
            <dt>邮件 Worker</dt>
            <dd><code>python -m app.workers.email_worker</code></dd>
            <dt>公开报名路径</dt>
            <dd><code>/register/:slug</code></dd>
          </dl>
        </div>
      </section>
      <section class="panel">
        <div class="panel-header"><h2 class="panel-title">部署信息</h2></div>
        <div class="panel-body">
          <dl class="settings-list">
            <dt>前端入口</dt>
            <dd><code>http://localhost:5173</code></dd>
            <dt>后端服务</dt>
            <dd><code>http://localhost:8000</code></dd>
            <dt>数据库</dt>
            <dd><code>PostgreSQL :5432</code></dd>
            <dt>队列缓存</dt>
            <dd><code>Redis :6379</code></dd>
          </dl>
        </div>
      </section>
    </div>

    <section class="panel info-panel">
      <div class="panel-header"><h2 class="panel-title">运行约束</h2></div>
      <div class="panel-body">
        <ul class="settings-points">
          <li>账号密码通过服务端密钥加密保存，前端不展示明文密码。</li>
          <li>批量邮件通过 Redis Queue 异步发送，HTTP 请求只创建任务。</li>
          <li>SMTP 可在页面保存，环境变量仍作为部署默认值。</li>
          <li>viewer 角色预留，只读权限由后端依赖限制写操作。</li>
          <li>公开接口位于 <code>/api/public/*</code>，报名提交接口带基础频率限制。</li>
        </ul>
      </div>
    </section>

    <section class="panel info-panel">
      <div class="panel-header"><h2 class="panel-title">常用 API 路径</h2></div>
        <div class="panel-body">
          <div class="api-grid">
            <div v-for="item in apiLinks" :key="item.path" class="api-item">
              <div>
                <div class="api-item__title">{{ item.title }}</div>
                <div class="api-item__desc">{{ item.description }}</div>
              </div>
              <code>{{ item.method }} {{ item.path }}</code>
            </div>
          </div>
        </div>
    </section>

    <section class="panel smtp-panel" v-loading="loading">
      <div class="panel-header">
        <div>
          <h2 class="panel-title">SMTP 设置</h2>
          <div class="caption">当前来源：{{ smtpSourceLabel }}</div>
        </div>
        <el-button type="primary" :loading="saving" @click="saveSmtp">保存 SMTP</el-button>
      </div>
      <div class="panel-body">
        <StateBlock
          v-if="loadError"
          title="SMTP 设置加载失败"
          :description="loadError"
          action-label="重试"
          mark="!"
          tone="error"
          @action="load"
        />
        <el-form v-else :model="smtpForm" label-position="top" class="smtp-form">
          <div class="grid grid-2">
            <el-form-item label="SMTP 主机" :error="smtpErrors.host">
              <el-input v-model="smtpForm.host" placeholder="smtp.example.com" @input="smtpErrors.host = ''" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input-number v-model="smtpForm.port" :min="1" :max="65535" controls-position="right" />
            </el-form-item>
            <el-form-item label="登录账号">
              <el-input v-model="smtpForm.username" placeholder="通常为邮箱地址" />
            </el-form-item>
            <el-form-item :label="smtpPasswordLabel">
              <el-input v-model="smtpForm.password" type="password" show-password autocomplete="new-password" placeholder="留空表示不修改" />
            </el-form-item>
            <el-form-item label="发件人名称">
              <el-input v-model="smtpForm.from_name" />
            </el-form-item>
            <el-form-item label="发件邮箱" :error="smtpErrors.from_email">
              <el-input v-model="smtpForm.from_email" @input="smtpErrors.from_email = ''" />
            </el-form-item>
            <el-form-item label="连接超时（秒）">
              <el-input-number v-model="smtpForm.timeout_seconds" :min="1" :max="120" controls-position="right" />
            </el-form-item>
            <el-form-item label="加密方式">
              <el-switch v-model="smtpForm.use_ssl" active-text="SSL" inactive-text="STARTTLS" />
            </el-form-item>
          </div>
          <el-checkbox v-if="smtpLoaded?.password_configured" v-model="smtpForm.clear_password">清空已保存的 SMTP 密码</el-checkbox>
        </el-form>

        <div v-if="!loadError" class="test-box">
          <h3>发送测试邮件</h3>
          <el-form :model="testForm" label-position="top">
            <div class="grid grid-2">
              <el-form-item label="收件邮箱">
                <el-input v-model="testForm.to_email" />
              </el-form-item>
              <el-form-item label="邮件主题">
                <el-input v-model="testForm.subject" />
              </el-form-item>
            </div>
            <el-form-item label="邮件正文">
              <el-input v-model="testForm.body" type="textarea" :rows="4" />
            </el-form-item>
          </el-form>
          <el-button :loading="testing" @click="sendTest">发送测试邮件</el-button>
        </div>
      </div>
    </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import StateBlock from '../components/common/StateBlock.vue'
import { getSmtpSettings, sendSmtpTest, updateSmtpSettings } from '../api/settings'
import type { SmtpSettings } from '../api/types'

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const loadError = ref('')
const smtpErrors = reactive({ host: '', from_email: '' })
const smtpLoaded = ref<SmtpSettings | null>(null)

const smtpForm = reactive({
  host: '',
  port: 465,
  username: '',
  password: '',
  clear_password: false,
  from_name: 'MonoReg',
  from_email: '',
  use_ssl: true,
  timeout_seconds: 20
})

const testForm = reactive({
  to_email: '',
  subject: 'MonoReg SMTP 测试',
  body: '这是一封来自 MonoReg 的 SMTP 测试邮件。'
})

const smtpSourceLabel = computed(() => (smtpLoaded.value?.source === 'database' ? '系统设置' : '环境变量默认值'))
const smtpPasswordLabel = computed(() => (smtpLoaded.value?.password_configured ? 'SMTP 密码（已配置）' : 'SMTP 密码'))
const apiLinks = [
  { title: '管理员登录', description: '获取后台访问令牌', method: 'POST', path: '/api/auth/login' },
  { title: '活动管理', description: '创建、编辑、发布活动', method: 'GET', path: '/api/admin/activities' },
  { title: '公开报名页', description: '读取报名页活动和字段', method: 'GET', path: '/api/public/activities/{slug}' },
  { title: '提交报名', description: '公开报名提交入口', method: 'POST', path: '/api/public/activities/{slug}/register' },
  { title: '报名数据', description: '后台报名列表和详情', method: 'GET', path: '/api/admin/registrations' },
  { title: 'SMTP 设置', description: '读取和保存系统邮件配置', method: 'GET', path: '/api/admin/settings/smtp' }
]

function fillForm(settings: SmtpSettings) {
  smtpLoaded.value = settings
  Object.assign(smtpForm, {
    host: settings.host,
    port: settings.port,
    username: settings.username || '',
    password: '',
    clear_password: false,
    from_name: settings.from_name,
    from_email: settings.from_email,
    use_ssl: settings.use_ssl,
    timeout_seconds: settings.timeout_seconds
  })
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    fillForm(await getSmtpSettings())
  } catch (error) {
    loadError.value = '请检查登录状态或后端服务状态，然后重试。'
  } finally {
    loading.value = false
  }
}

async function saveSmtp() {
  if (saving.value) return
  smtpErrors.host = ''
  smtpErrors.from_email = ''
  if (!smtpForm.host.trim()) {
    smtpErrors.host = '请填写 SMTP 主机'
    return
  }
  if (!smtpForm.from_email.trim()) {
    smtpErrors.from_email = '请填写发件邮箱'
    return
  }
  saving.value = true
  try {
    const settings = await updateSmtpSettings({
      ...smtpForm,
      password: smtpForm.password || undefined
    })
    fillForm(settings)
    ElMessage.success('SMTP 设置已保存')
  } finally {
    saving.value = false
  }
}

async function sendTest() {
  if (testing.value) return
  if (!testForm.to_email) {
    ElMessage.error('请填写收件邮箱')
    return
  }
  testing.value = true
  try {
    await sendSmtpTest(testForm)
    ElMessage.success('测试邮件已发送')
  } finally {
    testing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.settings-list {
  display: grid;
  grid-template-columns: 130px minmax(0, 1fr);
  gap: 14px;
}

dt {
  color: var(--mono-gray-500);
}

dd {
  margin: 0;
}

code {
  padding: 2px 6px;
  border: 1px solid var(--mono-gray-200);
  border-radius: var(--radius-sm);
  background: var(--mono-gray-50);
  overflow-wrap: anywhere;
}

.settings-points {
  margin: 0;
  padding-left: 18px;
}

.info-panel,
.smtp-panel {
  margin-top: 16px;
}

.api-grid {
  display: grid;
  gap: 10px;
}

.api-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px;
  border: 1px solid var(--mono-gray-200);
  border-radius: var(--radius-sm);
  background: var(--mono-gray-50);
}

.api-item__title {
  color: var(--mono-black);
  font-weight: 650;
}

.api-item__desc {
  margin-top: 2px;
  color: var(--mono-gray-500);
  font-size: 12px;
}

.smtp-form {
  max-width: 920px;
}

.test-box {
  max-width: 920px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--mono-gray-200);
}

.test-box h3 {
  margin: 0 0 14px;
  font-size: 15px;
}

@media (max-width: 760px) {
  .settings-list {
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .settings-list dd {
    margin-bottom: 10px;
  }

  .api-item {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .api-item code {
    white-space: normal;
    word-break: break-all;
  }

  .test-box .el-button {
    width: 100%;
  }
}
</style>
