<template>
  <main class="">
    <!-- SELECT COURSE POPUP -->
    <section
      v-if="!courses_have_been_fetched"
      class="h-screen flex-col items-center flex justify-center"
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

      <!-- Cookies section -->

      <label for="AWSALB" class="mt-5 mb-2">AWSALB Cookie</label>
      <input
        type="text"
        id="AWSALB"
        placeholder="AWSALB"
        class="border font-text text-center rounded-sm h-10 w-64 border-gray-400"
        v-model="awsalb"
      />

      <label for="AWSALBCORS" class="mt-5 mb-2">AWSALBCORS Cookie</label>
      <input
        type="text"
        placeholder="AWSALBCORS"
        class="border font-text text-center rounded-sm h-10 w-64 border-gray-400"
        id="AWSALBCORS"
        v-model="awsalbcors"
      />

      <label for="JSESSIONID" class="mt-5 mb-2">JSESSIONID Cookie</label>
      <input
        type="text"
        placeholder="JSESSIONID"
        class="border font-text text-center rounded-sm h-10 w-64 border-gray-400"
        id="JSESSIONID"
        v-model="jsessionid"
      />
      <span class="flex mt-3 gap-3">
        <input type="checkbox" id="use_cache" v-model="use_cache" />
        <label for="use_cache">Use Cache</label>
      </span>
      <button
        @click="findCourses"
        class="bg-udmercy-blue cursor-pointer font-semibold text-sm px-6 py-3 rounded-md mt-7 font-text text-white"
      >
        Find Courses
      </button>
      <p class="mt-5" v-if="courses_are_being_fetched">Fetching courses, please wait...</p>
    </section>

    <!-- COURSES TREE 
 
    -->
    <section class="px-8 py-5" v-else>
      <div class="flex gap-10 flex-row">
        <div class="w-[400px]">
          <h2 class="text-xl font-text font-bold mb-1">All Courses</h2>
          <div class="max-h-[600px] box-border overflow-auto">
            <div v-for="(courses, category) in ordered_courses" class="my-2">
              <details>
                <summary class="font-text">{{ category }}</summary>
                <div
                  v-for="course in courses"
                  @click="() => addCourse(course)"
                  :style="{ 'border-color': course.is_selected ? 'darkblue' : '' }"
                  class="border box-border px-3 pb-5 pt-4 my-2 rounded-md border-gray-300"
                >
                  <p class="font-medium overflow-ellipsis w-80">{{ course.course_name }}</p>
                  <p class="text-[15px]">
                    Course Number: {{ course.course_number }} | Section {{ course.section }}
                  </p>
                  <p v-if="course.meeting_begin_time" class="text-[15px]">
                    Time:
                    {{
                      course.meeting_begin_time.slice(0, 2) +
                      ':' +
                      course.meeting_begin_time.slice(2)
                    }}
                    -
                    {{
                      course.meeting_end_time.slice(0, 2) + ':' + course.meeting_end_time.slice(2)
                    }}. Days: {{ formatCourseDays(course) }}
                  </p>
                  <p v-else>This course does not have a set meeting time</p>
                </div>
              </details>
            </div>
          </div>
          <h2 class="text-xl font-text font-bold mt-5">Selected Courses</h2>
          <p v-if="chosen_courses.length == 0" class="mt-3">No courses have been selected yet</p>
          <div v-else>
            <div v-for="course in chosen_courses">
              <p class="mt-2">{{ course.course_name }}</p>
            </div>
          </div>
        </div>
        <!-- TODO: change selected date to current date -->
        <vue-cal
          :events="events"
          selected-date="2025-05-05"
          :time-from="9 * 60"
          hide-view-selector
          hide-title-bar
          :time-to="23 * 60"
          :disable-views="['years', 'year', 'month']"
          :on-event-click="onEventClick"
        >
        </vue-cal>
      </div>

      <!-- Using Vuetify (but we prefer Wave UI 🤘) -->
      <!-- <v-dialog v-model="showDialog">
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
              <li>
                Event starts at: {{ selectedEvent.start && selectedEvent.start.formatTime() }}
              </li>
              <li>Event ends at: {{ selectedEvent.end && selectedEvent.end.formatTime() }}</li>
            </ul>
          </v-card-text>
        </v-card>
      </v-dialog> -->
    </section>
  </main>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
// @ts-expect-error
import VueCal from 'vue-cal'

type Term = {
  code: string
  description: string
}

