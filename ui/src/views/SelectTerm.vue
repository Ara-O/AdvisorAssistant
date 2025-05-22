<template>
  <section class="h-screen flex-col items-center flex justify-center">
    <router-link
      to="/"
      class="font-text underline font-medium text-gray-600 absolute top-6 cursor-pointer left-10"
      >Return To Home</router-link
    >
    <h1 class="font-title font-medium text-4xl">Choose A Term</h1>
    <select
      type="text"
      class="border font-text text-center rounded-sm mt-7 h-10 w-64 border-gray-400"
      v-model="selected_term"
    >
      <option :value="null" selected default disabled>Select a term</option>
      <option
        :value="{ code: term.code, description: term.description }"
        v-for="(term, idx) in retrieved_terms"
      >
        {{ term.description }}
      </option>
    </select>

    <!-- <span class="flex mt-3 gap-3">
      <input type="checkbox" id="use_cache" v-model="use_cache" />
      <label for="use_cache">Use Cache</label>
    </span> -->
    <button
      @click="browseCourses"
      class="bg-udmercy-blue cursor-pointer font-semibold text-sm px-6 py-3 rounded-md mt-7 font-text text-white"
    >
      Browse Courses
    </button>
  </section>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { TYPE, useToast } from 'vue-toastification'
import axios from 'axios'

type Term = {
  code: string
  description: string
}

const retrieved_terms = ref<Term[]>([])
const toast = useToast()
const selected_term = ref<null | Term>(null)
const courses_are_being_fetched = ref<boolean>(false)

async function browseCourses() {
  try {
    toast.clear()
    if (selected_term.value === null) {
      toast('Please select a term', {
        type: TYPE.ERROR,
      })
      return
    }

    toast('Fetching courses...Please wait', {
      type: TYPE.INFO,
    })

    // let res = await axios.get(`${import.meta.env.VITE_API_URL}/fetch_courses`, {
    //   params: {
    //     term_name: selected_term.value.description,
    //     term_code: selected_term.value.code,
    //     awsalb: awsalb.value,
    //     awsalbcors: awsalbcors.value,
    //     jsessionid: jsessionid.value,
    //     use_cache: use_cache.value,
    //   },
    // })

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
  } catch (err) {
    alert(err)
    console.log(err)
  }
}

// Fetch the terms
onMounted(async () => {
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/api/fetch_all_terms`)
    retrieved_terms.value = res.data
  } catch (err) {
    toast('An unexpected error occured when fetching the terms. Please try again later', {
      type: TYPE.ERROR,
    })
    console.log(err)
  }
})
</script>
