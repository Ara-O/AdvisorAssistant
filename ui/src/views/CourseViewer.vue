<template>
  <main class="">
    <!-- Select Term -->
    <select-term
      @term-has-been-selected="onTermHasBeenSelected"
      v-if="!show_course_viewer"
    ></select-term>

    <!-- Browse Courses -->
    <browse-courses
      v-if="show_course_viewer"
      :courses_data="ordered_course_data"
      :course_categories="course_categories"
    ></browse-courses>
  </main>
</template>

<script lang="ts" setup>
import axios from 'axios'
import SelectTerm from '../components/SelectTerm.vue'
import BrowseCourses from '@/components/BrowseCourses.vue'
import { ref } from 'vue'
import { type Term } from '@/types/types'
import { TYPE, useToast } from 'vue-toastification'

const toast = useToast()
const selected_term = ref<Term | null>()
const refresh_course_data = ref<boolean>(false)
const ordered_course_data = ref<any[]>([])
const course_categories = ref<any>({})
const show_course_viewer = ref<boolean>(false)

// When the user has selected a term, fetch courses corresponding to that term
function onTermHasBeenSelected(term: Term, refresh_course_data_p: boolean) {
  selected_term.value = term
  refresh_course_data.value = refresh_course_data_p
  fetchCourses()
}

async function fetchCourses() {
  try {
    toast.clear()

    if (!selected_term.value) {
      toast('Please select a term', {
        type: TYPE.ERROR,
      })
      return
    }

    toast('Fetching courses... Please be patient, this may take a while.', {
      type: TYPE.INFO,
      timeout: false,
    })

    // Fetch all the courses
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/api/fetch_courses`, {
      params: {
        term_name: selected_term.value.description,
        term_code: selected_term.value.code,
        refresh_course_data: refresh_course_data.value,
      },
    })

    const data = res.data

    data.forEach((course: any) => {
      // Define course categories/subjects
      console.log(course.subject, course)
      if (!course_categories.value[course.subject]) {
        course_categories.value[course.subject] = course.course_description
      }

      if (!ordered_course_data.value[course.course_description]) {
        ordered_course_data.value[course.course_description] = [course]
      } else {
        ordered_course_data.value[course.course_description].push(course)
      }
    })

    show_course_viewer.value = true
    toast.clear()
  } catch (err) {
    toast.clear()
    toast('An unexpected error occured when fetching courses. Please try again later', {
      type: TYPE.ERROR,
    })

    console.log(err)
  }
}
</script>
