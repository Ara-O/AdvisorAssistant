import './assets/main.css'
import 'vue-cal/dist/vuecal.css'
// @ts-expect-error
import VueCal from 'vue-cal'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
