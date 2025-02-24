<template>
  <main>
    <h3>Fetch all Courses</h3>
    <select name="" id="" v-model="selected_course">
      <option :value="course.code" v-for="(course, idx) in course_mappings">
        {{ course.description }}
      </option>
    </select>
    <button @click="download_course">Download every course</button>
    <a
      href="https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/classSearch"
      target="_blank"
      >Get cookies</a
    >
    <vue-cal
      :events="events"
      selected-date="2025-11-19"
      :time-from="9 * 60"
      hide-title-bar
      :time-to="23 * 60"
      :disable-views="['years', 'year', 'month']"
      :on-event-click="onEventClick"
    >
    </vue-cal>

    <!-- Using Vuetify (but we prefer Wave UI 🤘) -->
    <v-dialog v-model="showDialog">
      <v-card>
        <v-card-title>
          <v-icon>{{ selectedEvent.icon }}</v-icon>
          <span>{{ selectedEvent.title }}</span>
          <v-spacer />
          <strong>{{ selectedEvent.start && selectedEvent.start.format('DD/MM/YYYY') }}</strong>
        </v-card-title>
        <v-card-text>
          <p v-html="selectedEvent.contentFull" />
          <strong>Event details:</strong>
          <ul>
            <li>Event starts at: {{ selectedEvent.start && selectedEvent.start.formatTime() }}</li>
            <li>Event ends at: {{ selectedEvent.end && selectedEvent.end.formatTime() }}</li>
          </ul>
        </v-card-text>
      </v-card>
    </v-dialog>
  </main>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
// @ts-expect-error
import VueCal from 'vue-cal'

type Course = {
  code: string
  description: string
}

const showDialog = false
const selectedEvent = {} as any

const events = [
  {
    start: '2025-11-19 10:30',
    end: '2026-11-19 11:45',
    // You can also define event dates with Javascript Date objects:
    // start: new Date(2025, 11 - 1, 16, 10, 30),
    // end: new Date(2025, 11 - 1, 16, 11, 30),
    title: 'Doctor appointment',
    content: '<i class="icon material-icons">local_hospital</i>',
    class: 'health',
  },
  {
    start: '2025-11-18 10:00',
    end: '2025-11-18 14:00',
    title: 'Golf with John',
    content: '<i class="icon material-icons">golf_course</i>',
    class: 'sport',
  },
]

function onEventClick(event: any) {
  console.log(event)
  // Prevent navigating to narrower view (default vue-cal behavior).
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

    console.log(res.data)
  } catch (err) {
    console.log(err)
  }
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

<style>
.vuecal__event.health {
  background-color: rgba(253, 156, 66, 0.9);
  border: 1px solid rgb(233, 136, 46);
  color: #fff;
  padding: 0px 0px;
}
.vuecal__event.sport {
  background-color: rgba(255, 102, 102, 0.9);
  border: 1px solid rgb(235, 82, 82);
  color: #fff;
  padding: 10px 0px;
}
</style>
