<script setup lang="ts">
/**
 * 通用使用说明组件
 * 参考 React 版本的设计，适配 Vue 3 + Element Plus
 */
import { ref, computed } from 'vue';
import {
  Upload,
  FolderOpened,
  Edit,
  Document,
  User,
  School,
  Grid,
  ArrowRight,
  InfoFilled,
  QuestionFilled,
  WarningFilled,
  CircleCheckFilled,
  Search,
  Monitor,
  VideoPlay,
  Delete,
  Lock,
  Lightning
} from '@element-plus/icons-vue';

// 页面类型 - 按业务流程顺序: landing → home → upload → check → refine
type PageType = 'landing' | 'home' | 'upload' | 'check' | 'refine';

// 步骤项接口
interface StepItem {
  num: string;
  title: string;
  desc: string;
  icon: string;
  color: string;
}

// 页面配置接口
interface PageConfig {
  title: string;
  subtitle: string;
  steps: StepItem[];
  tipsTitle: string;
  tips: string[];
  heroType: PageType;
}

// Props
interface Props {
  modelValue: boolean;
  pageType: PageType;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const closeGuide = () => {
  dialogVisible.value = false;
  // 记录用户已看过引导
  localStorage.setItem(`${props.pageType}_guide_shown`, 'true');
};

// 页面配置 - 按业务流程顺序排列: landing → home → upload → check → refine
const pageConfigs: Record<PageType, PageConfig> = {
  // 1. Landing - 登录/引导页
  landing: {
    title: "智研题库云快速上手",
    subtitle: "三步开启智能化教研之旅。系统将自动引导您完成身份验证与环境配置。",
    steps: [
      {
        num: "01",
        title: "身份鉴权",
        desc: "点击右上角登录按钮。使用测试账号解锁完整功能。",
        icon: "User",
        color: "text-slate-600 bg-slate-100 border-slate-200",
      },
      {
        num: "02",
        title: "场景定义",
        desc: "在屏幕中央选择所属的学段（初/高）与学科，初始化知识图谱。",
        icon: "School",
        color: "text-indigo-600 bg-indigo-50 border-indigo-100",
      },
      {
        num: "03",
        title: "进入工作台",
        desc: "点击下方大按钮进入协作大厅。也可浏览底部的文档与工具。",
        icon: "Grid",
        color: "text-purple-600 bg-purple-50 border-purple-100",
      },
    ],
    tipsTitle: "账号信息",
    tips: [
      "🔑 测试账号: jiwei / 123",
      "🔒 未登录状态下仅可浏览基础页面。",
      "🌐 推荐使用 Chrome 浏览器以获得最佳性能。",
    ],
    heroType: "landing",
  },

  // 2. Home - 工作台首页
  home: {
    title: "核心工作台指南",
    subtitle: "智研题库云的核心枢纽。这里整合了 P0-P5 六大中心入口，提供业务上下文管理与模块导航。",
    steps: [
      {
        num: "01",
        title: "确认业务上下文",
        desc: "检查顶部导航栏的学段/学科选择。这决定了后续所有操作的数据范围与知识图谱。",
        icon: "School",
        color: "text-indigo-600 bg-indigo-50 border-indigo-100",
      },
      {
        num: "02",
        title: "选择功能中心",
        desc: "点击下方的6大中心卡片进入对应模块。已上线的模块会高亮显示，规划中模块置灰。",
        icon: "Grid",
        color: "text-purple-600 bg-purple-50 border-purple-100",
      },
      {
        num: "03",
        title: "监控与反馈",
        desc: "P4/P5中心提供全局看板和日志反馈。可在这些模块监控题目流转效率与错误分布。",
        icon: "Monitor",
        color: "text-emerald-600 bg-emerald-50 border-emerald-100",
      },
    ],
    tipsTitle: "使用技巧与注意事项",
    tips: [
      "💡 卡片状态：绿色/蓝色卡片表示已上线可用；灰色表示规划中不可用。",
      "🔄 上下文切换：切换学段/学科后会自动刷新各中心的数据范围。",
      "🚀 快速导航：hover 到卡片上会出现箭头指引，点击即可进入对应模块。",
      "⚠️ 数据隔离：不同学段/学科的数据是隔离的，请确保选择了正确的业务上下文。",
    ],
    heroType: "home",
  },

  // 3. Upload - 上传管理 (P0)
  upload: {
    title: "资源导入向导",
    subtitle: "这是流水线的起点。负责将非结构化的本地文件(ZIP/JSON)转换为系统可读的结构化数据。",
    steps: [
      {
        num: "01",
        title: "选择文件",
        desc: "点击上传区域选择 ZIP 或 JSON 文件。推荐使用 ZIP 格式以包含图片。",
        icon: "Upload",
        color: "text-blue-600 bg-blue-50 border-blue-100",
      },
      {
        num: "02",
        title: "等待处理",
        desc: "观察实时终端窗口。系统会自动进行解压、解析和入库操作。",
        icon: "Monitor",
        color: "text-slate-600 bg-slate-100 border-slate-200",
      },
      {
        num: "03",
        title: "前往 P1",
        desc: "当看到「导入成功」绿色提示后,点击右侧出现的「去处理」按钮。",
        icon: "VideoPlay",
        color: "text-indigo-600 bg-indigo-50 border-indigo-100",
      },
    ],
    tipsTitle: "常见问题 (FAQ)",
    tips: [
      "❓ 为什么进度条卡在 99%？通常是在解压大文件，请耐心等待 10-20 秒。",
      "💡 技巧：单次建议上传不超过 100MB 的压缩包，以获得最快的处理速度。",
      "⚠️ 注意：文件名不要包含特殊字符，否则可能导致解压失败。",
    ],
    heroType: "upload",
  },

  // 4. Check - 试题自检与同步中心 (P1)
  check: {
    title: "试题自检与同步中心",
    subtitle: "P1 核心功能模块。对已上传的试题批次进行全方位检视、质量校验与同步处理，确保入库题目符合标准。",
    steps: [
      {
        num: "01",
        title: "选择批次",
        desc: "在左侧面板选择需要检视的试题批次。可按文件名、状态筛选，支持批量操作。",
        icon: "FolderOpened",
        color: "text-blue-600 bg-blue-50 border-blue-100",
      },
      {
        num: "02",
        title: "多维筛选",
        desc: "使用顶部筛选器按题型、难度、状态、AI优化状态等维度过滤题目，快速定位问题题目。",
        icon: "Search",
        color: "text-indigo-600 bg-indigo-50 border-indigo-100",
      },
      {
        num: "03",
        title: "详情检视",
        desc: "点击题目行展开详情面板，查看题干、选项、答案、解析。支持 LaTeX 公式渲染与图片预览。",
        icon: "Document",
        color: "text-emerald-600 bg-emerald-50 border-emerald-100",
      },
    ],
    tipsTitle: "使用技巧与注意事项",
    tips: [
      "💡 题号排序：题目默认按题号升序排列，无题号题目按类型优先级排序。",
      "🔍 关键词搜索：支持按题目ID、题干内容模糊搜索，快速定位特定题目。",
      "🎨 题型颜色：不同类型题目有不同颜色标识，便于快速识别题型分布。",
      "⚠️ 状态标记：注意查看题目状态列，'error' 状态表示该题目需要人工修正。",
      "🤖 AI筛选：使用AI优化状态筛选，可快速区分已AI处理和未处理题目。",
      "📊 统计卡片：顶部统计卡片实时显示当前筛选条件下的题目分布情况。",
    ],
    heroType: "check",
  },

  // 5. Refine - 标化中心 (P2) - 占位，后续补充
  refine: {
    title: "标化教研中心",
    subtitle: "P2 核心功能模块（开发中）。对已入库题目进行知识点打标、AI解析编写与人工审核。",
    steps: [
      {
        num: "01",
        title: "功能开发中",
        desc: "标化中心正在开发中，敬请期待。",
        icon: "Edit",
        color: "text-slate-400 bg-slate-50 border-slate-200",
      },
    ],
    tipsTitle: "敬请期待",
    tips: [
      "🚧 标化中心功能正在开发中，将在后续版本上线。",
    ],
    heroType: "refine",
  },
};

// Icon映射表
const iconMap: Record<string, any> = {
  Upload,
  FolderOpened,
  Edit,
  Document,
  User,
  School,
  Grid,
  ArrowRight,
  InfoFilled,
  QuestionFilled,
  WarningFilled,
  CircleCheckFilled,
  Search,
  Monitor,
  VideoPlay,
  Delete,
  Lock,
  Lightning
};

// 获取当前页面配置
const currentPage = computed(() => {
  const config = pageConfigs[props.pageType];
  if (!config) {
    console.warn(`未找到页面类型 "${props.pageType}" 的配置，使用默认配置`);
    return pageConfigs.home;
  }
  return config;
});
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    width="900px"
    :close-on-click-modal="false"
    class="help-guide-dialog"
    :show-close="true"
  >
    <!-- Hero Section -->
    <div class="flex items-start gap-12 bg-white p-8 pb-8 mb-0 md:flex-row flex-col">
      <div class="flex-1 md:text-center">
        <div class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-transparent text-indigo-400 text-[11px] font-extrabold uppercase tracking-widest mb-4">
          <el-icon><InfoFilled /></el-icon>
          <span>GUIDEBOOK</span>
        </div>
        <h2 class="text-3xl font-extrabold text-slate-900 mb-3 tracking-tight leading-tight">{{ currentPage.title }}</h2>
        <p class="text-sm text-slate-500 leading-relaxed m-0 max-w-lg">{{ currentPage.subtitle }}</p>
      </div>
      <div class="w-80 shrink-0">
        <!-- Upload Hero -->
        <div v-if="currentPage.heroType === 'upload'" class="w-full h-32 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 flex flex-col items-center justify-center relative overflow-hidden">
          <div class="flex items-center gap-4 z-10">
            <div class="w-16 h-16 bg-white rounded-2xl shadow-sm border border-blue-200 flex items-center justify-center">
              <div class="flow-icon text-3xl text-indigo-600"><el-icon><Document /></el-icon></div>
            </div>
            <div class="flex gap-1">
              <div class="w-2 h-2 rounded-full bg-blue-300 animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style="animation-delay: 300ms"></div>
            </div>
            <div class="w-16 h-16 bg-white rounded-2xl shadow-sm border border-indigo-200 flex items-center justify-center">
              <div class="flow-icon text-3xl text-indigo-600"><el-icon><Document /></el-icon></div>
            </div>
          </div>
          <div class="absolute bottom-2 text-[10px] text-blue-400 font-mono tracking-widest uppercase">ETL Pipeline Active</div>
        </div>

