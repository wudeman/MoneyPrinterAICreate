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
      path: '/script-edit',
      name: 'scriptEdit',
      component: () => import('../views/ScriptEditView.vue')
    },
    {
    path: '/character-scene',
    name: 'characterScene',
    component: () => import('../views/CharacterSceneDesignView.vue')
  },
  {
    path: '/storyboard',
    name: 'storyboard',
    component: () => import('../views/StoryboardView.vue')
  },
  {
    path: '/media-generation',
    name: 'mediaGeneration',
    component: () => import('../views/MediaGenerationView.vue')
  },
  {
    path: '/video-synthesis',
    name: 'videoSynthesis',
    component: () => import('../views/VideoSynthesisView.vue')
  },
  {
    path: '/model-management',
    name: 'modelManagement',
    component: () => import('../views/ModelManagementView.vue')
  },
    {
    path: '/template-management',
    name: 'templateManagement',
    component: () => import('../views/TemplateManagement.vue')
  },
    {
      path: '/dict-management',
      name: 'dictManagement',
      component: () => import('../views/DictManagement.vue')
    },
    {
      path: '/integration-test',
      name: 'integrationTest',
      component: () => import('../views/IntegrationTestView.vue')
    }
  ]
})

export default router