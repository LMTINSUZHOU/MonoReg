<template>
  <AdminLayout>
    <section class="panel" v-loading="loading">
      <div class="panel-header">
        <h2 class="panel-title">报名详情</h2>
        <RouterLink class="mono-link" to="/registrations">返回列表</RouterLink>
      </div>
      <div v-if="registration" class="panel-body detail-grid">
        <div>
          <div class="caption">基本信息</div>
          <dl class="detail-list">
            <dt>姓名</dt><dd>{{ registration.name || '-' }}</dd>
            <dt>邮箱</dt><dd>{{ registration.email }}</dd>
            <dt>手机号</dt><dd>{{ registration.phone || '-' }}</dd>
            <dt>状态</dt><dd><StatusTag :status="registration.status" /></dd>
            <dt>报名时间</dt><dd>{{ registration.submitted_at }}</dd>
          </dl>
          <el-form :model="editForm" label-position="top" class="edit-form">
            <el-form-item label="修改状态">
              <el-select v-model="editForm.status">
                <el-option v-for="status in registrationStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
              </el-select>
            </el-form-item>
            <el-button type="primary" @click="save">保存状态</el-button>
          </el-form>
        </div>
        <div>
          <div class="caption">动态表单数据</div>
          <pre class="json-box">{{ JSON.stringify(registration.form_data, null, 2) }}</pre>
          <div v-if="registration.account" class="account-box">
            <div class="caption">账号</div>
            <strong>{{ registration.account.username }}</strong>
            <StatusTag :status="registration.account.status" />
          </div>
        </div>
      </div>
    </section>
  </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AdminLayout from '../components/layout/AdminLayout.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { getRegistration, updateRegistration } from '../api/registrations'
import type { Registration } from '../api/types'
import { registrationStatusOptions } from '../utils/labels'

const route = useRoute()
const loading = ref(false)
const registration = ref<Registration | null>(null)
const editForm = reactive({ status: '' })

async function load() {
  loading.value = true
  try {
    registration.value = await getRegistration(Number(route.params.id))
    editForm.status = registration.value.status
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!registration.value) return
  await updateRegistration(registration.value.id, { status: editForm.status })
  ElMessage.success('报名状态已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.detail-grid {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 32px;
}

.detail-list {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 12px;
  margin: 16px 0 24px;
}

dt {
  color: var(--mono-gray-500);
}

dd {
  margin: 0;
}

.json-box {
  min-height: 240px;
  padding: 16px;
  overflow: auto;
  border: 1px solid var(--mono-gray-200);
  border-radius: var(--radius-sm);
  background: var(--mono-gray-50);
  color: var(--mono-gray-800);
  font-size: 13px;
}

.account-box {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}
</style>
