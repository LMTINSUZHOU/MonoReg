<template>
  <main class="public-page">
    <section class="public-panel panel">
      <div v-if="loading" class="public-loading">正在加载报名页面...</div>
      <StateBlock
        v-else-if="loadError"
        title="报名页面加载失败"
        :description="loadError"
        action-label="重新加载"
        mark="!"
        tone="error"
        @action="load"
      />
      <template v-else-if="success">
        <div class="success-mark">✓</div>
        <h1>报名成功</h1>
        <p class="muted">你的报名信息已提交，请留意后续邮件通知。</p>
        <RouterLink class="mono-link" :to="`/register/${slug}`">继续提交另一份报名</RouterLink>
      </template>
      <template v-else-if="activity">
        <div class="public-header">
          <div class="caption">公开报名</div>
          <h1>{{ activity.title }}</h1>
          <div v-if="activity.description" class="markdown-body" v-html="renderedDescription"></div>
          <StatusTag :status="activity.status" />
        </div>
        <el-form :model="formValues" label-position="top" @submit.prevent="submit">
          <el-form-item
            v-for="field in fields"
            :key="field.field_key"
            :label="field.field_label"
            :required="field.required"
            :error="fieldErrors[field.field_key]"
          >
            <el-input
              v-if="['text', 'email', 'phone', 'number', 'date'].includes(field.field_type)"
              v-model="formValues[field.field_key]"
              :type="field.field_type === 'number' ? 'number' : field.field_type === 'date' ? 'date' : 'text'"
              :placeholder="field.placeholder"
              @input="clearFieldError(field.field_key)"
            />
            <el-input v-else-if="field.field_type === 'textarea'" v-model="formValues[field.field_key]" type="textarea" :rows="4" :placeholder="field.placeholder" @input="clearFieldError(field.field_key)" />
            <el-select v-else-if="field.field_type === 'select'" v-model="formValues[field.field_key]" :placeholder="field.placeholder" @change="clearFieldError(field.field_key)">
              <el-option v-for="option in field.options_json" :key="option" :label="option" :value="option" />
            </el-select>
            <el-select v-else-if="field.field_type === 'multi_select'" v-model="formValues[field.field_key]" multiple :placeholder="field.placeholder" @change="clearFieldError(field.field_key)">
              <el-option v-for="option in field.options_json" :key="option" :label="option" :value="option" />
            </el-select>
            <el-radio-group v-else-if="field.field_type === 'radio'" v-model="formValues[field.field_key]" @change="clearFieldError(field.field_key)">
              <el-radio v-for="option in field.options_json" :key="option" :value="option">{{ option }}</el-radio>
            </el-radio-group>
            <el-checkbox v-else-if="field.field_type === 'checkbox'" v-model="formValues[field.field_key]" @change="clearFieldError(field.field_key)">{{ field.placeholder || '确认' }}</el-checkbox>
            <div v-if="field.help_text" class="field-help">{{ field.help_text }}</div>
          </el-form-item>
          <el-button type="primary" :loading="submitting" :disabled="submitting || activity.status !== 'open'" class="submit-button" @click="submit">提交报名</el-button>
        </el-form>
      </template>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import StatusTag from '../components/common/StatusTag.vue'
import StateBlock from '../components/common/StateBlock.vue'
import { getPublicActivity } from '../api/activities'
import { submitPublicRegistration } from '../api/registrations'
import type { Activity, FormField } from '../api/types'
import { renderMarkdown } from '../utils/markdown'

const route = useRoute()
const slug = String(route.params.slug)
const loading = ref(false)
const submitting = ref(false)
const success = ref(false)
const loadError = ref('')
const fieldErrors = reactive<Record<string, string>>({})
const activity = ref<Activity | null>(null)
const fields = ref<FormField[]>([])
const formValues = reactive<Record<string, unknown>>({})
const renderedDescription = computed(() => renderMarkdown(activity.value?.description || ''))

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const data = await getPublicActivity(slug)
    activity.value = data.activity
    fields.value = data.fields.map((field) => ({
      ...field,
      field_key: field.field_key || field.key || '',
      field_label: field.field_label || field.label || '',
      field_type: field.field_type || field.type || 'text',
      options_json: field.options_json || field.options || []
    }))
    fields.value.forEach((field) => {
      formValues[field.field_key] = field.field_type === 'multi_select' ? [] : ''
      fieldErrors[field.field_key] = ''
    })
  } catch (error) {
    loadError.value = '请确认报名链接是否正确，或稍后重试。'
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (submitting.value) return
  clearFieldErrors()
  if (activity.value?.status !== 'open') {
    ElMessage.error('活动当前不开放报名')
    return
  }
  for (const field of fields.value) {
    const value = formValues[field.field_key]
    if (field.required && (value === '' || value === undefined || value === false || (Array.isArray(value) && !value.length))) {
      fieldErrors[field.field_key] = `请填写 ${field.field_label}`
      ElMessage.error(fieldErrors[field.field_key])
      return
    }
  }
  submitting.value = true
  try {
    const formData: Record<string, unknown> = {}
    for (const field of fields.value) {
      if (!['name', 'email', 'phone'].includes(field.field_key)) {
        formData[field.field_key] = formValues[field.field_key]
      }
    }
    await submitPublicRegistration(slug, {
      name: formValues.name,
      email: formValues.email,
      phone: formValues.phone,
      form_data: formData
    })
    success.value = true
  } finally {
    submitting.value = false
  }
}

function clearFieldError(key: string) {
  fieldErrors[key] = ''
}

function clearFieldErrors() {
  for (const field of fields.value) {
    fieldErrors[field.field_key] = ''
  }
}

onMounted(load)
</script>

<style scoped>
.public-page {
  min-height: 100vh;
  padding: 48px 20px;
  background: var(--mono-gray-50);
}

.public-panel {
  width: min(760px, 100%);
  margin: 0 auto;
  padding: 32px;
}

.public-header {
  margin-bottom: 32px;
}

.public-header h1,
h1 {
  margin: 4px 0 8px;
  font-size: 32px;
  line-height: 1.2;
}

.submit-button {
  width: 100%;
}

.public-panel :deep(.el-form-item__content) {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 6px;
  line-height: 1.5;
}

.public-panel :deep(.el-radio-group),
.public-panel :deep(.el-checkbox) {
  align-self: flex-start;
}

.public-panel :deep(.el-select) {
  width: 100%;
}

.public-panel :deep(.el-form-item__error) {
  position: static;
  width: 100%;
  padding-top: 0;
  line-height: 1.45;
}

.field-help {
  width: 100%;
  margin-top: 0;
  color: var(--mono-gray-500);
  font-size: 12px;
  line-height: 1.45;
}

.success-mark {
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  margin-bottom: 16px;
  border-radius: 50%;
  background: var(--mono-black);
  color: var(--mono-white);
  font-size: 28px;
}

.public-loading {
  padding: 48px;
  color: var(--mono-gray-500);
  text-align: center;
}

@media (max-width: 640px) {
  .public-page {
    padding: 20px 12px;
  }

  .public-panel {
    padding: 20px;
  }

  .public-header {
    margin-bottom: 24px;
  }

  .public-header h1,
  h1 {
    font-size: 24px;
  }

  .public-panel :deep(.el-radio-group) {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }

  .success-mark {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
}
</style>
