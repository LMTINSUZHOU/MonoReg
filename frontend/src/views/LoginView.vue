<template>
  <main class="login-page">
    <section class="login-card panel">
      <div class="login-brand">
        <span class="login-mark">M</span>
        <div>
          <h1>MonoReg</h1>
          <p>竞赛 / 大型活动报名管理系统</p>
        </div>
      </div>
      <el-form :model="form" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名" :error="formErrors.username">
          <el-input v-model="form.username" autocomplete="username" @input="formErrors.username = ''" />
        </el-form-item>
        <el-form-item label="密码" :error="formErrors.password">
          <el-input v-model="form.password" type="password" autocomplete="current-password" show-password @input="formErrors.password = ''" />
        </el-form-item>
        <el-button type="primary" class="login-button" :loading="loading" :disabled="loading" @click="submit">登录</el-button>
      </el-form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const formErrors = reactive({ username: '', password: '' })
const form = reactive({ username: 'admin', password: 'admin123456' })

async function submit() {
  if (loading.value) return
  formErrors.username = ''
  formErrors.password = ''
  if (!form.username) {
    formErrors.username = '请输入用户名'
    ElMessage.error(formErrors.username)
    return
  }
  if (!form.password) {
    formErrors.password = '请输入密码'
    ElMessage.error(formErrors.password)
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: var(--mono-gray-50);
}

.login-card {
  width: min(420px, 100%);
  padding: 32px;
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.login-mark {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 8px;
  background: var(--mono-black);
  color: var(--mono-white);
  font-weight: 750;
}

h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
}

p {
  margin: 4px 0 0;
  color: var(--mono-gray-500);
}

.login-button {
  width: 100%;
  margin-top: 8px;
}
</style>
