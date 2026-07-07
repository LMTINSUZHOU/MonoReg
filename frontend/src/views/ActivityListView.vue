<template>
    <PageToolbar>
      <template #left>
        <el-input v-model="filters.keyword" placeholder="搜索活动名称 / slug" clearable @keyup.enter="load" />
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 140px">
          <el-option v-for="status in activityStatusOptions" :key="status.value" :label="status.label" :value="status.value" />
        </el-select>
        <el-button :loading="loading" @click="load">筛选</el-button>
      </template>
      <el-button type="primary" @click="router.push('/activities/new')">创建活动</el-button>
    </PageToolbar>

    <section class="panel">
      <div class="panel-body">
        <el-table :data="items" v-loading="loading" element-loading-text="加载活动中" empty-text="暂无活动">
          <el-table-column prop="title" label="活动名称" min-width="220" />
          <el-table-column prop="slug" label="Slug" min-width="150" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }"><StatusTag :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="max_registrations" label="人数上限" width="100" />
          <el-table-column label="报名链接" min-width="150">
            <template #default="{ row }">
              <RouterLink class="mono-link" :to="`/register/${row.slug}`">公开报名</RouterLink>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="360" fixed="right">
            <template #default="{ row }">
              <el-button text @click="router.push(`/activities/${row.id}/edit`)">编辑</el-button>
              <el-button text @click="router.push(`/activities/${row.id}/form`)">表单</el-button>
              <el-button text :loading="actionLoading === `publish-${row.id}`" :disabled="Boolean(actionLoading)" @click="publish(row.id)">发布</el-button>
              <el-button text :loading="actionLoading === `close-${row.id}`" :disabled="Boolean(actionLoading)" @click="close(row.id)">关闭</el-button>
              <el-button text :loading="actionLoading === `duplicate-${row.id}`" :disabled="Boolean(actionLoading)" @click="duplicate(row.id)">复制</el-button>
              <el-button text :loading="actionLoading === `delete-${row.id}`" :disabled="Boolean(actionLoading)" @click="remove(row.id)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <StateBlock
              :title="loadError ? '活动加载失败' : '暂无活动'"
              :description="loadError || '创建第一个活动后即可配置表单、发布报名链接。'"
              :action-label="loadError ? '重试' : '创建活动'"
              :mark="loadError ? '!' : '+'"
              :tone="loadError ? 'error' : 'empty'"
              @action="loadError ? load() : router.push('/activities/new')"
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
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageToolbar from '../components/common/PageToolbar.vue'
import StatusTag from '../components/common/StatusTag.vue'
import StateBlock from '../components/common/StateBlock.vue'
import {
  closeActivity,
  deleteActivity,
  duplicateActivity,
  listActivities,
  publishActivity
} from '../api/activities'
import type { Activity } from '../api/types'
import { activityStatusOptions } from '../utils/labels'
import { debounce } from '../utils/timing'

const router = useRouter()
const loading = ref(false)
const actionLoading = ref('')
const loadError = ref('')
const items = ref<Activity[]>([])
const total = ref(0)
const filters = reactive({ page: 1, page_size: 20, keyword: '', status: '' })
const debouncedLoad = debounce(() => {
  filters.page = 1
  load()
}, 260)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const data = await listActivities(filters)
    items.value = data.items
    total.value = data.total
  } catch (error) {
    items.value = []
    total.value = 0
    loadError.value = '请检查网络或后端服务状态，然后重试。'
  } finally {
    loading.value = false
  }
}

async function publish(id: number) {
  await runAction(`publish-${id}`, async () => {
    await publishActivity(id)
    ElMessage.success('活动已发布')
    await load()
  })
}

async function close(id: number) {
  await runAction(`close-${id}`, async () => {
    await closeActivity(id)
    ElMessage.success('活动已关闭')
    await load()
  })
}

async function duplicate(id: number) {
  await runAction(`duplicate-${id}`, async () => {
    await duplicateActivity(id)
    ElMessage.success('活动已复制')
    await load()
  })
}

async function remove(id: number) {
  await ElMessageBox.confirm('确认删除该活动及其报名数据？', '删除活动')
  await runAction(`delete-${id}`, async () => {
    await deleteActivity(id)
    ElMessage.success('活动已删除')
    await load()
  })
}

async function runAction(key: string, action: () => Promise<void>) {
  if (actionLoading.value) return
  actionLoading.value = key
  try {
    await action()
  } finally {
    actionLoading.value = ''
  }
}

onMounted(load)

watch(() => [filters.keyword, filters.status], debouncedLoad)
</script>

<style scoped>
.table-pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
