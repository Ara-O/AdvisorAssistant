<template>
  <section class="px-8 py-5">
    <div class="flex gap-10 flex-row">
      <!-- Left section: Course list -->
      <all-courses-list
        :events="events"
        :chosen_courses="chosen_courses"
        :courses_data="courses_data"
        :course_categories="course_categories"
        @add-course="addCourse"
        @remove-course="removeCourse"
      ></all-courses-list>

      <!-- Right section: Course calendar -->
      <courses-calendar
        :chosen_courses="chosen_courses"
        :events="events"
        @remove_course="removeCourse"
      ></courses-calendar>
    </div>
  </section>
</template>

<script lang="ts" setup>
import AllCoursesList from './AllCoursesList.vue'
import CoursesCalendar from './CoursesCalendar.vue'
import { ref } from 'vue'

defineProps(['courses_data', 'course_categories'])

const events = ref<any>([])
const chosen_courses = ref<any>([])

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
</script>
