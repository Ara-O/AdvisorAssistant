import { createRouter, createWebHistory } from 'vue-router'
import CourseViewer from '../views/CourseViewer.vue'
import LandingPage from '@/views/LandingPage.vue'

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
  ],
})

export default router
