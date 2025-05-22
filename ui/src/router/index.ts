import { createRouter, createWebHistory } from 'vue-router'
import CourseViewer from '../views/CourseViewer.vue'
import LandingPage from '@/views/LandingPage.vue'
import AdvisorAssistant from '@/views/AdvisorAssistant.vue'
import SelectTerm from '@/views/SelectTerm.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingPage,
    },
    {
      path: '/courses',
      name: 'course-viewer',
      component: CourseViewer,
    },
    {
      path: '/advisor-assistant',
      name: 'advisor-assistant',
      component: AdvisorAssistant,
    },
    {
      path: '/select-term',
      name: 'select-term',
      component: SelectTerm,
    },
  ],
})

export default router
