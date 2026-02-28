import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { vi } from 'vitest'

// Mock QuestionCard 组件（简化版）
const QuestionCard = {
  name: 'QuestionCard',
  props: {
    question: {
      type: Object,
      required: true
    },
    readonly: {
      type: Boolean,
      default: false
    }
  },
  template: `
    <div class="question-card" @click="$emit('select', question.id)">
      <div class="question-stem">{{ question.stem }}</div>
      <div class="options">
        <div v-for="(opt, idx) in question.options" :key="idx" class="option-item">
          {{ opt.label }}. {{ opt.content }}
        </div>
      </div>
      <button v-if="!readonly" class="edit-button">编辑</button>
    </div>
  `
}

// 测试数据
const mockQuestion = {
  id: 'q-101',
  questionNumber: 1,
  type: 'single_choice',
  difficulty: 'easy',
  stem: '测试题干内容',
  options: [
    { label: 'A', content: '选项A' },
    { label: 'B', content: '选项B' },
    { label: 'C', content: '选项C' },
    { label: 'D', content: '选项D' }
  ],
  answer: 'A',
  status: 'active'
}

describe('QuestionCard 组件', () => {
  it('应正确渲染题干内容', () => {
    const wrapper = mount(QuestionCard, {
      props: { question: mockQuestion }
    })
    
    expect(wrapper.text()).toContain('测试题干内容')
  })

  it('应正确渲染所有选项', () => {
    const wrapper = mount(QuestionCard, {
      props: { question: mockQuestion }
    })
    
    const optionItems = wrapper.findAll('.option-item')
    expect(optionItems.length).toBe(4)
    expect(wrapper.text()).toContain('选项A')
    expect(wrapper.text()).toContain('选项B')
  })

  it('点击卡片应触发 select 事件', async () => {
    const wrapper = mount(QuestionCard, {
      props: { question: mockQuestion }
    })
    
    await wrapper.trigger('click')
    
    const emitted = wrapper.emitted('select')
    expect(emitted).toBeTruthy()
    expect(emitted?.[0]).toEqual(['q-101'])
  })

  it('readonly 模式下应隐藏编辑按钮', () => {
    const wrapper = mount(QuestionCard, {
      props: { question: mockQuestion, readonly: true }
    })
    
    const editBtn = wrapper.find('.edit-button')
    expect(editBtn.exists()).toBe(false)
  })

  it('非 readonly 模式下应显示编辑按钮', () => {
    const wrapper = mount(QuestionCard, {
      props: { question: mockQuestion, readonly: false }
    })
    
    const editBtn = wrapper.find('.edit-button')
    expect(editBtn.exists()).toBe(true)
  })
})
