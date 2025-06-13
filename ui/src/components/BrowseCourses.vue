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
        @remove-course="removeCourse"
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

function toMinutes(timeStr: string): number {
  const [hour, minute] = timeStr.split(':').map(Number)
  return hour * 60 + minute
}

function isOverlapping(eventA: any, eventB: any): boolean {
  const dateA = new Date(eventA.start).getDate()
  const dateB = new Date(eventB.start).getDate()
  if (dateA !== dateB) return false

  const startA = toMinutes(eventA.course_start_time)
  const endA = toMinutes(eventA.course_end_time)
  const startB = toMinutes(eventB.course_start_time)
  const endB = toMinutes(eventB.course_end_time)

  return Math.max(startA, startB) < Math.min(endA, endB)
}

function removeCourse(course: any) {
  course.is_selected = false

  // Remove course from chosen list and events
  chosen_courses.value = chosen_courses.value.filter(
    (coursed: any) => coursed.course_id !== course.course_id,
  )
  events.value = events.value.filter((classs: any) => classs.course_id !== course.course_id)

  // Recheck overlap status for all remaining 'overlap' courses
  events.value.forEach((event: any, index: any, arr: any) => {
    if (event.class === 'overlap') {
      const stillConflicts = arr.some(
        (other: any) => other.course_id !== event.course_id && isOverlapping(event, other),
      )

      // Update the class based on whether there's still a conflict
      if (!stillConflicts) {
        arr[index].class = 'valid'
      }
    }
  })
}
</script>
