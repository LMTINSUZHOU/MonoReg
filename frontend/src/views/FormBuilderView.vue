<template>
    <div class="builder">
      <section class="panel type-panel">
        <div class="panel-header"><h2 class="panel-title">字段类型</h2></div>
        <div class="panel-body type-list">
          <button v-for="type in fieldTypeOptions" :key="type.value" class="type-button" @click="addField(type.value)">{{ type.label }}</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h2 class="panel-title">字段列表</h2>
          <el-button type="primary" :loading="saving" :disabled="loading" @click="save">保存字段配置</el-button>
        </div>
        <div class="panel-body" v-loading="loading" element-loading-text="加载字段中">
          <StateBlock
            v-if="!fields.length && !loading"
            title="暂无字段"
            description="添加字段后即可保存报名表单配置。"
            action-label="添加单行文本"
            mark="+"
            @action="addField('text')"
          />
          <div v-for="(field, index) in fields" :key="field.field_key" class="field-row" :class="{ active: selectedIndex === index }" @click="selectedIndex = index">
            <div>
              <strong>{{ field.field_label }}</strong>
              <div class="muted">{{ field.field_key }} · {{ fieldTypeLabel(field.field_type) }}</div>
            </div>
            <div class="field-actions">
              <el-button text @click.stop="move(index, -1)">上移</el-button>
              <el-button text @click.stop="move(index, 1)">下移</el-button>
              <el-button text @click.stop="remove(index)">删除</el-button>
            </div>
          </div>
        </div>
      </section>

      <section class="panel config-panel">
        <div class="panel-header"><h2 class="panel-title">字段配置</h2></div>
        <div class="panel-body">
          <el-form v-if="selectedField" :model="selectedField" label-position="top">
            <el-form-item label="字段名称">
              <el-input v-model="selectedField.field_label" />
            </el-form-item>
            <el-form-item label="字段标识">
              <el-input v-model="selectedField.field_key" :disabled="coreKeys.includes(selectedField.field_key)" />
            </el-form-item>
            <el-form-item label="字段类型">
              <el-select v-model="selectedField.field_type">
                <el-option v-for="type in fieldTypeOptions" :key="type.value" :label="type.label" :value="type.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="占位提示">
              <el-input v-model="selectedField.placeholder" />
            </el-form-item>
            <el-form-item label="帮助文本">
              <el-input v-model="selectedField.help_text" />
            </el-form-item>
            <el-form-item label="选项（一行一个）" v-if="optionTypes.includes(selectedField.field_type)">
              <el-input v-model="optionsText" type="textarea" :rows="5" />
            </el-form-item>
            <el-checkbox v-model="selectedField.required">必填</el-checkbox>
            <el-checkbox v-model="selectedField.show_in_table">列表展示</el-checkbox>
          </el-form>
          <div v-else class="empty-state">选择一个字段进行配置。</div>
        </div>
      </section>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import StateBlock from '../components/common/StateBlock.vue'
import { listFormFields, saveFormFields } from '../api/activities'
import type { FormField } from '../api/types'
import { fieldTypeLabel, fieldTypeOptions } from '../utils/labels'

const route = useRoute()
const activityId = Number(route.params.id)
const loading = ref(false)
const saving = ref(false)
const selectedIndex = ref(0)
const optionTypes = ['select', 'multi_select', 'radio']
const coreKeys = ['name', 'email', 'phone']
const fields = ref<FormField[]>([])
const selectedField = computed(() => fields.value[selectedIndex.value] || null)
const optionsText = computed({
  get: () => selectedField.value?.options_json?.join('\n') || '',
  set: (value: string) => {
    if (selectedField.value) {
      selectedField.value.options_json = value.split('\n').map((item) => item.trim()).filter(Boolean)
    }
  }
})

function coreField(key: string, label: string, type: string, sort: number): FormField {
  return {
    field_key: key,
    field_label: label,
    field_type: type,
    required: key !== 'phone',
    placeholder: '',
    help_text: '',
    options_json: [],
    validation_json: {},
    show_in_table: true,
    sort_order: sort
  }
}

async function load() {
  loading.value = true
  try {
    const data = await listFormFields(activityId)
    fields.value = data.length ? data : [coreField('name', '姓名', 'text', 1), coreField('email', '邮箱', 'email', 2), coreField('phone', '手机号', 'phone', 3)]
  } finally {
    loading.value = false
  }
}

function addField(type: string) {
  const next = fields.value.length + 1
  fields.value.push({
    field_key: `field_${next}`,
    field_label: `字段 ${next}`,
    field_type: type,
    required: false,
    placeholder: '',
    help_text: '',
    options_json: optionTypes.includes(type) ? ['选项一', '选项二'] : [],
    validation_json: {},
    show_in_table: true,
    sort_order: next
  })
  selectedIndex.value = fields.value.length - 1
}

function move(index: number, delta: number) {
  const target = index + delta
  if (target < 0 || target >= fields.value.length) return
  const [item] = fields.value.splice(index, 1)
  fields.value.splice(target, 0, item)
  selectedIndex.value = target
}

function remove(index: number) {
  if (coreKeys.includes(fields.value[index].field_key)) {
    ElMessage.error('核心字段不能删除')
    return
  }
  fields.value.splice(index, 1)
  selectedIndex.value = Math.max(0, index - 1)
}

async function save() {
  if (saving.value) return
  saving.value = true
  try {
    fields.value.forEach((field, index) => {
      field.sort_order = index + 1
    })
    await saveFormFields(activityId, fields.value)
    ElMessage.success('表单字段已保存')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.builder {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr) 320px;
  gap: 16px;
}

.type-list {
  display: grid;
  gap: 8px;
}

.type-button {
  height: 36px;
  border: 1px solid var(--mono-gray-300);
  border-radius: var(--radius-sm);
  background: var(--mono-white);
  color: var(--mono-black);
  text-align: left;
  padding: 0 12px;
  font: inherit;
  cursor: pointer;
}

.type-button:hover {
  border-color: var(--mono-black);
}

.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px;
  border: 1px solid var(--mono-gray-200);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.field-row + .field-row {
  margin-top: 8px;
}

.field-row.active {
  border-color: var(--mono-black);
  background: var(--mono-gray-50);
}

.field-actions {
  display: flex;
  gap: 4px;
}

.empty-state {
  padding: 24px;
  color: var(--mono-gray-500);
  text-align: center;
}

@media (max-width: 1100px) {
  .builder {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .type-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .field-row {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .field-actions {
    flex-wrap: wrap;
  }

  .field-actions .el-button {
    flex: 1 1 calc(33.333% - 4px);
    min-width: 0;
  }
}

@media (max-width: 420px) {
  .type-list {
    grid-template-columns: 1fr;
  }

  .field-actions .el-button {
    flex-basis: 100%;
  }
}
</style>
