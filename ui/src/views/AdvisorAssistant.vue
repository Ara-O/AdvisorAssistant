<template>
  <main>
    <!-- Select term -->
    <select-term @term-has-been-selected="onTermHasBeenSelected" v-if="progress === 0"
      >Pick the semester you need advising for.</select-term
    >

    <upload-degree-evaluation-file
      v-if="progress === 1"
      @on-file-has-been-parsed="fileHasBeenParsed"
    ></upload-degree-evaluation-file>

    <verify-course-history
      :requirements="requirements"
      @start-advisor-assistant="startAdvisorAssistant"
      v-if="progress === 2"
    ></verify-course-history>

    <advisor-assistant-dashboard
      :selected_term="selected_term"
      :processed_requirements="processed_requirements"
      v-if="progress === 3"
    >
    </advisor-assistant-dashboard>
  </main>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import type { Term } from '@/types/types'
import SelectTerm from '@/components/SelectTerm.vue'
import UploadDegreeEvaluationFile from '@/components/UploadDegreeEvaluationFile.vue'
import AdvisorAssistantDashboard from '@/components/AdvisorAssistantDashboard.vue'
import VerifyCourseHistory from '@/components/VerifyCourseHistory.vue'
import axios from 'axios'

const selected_term = ref<Term>()
const progress = ref<number>(0)
const requirements = ref()
const refresh_course_data = ref<boolean>(false)
const processed_requirements = ref()

function onTermHasBeenSelected(term: Term, refresh_data: boolean) {
  selected_term.value = term
  refresh_course_data.value = refresh_data
  progress.value++
}

function fileHasBeenParsed(requirements_p: any) {
  requirements.value = requirements_p
  progress.value++
}

async function startAdvisorAssistant() {
  try {
    let res = await axios.post(`${import.meta.env.VITE_API_URL}/api/start-advisor-assistant`, {
      requirements_not_satisfied: requirements.value.requirements_not_satisfied,
      requirements_satisfied: requirements.value.requirements_satisfied,
      term_name: selected_term.value?.description,
    })

    console.log(res.data)

    processed_requirements.value = res.data
    progress.value++
  } catch (err) {}
}
</script>
