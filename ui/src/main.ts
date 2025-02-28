import './assets/main.css'
import 'vue-cal/dist/vuecal.css'
// @ts-expect-error
import VueCal from 'vue-cal'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark-selector',
    },
  },
})
app.use(createPinia())
app.use(router)

app.mount('#app')
