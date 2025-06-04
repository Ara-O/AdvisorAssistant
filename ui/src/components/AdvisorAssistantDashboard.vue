<template>
  <section class="p-5 flex gap-8">
    <missing-requirements-list
      :events="events"
      :selected_term="props.selected_term"
      @add-course="addCourse"
      @remove-course="removeCourse"
      :chosen_courses="chosen_courses"
      @update-requirements-list="updateRequirementsList"
    ></missing-requirements-list>

    <courses-calendar
      :chosen_courses="chosen_courses"
      :events="events"
      @remove-course="removeCourse"
    ></courses-calendar>
  </section>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import MissingRequirementsList from './MissingRequirementsList.vue'
import { useClipboard } from '@vueuse/core'
import CoursesCalendar from './CoursesCalendar.vue'
import { type Term } from '@/types/types'

const props = defineProps(['selected_term'])

const events = ref<any>([])
const chosen_courses = ref([])

function addCourse(course: any) {
  events.value.push(course)
}

function removeCourse(course: any) {
  // Deselect the course and remove it from the chosen courses list if it
  course.is_selected = false
  // @ts-ignore
  chosen_courses.value = chosen_courses.value.filter(
    (coursed: any) => coursed.course_id !== course.course_id,
  )
  events.value = events.value.filter((classs: any) => classs.course_id !== course.course_id)
}

function updateRequirementsList() {}
</script>

<style>
:root {
  --udmercy-red: #a5093e;
  --udmercy-blue: #002d72;
}

.Vue-Toastification__toast {
  font-family: 'Poppins';
}

.Vue-Toastification__toast--info {
  border-radius: 0px;
  font-size: 4px;
  background-color: white;
  color: black;
  border-left: solid 7px black;
  box-shadow:
    0 1px 10px 0 rgba(111, 111, 111, 0.1),
    0 2px 15px 0 rgba(161, 161, 161, 0.05);
}

.Vue-Toastification__toast--error {
  border-radius: 0px;
  font-size: 4px;
  background-color: white;
  color: var(--udmercy-red);
  border-left: solid 7px var(--udmercy-red);
  box-shadow:
    0 1px 10px 0 rgba(111, 111, 111, 0.1),
    0 2px 15px 0 rgba(161, 161, 161, 0.05);
}

.Vue-Toastification__toast--warning {
  border-radius: 0px;
  font-size: 4px;
  background-color: white;
  color: #c78204;
  border-left: solid 7px #c78204;
  box-shadow:
    0 1px 10px 0 rgba(111, 111, 111, 0.1),
    0 2px 15px 0 rgba(161, 161, 161, 0.05);
}

.Vue-Toastification__toast--success {
  border-radius: 0px;
  font-size: 4px;
  background-color: white;
  color: var(--udmercy-blue);
  border-left: solid 7px var(--udmercy-blue);
  box-shadow:
    0 1px 10px 0 rgba(111, 111, 111, 0.1),
    0 2px 15px 0 rgba(161, 161, 161, 0.05);
}

.Vue-Toastification__toast--info .Vue-Toastification__close-button {
  color: black;
}

.Vue-Toastification__toast--info .Vue-Toastification__progress-bar {
  background-color: black;
}

.Vue-Toastification__toast--error .Vue-Toastification__close-button {
  color: var(--udmercy-red);
}

.Vue-Toastification__toast--success .Vue-Toastification__close-button {
  color: var(--udmercy-blue);
}
.Vue-Toastification__toast--warning .Vue-Toastification__close-button {
  color: #c78204;
}

.Vue-Toastification__toast--error .Vue-Toastification__progress-bar {
  background-color: var(--udmercy-red);
}
.Vue-Toastification__toast--success .Vue-Toastification__progress-bar {
  background-color: var(--udmercy-blue);
}
.Vue-Toastification__toast--warning .Vue-Toastification__progress-bar {
  background-color: #c78204;
}
.Vue-Toastification__toast-body {
  font-size: 13.5px;
}
</style>
