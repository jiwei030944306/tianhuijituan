<script setup lang="ts">
/**
 * 根组件
 */
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import GlobalNavbar from '@/components/common/GlobalNavbar.vue';

const route = useRoute();

// 根据路由元信息决定是否显示导航栏
const shouldShowNavbar = computed(() => {
  return !route.meta.hideNavbar;
});
</script>

<template>
  <div id="app">
    <!-- 全局导航栏 -->
    <GlobalNavbar v-if="shouldShowNavbar" />
    
    <!-- 路由视图（添加padding-top避免被导航栏遮挡） -->
    <router-view />
  </div>
</template>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
}

#app {
  min-height: 100vh;
}
</style>
