<template>
  <main>
    <h3>Fetch all Courses</h3>
    <select name="" id="" v-model="selected_course">
      <option :value="course.code" v-for="(course, idx) in course_mappings">
        {{ course.description }}
      </option>
    </select>
    <button @click="download_course">Download every course</button>
  </main>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'

type Course = {
  code: string
  description: string
}

const course_mappings = ref<Course[]>([])
const selected_course = ref<Course>()

async function download_course() {
  console.log(selected_course.value)
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/fetch_courses`, {
      params: {
        term: selected_course.value,
      },
    })
  } catch (err) {}
}

onMounted(async () => {
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/course_proxy`)
    course_mappings.value = res.data

    selected_course.value = course_mappings.value[0]
  } catch (err) {
    console.log(err)
  }
})
</script>