const selected_term = ref<Term | null>(null)
const retrieved_terms = ref<Term[]>([])
const courses_have_been_fetched = ref<boolean>(false)
const courses_are_being_fetched = ref<boolean>(false)
const showDialog = false
const selectedEvent = {} as any
const events = ref<any>([])
const ordered_courses = ref<any>({})
const chosen_courses = ref<any>([])
const jsessionid = ref('')
const awsalb = ref('')
const awsalbcors = ref('')
const use_cache = ref<boolean>(true)

function onEventClick(event: any) {
  // console.log(event)
  // Prevent navigating to narrower view (default vue-cal behavior).
}

function formatCourseDays(course: any) {
  const days = []
  if (course.monday) {
    days.push('M')
  }
  if (course.tuesday) {
    days.push('T')
  }
  if (course.wednesday) {
    days.push('W')
  }
  if (course.thursday) {
    days.push('Th')
  }
  if (course.friday) {
    days.push('F')
  }
  if (course.saturday) {
    days.push('Sa')
  }
  if (course.sunday) {
    days.push('Sn')
  }

  return days.join(' | ')
}

async function findCourses() {
  try {
    if (selected_term.value === null) {
      alert('Please enter a selected term')
      return
    }

    courses_are_being_fetched.value = true

    let res = await axios.get(`${import.meta.env.VITE_API_URL}/fetch_courses`, {
      params: {
        term_name: selected_term.value.description,
        term_code: selected_term.value.code,
        awsalb: awsalb.value,
        awsalbcors: awsalbcors.value,
        jsessionid: jsessionid.value,
        use_cache: use_cache.value,
      },
    })

    const courses = res.data
    const course_categories = new Set()

    courses.forEach((course: any) => {
      course_categories.add(course.course_description)
      if (!ordered_courses.value[course.course_description]) {
        ordered_courses.value[course.course_description] = [course]
      } else {
        ordered_courses.value[course.course_description].push(course)
      }
    })

    // After fetching the course
    courses_are_being_fetched.value = false
    courses_have_been_fetched.value = true
  } catch (err) {
    alert(err)
    console.log(err)
  }
}

function addCourse(course: any) {
  if (course.is_selected) {
    // Deselect the course and remove it from the chosen courses list if it
    course.is_selected = false
    // @ts-ignore
    chosen_courses.value = chosen_courses.value.filter(
      (coursed: any) => coursed.course_id !== course.course_id,
    )

    // console.log(events.value)
    // console.log(course.course_id)
    events.value = events.value.filter((classs: any) => classs.course_id !== course.course_id)
    return
  }

  course.is_selected = true
  chosen_courses.value.push(course)

  let enddate = course.start_date.split('/')
  let formattedEndDate = enddate[2] + '-' + enddate[1] + '-' + enddate[0]
  let startdate = course.end_date.split('/')
  let formattedStartDate = startdate[2] + '-' + startdate[1] + '-' + startdate[0]

  let beginTimeC = course.meeting_begin_time
  let begintime = beginTimeC.slice(0, 2) + ':' + beginTimeC.slice(2)

  let endTimeC = course.meeting_end_time
  let endtime = endTimeC.slice(0, 2) + ':' + endTimeC.slice(2)

  let days = []

  if (course.monday) {
    days.push('05')
  }
  if (course.tuesday) {
    days.push('06')
  }
  if (course.wednesday) {
    days.push('07')
  }
  if (course.thursday) {
    days.push('08')
  }
  if (course.friday) {
    days.push('09')
  }
  if (course.saturday) {
    days.push('10')
  }
  if (course.sunday) {
    days.push('11')
  }

  days.forEach((day) => {
    // TODO: Change this to Current day
    let starttime = '2025-05-' + day + ' ' + begintime
    let endtimes = '2025-05-' + day + ' ' + endtime

    events.value.push({
      start: starttime,
      end: endtimes,
      title: course.course_name,
      // content: `<p>${course.building}</p>`,
      class: 'health',
      course_id: course.course_id,
    })
  })
}

// Fetch the terms
onMounted(async () => {
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/course_proxy`)
    retrieved_terms.value = res.data
  } catch (err) {
    alert(err)
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

.vuecal__event-title {
  font-size: 12px;
}

.vuecal__event-time {
  font-size: 12px;
}

.vuecal__event-content {
  font-size: 12px;
}

.vuecal {
  font-family: 'Raleway' !important;
}
</style>
