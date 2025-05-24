<template>
  <div>
    <h1 class="font-title text-2xl mb-4 font-medium">Course Calendar</h1>

    <vue-cal
      :events="props.events"
      selected-date="2025-05-05"
      :time-from="8 * 60"
      hide-view-selector
      :time-cell-height="60"
      hide-title-bar
      :time-to="23 * 60"
      :disable-views="['years', 'year', 'month']"
      :on-event-click="onEventClick"
    >
    </vue-cal>
  </div>
</template>

<script lang="ts" setup>
// @ts-expect-error
import VueCal from 'vue-cal'

const props = defineProps(['chosen_courses', 'events'])
const emits = defineEmits(['remove-course'])

function onEventClick(event: any) {
  const remove_course = confirm('Do you want to remove this course?')

  if (remove_course) {
    const found_course = props.chosen_courses.find(
      (course: any) => String(course.course_id) === String(event.course_id),
    )

    found_course.is_selected = false
    if (found_course) {
      emits('remove-course', { course_id: found_course.course_id })
    }
  }
}
</script>

<style>
.vuecal__event.valid {
  background-color: rgba(2, 35, 99, 0.9);
  border: 1px solid rgba(2, 35, 99, 0.9);
  color: #fff;
  padding: 0px 0px;
}

.vuecal__event.overlap {
  background-color: rgba(191, 3, 3, 0.9);
  border: 1px solid rgba(191, 3, 3, 0.9);
  color: #fff;
  padding: 0px 0px;
}

.vuecal__event.sport {
  background-color: rgba(130, 11, 11, 0.9);
  border: 1px solid rgb(235, 82, 82);
  color: #fff;
  padding: 10px 0px;
}

.vuecal__event-title {
  font-size: 12px;
  padding: 10px 4px;
  font-weight: 500;
}

.vuecal__event-time {
  font-size: 12px;
  margin-top: -8px;
}

.vuecal__event-content {
  font-size: 12px;
}

.vuecal {
  font-family: 'Raleway' !important;
}

.selected-course {
  background-color: #093575;
  border: solid 1px #093575;
  color: white;
}

.vuecal__flex.weekday-label span:last-of-type {
  display: none;
}

.vuecal__no-event {
  display: none;
}
</style>
