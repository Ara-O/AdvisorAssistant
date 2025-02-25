<template>
  <main>
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

      <button
        @click="findCourses"
        class="bg-udmercy-blue cursor-pointer font-semibold text-sm px-6 py-3 rounded-md mt-7 font-text text-white"
      >
        Find Courses
      </button>
      <p class="mt-5" v-if="courses_are_being_fetched">Fetching courses, please wait...</p>
    </section>

    <!-- OR ELSE -->

    <section v-else>
      <!-- <h3>Fetch all Courses</h3>
      <select name="term" id="term" v-model="selected_term">
        <option
          :value="{ code: course.code, name: course.description }"
          v-for="(course, idx) in retrieved_terms"
        >
          {{ course.description }}
        </option>
      </select>
      <br /> -->

      <br />
      <button @click="download_course">Download every course</button>
      <a
        href="https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/classSearch"
        target="_blank"
        >Get cookies</a
      >
      <div style="display: flex">
        <div>
          <div v-for="(courses, category) in ordered_courses">
            <details>
              <summary>{{ category }}</summary>
              <div
                v-for="course in courses"
                :style="{ 'background-color': course.is_selected ? 'skyblue' : 'pink' }"
                @click="() => addStuff(course)"
              >
                <p>{{ course.course_name }}</p>
                <p>{{ course.course_number }}</p>
                <p>Type: {{ course.meeting_type_description }}</p>
                <p>Section: {{ course.section }}</p>
                <p>Start time: {{ course.meeting_begin_time }}</p>
              </div>
            </details>
          </div>
        </div>
        <!-- TODO: change selected date to current date -->
        <vue-cal
          :events="events"
          selected-date="2025-05-05"
          :time-from="9 * 60"
          hide-title-bar
          :time-to="23 * 60"
          :disable-views="['years', 'year', 'month']"
          :on-event-click="onEventClick"
        >
        </vue-cal>
      </div>

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
              <li>
                Event starts at: {{ selectedEvent.start && selectedEvent.start.formatTime() }}
              </li>
              <li>Event ends at: {{ selectedEvent.end && selectedEvent.end.formatTime() }}</li>
            </ul>
          </v-card-text>
        </v-card>
      </v-dialog>
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

function onEventClick(event: any) {
  // console.log(event)
  // Prevent navigating to narrower view (default vue-cal behavior).
}

const ordered_courses = ref<any>({})
const chosen_courses = ref<any>([])
const jsessionid = ref('')
const awsalb = ref('')
const awsalbcors = ref('')

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

    // After fetching the course, make this
    courses_are_being_fetched.value = false
    courses_have_been_fetched.value = true
  } catch (err) {
    alert(err)
    console.log(err)
  }
}

async function download_course() {
  // console.log(selected_course.value)
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/fetch_courses`, {
      params: {
        // term_name: selected_course.value.name,
        // term_code: selected_course.value.code,
        awsalb: awsalb.value,
        awsalbcors: awsalbcors.value,
        jsessionid: jsessionid.value,
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

    // console.log(ordered_courses)
    // console.log(course_categories)

    // console.log(res.data)
  } catch (err) {
    console.log(err)
  }
}

function addStuff(course: any) {
  // console.log(course)
  if (!course.is_selected) {
    course.is_selected = true
    chosen_courses.value.push(course)
  } else {
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
  // console.log(chosen_courses)

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

  days.forEach((day) => {
    // TODO: Change this to Current day
    let starttime = '2025-05-' + day + ' ' + begintime
    let endtimes = '2025-05-' + day + ' ' + endtime

    events.value.push({
      start: starttime,
      end: endtimes,
      title: course.course_name,
      content: `<p>${course.building}</p>`,
      class: 'health',
      course_id: course.course_id,
    })
  })

  console.log(events)
  // {
  //   start: '2025-11-18 10:00',
  //   end: '2025-11-18 14:00',
  //   title: 'Golf with John',
  //   content: '<i class="icon material-icons">golf_course</i>',
  //   class: 'sport',
  // },
}

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
</style>
