<template>
  <Vueform size="lg" :schema="schema" @change="handleChange" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface Schema {
  [key: string]: any // Allows dynamic keys with any value type
}

// const config = {
//   "name": "QTrobot AI Data Assistant",
//   "description": "A powerful, on-device AI assistant capable of engaging in natural voice conversations",
//   "parameters": [
//     { "name": "param1", "type": "bool", "label": "Scene undrestanding", "description": "enable scene undrestanding using vlm", "default": true },

//     {
//       "name": "param2", "type": "int", "label": "Parameter 2", "default": 4,
//       "description": "an integer number",
//       "ui": { "element": "slider", "min": 1, "max": 10 }
//     },
//     { "name": "param3", "type": "float", "label": "Parameter 3", "default": 7.5 },

//     {
//       "name": "param4", "type": "str", "label": "Parameter 4", "default": "b",
//       "description": "an integer number",
//       "ui": { "element": "select", "items": ["a", "b", "c"] }
//     },

//     {
//       "name": "param5", "type": "list", "label": "Parameter 5", "default": ["a", "b"],
//       "description": "a list of strings",
//       "ui": { "create": true, "items": ["a", "b", "c"] }
//     },

//     {
//       "name": "param6", "type": "str", "label": "Parameter 6", "default": "",
//       "description": "a long text",
//       "ui": { "element": "textarea" }
//     },


//   ]
// }

const schema = ref<Schema>({})
let timer = ref<any>(null)

const renderBoolSchema = (schema:any, param:any) => {
  let { name, label, description } = param
  label = label || name
  schema.value[name] = {
    type: 'toggle',
    label: label,
    info: description,
    default: param.default,
    columns: { container: 12, label: 11, wrapper: 12 }
  }
  return schema
}

const renderNumberSchema = (schema:any, param:any) => {
  let { name, label, ui, type, description } = param
  label = label || name
  let rules = []
  if (type == 'int') rules.push('integer')
  if (ui?.min) rules.push(`min:${ui.min}`)
  if (ui?.max) rules.push(`max:${ui.max}`)
  if (ui?.element == 'slider') {
    schema.value[name] = {
      type: 'slider',
      min: ui.min,
      max: ui.max,
      label: label,
      info: description,
      default: param.default,
      showTooltip: 'focus',
      columns: { container: 12, label: 5, wrapper: 12 }
    }

  }
  else {
    schema.value[name] = {
      type: 'text',
      inputType: 'number',
      label: label,
      info: description,
      default: param.default,
      rules: rules,
      columns: { container: 12, label: 8, wrapper: 12 }
    }
  }
  return schema
}


const renderStringSchema = (schema:any, param:any) => {
  let { name, label, ui, description } = param
  label = label || name
  // text, password, email, date, textarea, select
  const element = ui?.element || 'text'
  const rules:any[] = []

  if (element == 'textarea') {
    schema.value[name] = {
      type: 'textarea',
      label: label,
      info: description,
      default: param.default,
      rules: rules,
      autogrow: true,
      // columns: { container: 12, label: 5, wrapper: 12 }
    }
  }
  else if (element == 'select') {
    schema.value[name] = {
      type: 'select',
      label: label,
      info: description,
      default: param.default,
      items: ui?.items,
      columns: { container: 12, label: 5, wrapper: 12 }
    }
  }
  else if (['text', 'password', 'email', 'date'].includes(element)) {
    if (element == 'email') rules.push('email')
    schema.value[name] = {
      type: 'text',
      inputType: element,
      label: label,
      info: description,
      default: param.default,
      rules: rules,
      columns: { container: 12, label: 5, wrapper: 12 }
    }
  }
}


const renderListSchema = (schema:any, param:any) => {
  let { name, label, ui, description } = param
  label = label || name
  const create = (ui?.create !== undefined) ? ui?.create : true
  const items = ui?.items || param.default
  schema.value[name] = {
    type: 'tags',
    create: create,
    label: label,
    info: description,
    items: items,
    default: param.default,
    columns: { container: 12, label: 5, wrapper: 12 }
  }
}

const renderUISchema = (schema:any, param:any) => {
  const { name, type } = param
  if (!name || !type) return schema

  switch (type) {
    case 'bool':
      renderBoolSchema(schema, param)
      break;
    case 'int':
      renderNumberSchema(schema, param)
      break;
    case 'float':
      renderNumberSchema(schema, param)
      break;
    case 'str':
      renderStringSchema(schema, param)
      break;
    case 'list':
      renderListSchema(schema, param)
      break;

    default:
      break;
  }
  return schema
}

// @ts-ignore
onMounted(async () => {  
  const response = await axios.get('/api/config')
  console.log(response.data)
  const { parameters, name, description } = response.data
  document.title = name || 'Paramify'

  schema.value['title'] = {
    type: 'static',
    content: name,
    description: description,
    tag: 'h2',
  }

  let i = 0
  schema.value[`divider${i++}`] = { type: 'static', tag: 'hr', }
  for (const param of parameters) {
    // schema.value[`divider${i++}`] = { type: 'static', tag: 'hr', }
    renderUISchema(schema, param)
  }
})

// Debounce function
// @ts-ignore
const debounce = (func:any, timeout = 300) => {
  return (...args:any[]) => {

    if(timer.value) clearTimeout(timer.value)
    timer.value = setTimeout(() => {
      func.apply(this, args)
    }, timeout)
  }
}

// @ts-ignore
const handleChange = debounce(async (newValue:any, oldValue:any, form$:any) => {
  // Determine changed fields
  const changedFields = Object.keys(newValue).filter(
    (key) => (newValue[key] !== oldValue[key] && oldValue[key] !== undefined)
  )

  let updatedData:any = {}
  changedFields.forEach((field) => {
    updatedData[field] = newValue[field]
    // console.log(`Field "${field}" changed to:`, newValue[field])
  })

  // Check if updatedData contains any changes
  if (Object.keys(updatedData).length === 0) return
  
  form$.messageBag.clear()  
  try {
    const response:any = await axios.post('/api/update', updatedData)
    console.log('Changes sent to server:', updatedData, response.data)        
    if(response?.data?.status != 'success') {
      form$.messageBag.append(`Failed to store value of "${Object.keys(updatedData)}"`)
    }
  } catch (error) {
    console.error('Failed to send data:', error)
    form$.messageBag.append(`Failed to store value of "${Object.keys(updatedData)}"`)
  }

}, 1000)

</script>
