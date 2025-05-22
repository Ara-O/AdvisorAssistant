<template>
  <main
    class="flex lg:justify-center items-center justify-start gap-x-10 gap-y-20 content-center px-10 flex-wrap-reverse h-screen"
  >
    <section class="w-full max-w-[700px]">
      <h1 class="font-title text-5xl font-medium">UDM Advisor Assistant</h1>
      <div class="mt-7">
        <p class="text-lg">
          <span class="font-semibold">Course Viewer & Calendar </span>: Easily browse courses, track
          deadlines, and stay organized.
        </p>
        <button
          class="font-text cursor-pointer mt-3 w-40 bg-udmercy-blue text-white font-semibold px-5 py-3 text-sm rounded-sm"
          @click="goToCourseViewer"
        >
          Course Viewer
        </button>
      </div>
      <div class="mt-6">
        <p class="text-lg">
          <span class="font-semibold">Advisor Assistant </span>: Upload your degree evaluation and
          get a personalized schedule
        </p>
        <button
          class="font-text mt-3 w-40 cursor-pointer bg-udmercy-blue text-white font-semibold px-5 py-3 text-sm rounded-sm"
          @click="goToAdvisorAssistant"
        >
          Advisor Assistant
        </button>
      </div>
    </section>
    <section class="float-left">
      <img :src="DetroitMercyLogo" alt="Detroit Mercy Logo" class="w-36 md:w-50" />
    </section>
  </main>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'
import DetroitMercyLogo from '../assets/detroit-mercy-logo.png'

const router = useRouter()

function goToCourseViewer() {
  router.push({
    name: 'course-viewer',
  })
}

function goToAdvisorAssistant() {
  router.push({
    name: 'advisor-assistant',
  })
}
</script>
