import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
    { path: '/register/:slug', component: () => import('../views/PublicRegisterView.vue'), meta: { public: true } },
    { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
    { path: '/activities', component: () => import('../views/ActivityListView.vue') },
    { path: '/activities/new', component: () => import('../views/ActivityEditView.vue') },
    { path: '/activities/:id/edit', component: () => import('../views/ActivityEditView.vue') },
    { path: '/activities/:id/form', component: () => import('../views/FormBuilderView.vue') },
    { path: '/registrations', component: () => import('../views/RegistrationListView.vue') },
    { path: '/registrations/:id', component: () => import('../views/RegistrationDetailView.vue') },
    { path: '/accounts', component: () => import('../views/AccountManageView.vue') },
    { path: '/email-templates', component: () => import('../views/EmailTemplateView.vue') },
    { path: '/email-jobs', component: () => import('../views/EmailJobView.vue') },
    { path: '/settings', component: () => import('../views/SettingsView.vue') }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) {
    return '/login'
  }
  if (to.path === '/login' && auth.token) {
    return '/dashboard'
  }
  return true
})

export default router