        <!-- Landing Hero -->
        <div v-else-if="currentPage.heroType === 'landing'" class="w-full h-32 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl border border-indigo-500 flex flex-col items-center justify-center relative overflow-hidden shadow-inner">
          <el-icon class="text-3xl text-white animate-pulse mb-2"><Lightning /></el-icon>
          <div class="text-[10px] text-white/80 font-extrabold uppercase tracking-widest">System Ready</div>
        </div>

        <!-- Default Hero (适用于 home, check, refine) -->
        <div v-else class="w-full h-32 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-center gap-3 p-4">
          <div class="flex flex-col items-center gap-1 opacity-50 text-[10px] font-extrabold text-slate-400">
            <el-icon class="text-2xl"><Upload /></el-icon>
            <span>P0 上传</span>
          </div>
          <el-icon class="text-slate-300 text-base"><ArrowRight /></el-icon>
          <div class="flex flex-col items-center gap-1 text-[10px] font-extrabold text-blue-600">
            <el-icon class="text-2xl"><FolderOpened /></el-icon>
            <span>P1 同步</span>
          </div>
          <el-icon class="text-slate-300 text-base"><ArrowRight /></el-icon>
          <div class="flex flex-col items-center gap-1 opacity-50 text-[10px] font-extrabold text-slate-400">
            <el-icon class="text-2xl"><Edit /></el-icon>
            <span>P2 标化</span>
          </div>
          <el-icon class="text-slate-300 text-base"><ArrowRight /></el-icon>
          <div class="flex flex-col items-center gap-1 opacity-50 text-[10px] font-extrabold text-slate-400">
            <el-icon class="text-2xl"><Document /></el-icon>
            <span>P3 归档</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Steps Section -->
    <div class="m-0 mx-8 mb-8">
      <h3 class="flex items-center gap-2 text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-6">
        <el-icon><InfoFilled /></el-icon>
        核心流程 (Core Workflow)
      </h3>
      <div class="grid grid-cols-3 gap-6">
        <div
          v-for="(step, index) in currentPage.steps"
          :key="index"
          class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-lg hover:border-indigo-200 transition-all duration-200 group relative overflow-hidden"
        >
          <!-- 背景装饰数字 -->
          <span class="text-6xl font-extrabold text-slate-50 transition-colors duration-200 select-none leading-none absolute right-4 top-4 z-0 group-hover:text-indigo-50">{{ step.num }}</span>

