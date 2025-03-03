import './assets/main.css'
import 'vue-cal/dist/vuecal.css'
// @ts-expect-error
import VueCal from 'vue-cal'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import Toast, { POSITION } from 'vue-toastification'
// Import the CSS or use your own!
import 'vue-toastification/dist/index.css'
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

app.use(Toast, {
  transition: 'Vue-Toastification__fade',
  position: POSITION.TOP_RIGHT,
  icon: false,
})

app.use(createPinia())
app.use(router)

app.mount('#app')
