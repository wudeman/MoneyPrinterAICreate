import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/model-management',
      name: 'modelManagement',
      component: () => import('../views/ModelManagementView.vue')
    },
    {
      path: '/template-management',
      name: 'template-management',
      component: () => import('../views/TemplateManagement.vue')
    }
  ]
})

export default router