          <div class="flex justify-between items-start mb-4 relative z-10">
            <div :class="['w-12 h-12 rounded-xl flex items-center justify-center border shadow-sm text-2xl', step.color]">
              <el-icon><component :is="iconMap[step.icon]" /></el-icon>
            </div>
          </div>
          <h4 class="text-lg font-extrabold text-slate-800 mb-2 transition-colors duration-200 relative z-10 group-hover:text-indigo-700">{{ step.title }}</h4>
          <p class="text-sm text-slate-500 leading-relaxed m-0 relative z-10">{{ step.desc }}</p>
        </div>
      </div>
    </div>

    <!-- Tips Section -->
    <div class="m-0 mx-8 mb-8 bg-white p-6 rounded-xl border border-slate-200">
      <h3 class="flex items-center gap-2 text-sm font-extrabold text-slate-800 mb-4">
        <el-icon><QuestionFilled /></el-icon>
        {{ currentPage.tipsTitle }}
      </h3>
      <div class="flex flex-col gap-3">
        <div v-for="(tip, index) in currentPage.tips" :key="index" class="flex gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm text-slate-500 leading-relaxed">
          <span class="shrink-0 select-none">{{ tip.substring(0, 2) }}</span>
          <span>{{ tip.substring(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <template #footer>
      <div class="flex justify-end p-6 bg-white border-t border-slate-100">
        <el-button type="primary" size="large" @click="closeGuide" class="!bg-gray-800 !border-gray-800 !py-3 !px-6 !font-extrabold !rounded-lg hover:!bg-gray-900 hover:!border-gray-900 hover:!scale-[1.02] active:scale-95 transition-all">
          明白，开始操作
          <el-icon class="ml-1"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.help-guide-dialog {
  --el-dialog-bg-color: #ffffff;
}

/* 移除 Dialog body 的默认 padding */
.help-guide-dialog :deep(.el-dialog__body) {
  padding: 0 !important;
}

/* 移除 Dialog header */
.help-guide-dialog :deep(.el-dialog__header) {
  display: none;
}
</style>
