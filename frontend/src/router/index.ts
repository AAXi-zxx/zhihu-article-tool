import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '主页',
      component: HomePage,
    },
    {
      path: '/create',
      name: '创作文章',
      component: () => import('@/pages/article/ArticleCreatePage.vue'),
    },
    {
      path: '/article/list',
      name: '文章列表',
      component: () => import('@/pages/article/ArticleListPage.vue'),
    },
    {
      path: '/article/:taskId',
      name: '文章详情',
      component: () => import('@/pages/article/ArticleDetailPage.vue'),
    },
    {
      path: '/admin/statistics',
      name: '数据分析',
      component: () => import('@/pages/admin/StatisticsPage.vue'),
    },
  ],
})

export default router
