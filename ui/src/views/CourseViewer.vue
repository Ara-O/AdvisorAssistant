<template>
  <main class="">
    <!-- Select Term -->
    <select-term @term-has-been-selected="onTermHasBeenSelected"></select-term>

    <!-- Browse Courses -->
  </main>
</template>

<script lang="ts" setup>
import axios from 'axios'
import SelectTerm from '../components/SelectTerm.vue'
import { ref } from 'vue'
import { TYPE, useToast } from 'vue-toastification'
import { type Term } from '@/types/types'

const toast = useToast()
const selected_term = ref<Term | null>()
const refresh_course_data = ref<boolean>(false)

async function fetchCourses() {
  try {
    toast.clear()

    if (!selected_term.value) {
      toast('Please select a term', {
        type: TYPE.ERROR,
      })
      return
    }

    toast('Fetching courses... Please be patient.', {
      type: TYPE.INFO,
    })

    let res = await axios.get(`${import.meta.env.VITE_API_URL}/api/fetch_courses`, {
      params: {
        term_name: selected_term.value.description,
        term_code: selected_term.value.code,
        refresh_course_data: refresh_course_data.value,
      },
    })

    // const courses = res.data
    // const course_categories: any = {}
    // courses.forEach((course: any) => {
    //   if (!course_categories[course.subject]) {
    //     course_categories[course.subject] = course.course_description
    //   }
    //   if (!ordered_course_list.value[course.course_description]) {
    //     ordered_course_list.value[course.course_description] = [course]
    //   } else {
    //     ordered_course_list.value[course.course_description].push(course)
    //   }
    // })
    // course_types.value = course_categories
  } catch (err) {}
}
function onTermHasBeenSelected(term: Term, refresh_course_data_p: boolean) {
  selected_term.value = term
  refresh_course_data.value = refresh_course_data_p
  fetchCourses()
}
</script>
