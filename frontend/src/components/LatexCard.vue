<template>
  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
    <div class="bg-slate-50 px-4 py-2 border-b border-slate-100 font-bold text-slate-700 text-xs uppercase tracking-wider flex justify-between items-center">
      {{ title }}
      <span class="text-[10px] text-slate-400 bg-white border border-slate-200 px-1.5 rounded">{{ items.length }} 符号</span>
    </div>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-px bg-slate-100">
      <div 
        v-for="(latex, idx) in items" 
        :key="idx"
        @click="copyToClipboard(latex)"
        class="bg-white p-4 flex flex-col items-center justify-center gap-3 hover:bg-indigo-50 transition-colors min-h-[100px] group cursor-pointer relative"
      >
        <div class="text-xl text-slate-800 scale-110 group-hover:scale-125 transition-transform">
          <MathText :text="latex" />
        </div>
        <code class="text-[10px] text-slate-400 font-mono bg-slate-100 px-2 py-0.5 rounded group-hover:bg-white group-hover:text-indigo-600 border border-transparent group-hover:border-indigo-100 transition-colors select-all">
          {{ latex }}
        </code>
        
        <!-- Copy Feedback Tooltip -->
        <div 
          v-if="copied === latex" 
          class="absolute top-2 right-2 text-[10px] bg-green-500 text-white px-1.5 py-0.5 rounded animate-fade-in-up"
        >
          Copied!
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import MathText from '@/components/common/MathText.vue';

defineProps<{
  title: string;
  items: string[];
}>();

const copied = ref<string | null>(null);

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    copied.value = text;
    setTimeout(() => {
      copied.value = null;
    }, 1500);
  } catch (err) {
    console.error('Failed to copy:', err);
  }
};
</script>
