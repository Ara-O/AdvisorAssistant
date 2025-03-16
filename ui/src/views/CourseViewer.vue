<template>
  <main class="">
    <!-- SELECT COURSE POPUP -->
    <section
      v-if="!courses_have_been_fetched"
      class="h-screen flex-col items-center flex justify-center"
    >
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

    <!-- COURSES TREE -->
    <section class="px-8 py-5" v-else>
      <div class="flex gap-10 flex-row">
        <div class="max-w-[400px] w-full min-w-[300px]">
          <h2 class="text-xl font-text font-bold mb-1">All Courses</h2>
          <div class="flex gap-4">
            <div class="mt-3 mb-3">
              <label for="name_search" class="block font-semibold">Search by Course Title</label>
              <input
                type="text"
                id="name_search"
                v-model="search_by_name_field"
                class="border border-solid mt-2 px-3 w-full font-text text-sm py-2 border-gray-300 rounded-sm"
                placeholder="Search By Course Title"
              />
            </div>
            <div class="mt-3 mb-3">
              <label for="name_search" class="block font-semibold">Search by Type</label>
              <select
                type="text"
                id="name_search"
                v-model="search_by_course_type"
                class="border border-solid mt-2 px-3 w-36 font-text text-sm py-2 border-gray-300 rounded-sm"
                placeholder="Search By Name"
              >
                <option :value="null">All Types</option>
                <option :value="acronym" v-for="(full_title, acronym) in course_types">
                  {{ acronym }}: {{ full_title }}
                </option>
              </select>
            </div>
          </div>
          <div class="mt-3 mb-3 gap-3 flex">
            <span>
              <label for="name_search" class="block font-semibold">Attribute</label>
              <input
                type="text"
                id="name_search"
                v-model="search_by_attribute_field"
                class="border border-solid mt-2 px-3 w-full font-text text-sm py-2 border-gray-300 rounded-sm"
                placeholder="Search By Attribute"
              />
            </span>
            <span>
              <label for="course_no_search" class="block font-semibold">Course Number</label>
              <input
                type="text"
                id="course_no_search"
                v-model="search_by_course_no_field"
                class="border border-solid mt-2 px-3 w-36 font-text text-sm py-2 border-gray-300 rounded-sm"
                placeholder="Search By No."
              />
            </span>
          </div>
          <div class="max-h-[500px] h-auto box-border overflow-auto">
            <div v-for="(courses, category) in filtered_course_list" class="my-2">
              <details v-if="courses.length !== 0">
                <summary class="font-text" v-html="category"></summary>
                <div
                  v-for="course in courses"
                  @click="() => addCourse(course)"
                  :class="{ 'selected-course': course.is_selected }"
                  class="border box-border px-3 pb-5 pt-4 cursor-pointer my-2 rounded-md border-gray-300"
                >
                  <p
                    class="font-medium overflow-ellipsis w-80"
                    v-html="
                      course.course_name + ' - ' + course.subject + ' ' + course.course_number + ''
                    "
                  ></p>
                  <p class="text-[15px]" v-for="meeting in course.meeting_times">
                    {{ meeting.meeting_type_description }} Times: {{ formatMeetingTime(meeting) }}.
                    {{
                      formatCourseDays(meeting) !== '' ? `Days: ${formatCourseDays(meeting)}` : ''
                    }}
                  </p>
                  <p class="text-[15px]">
                    Section {{ course.section }} | Credits: {{ course.credits }}
                  </p>
                  <p v-if="course.attributes && course.attributes.length > 0">
                    Attributes: {{ formatCourseAttributes(course) }}
                  </p>
                  <!-- <p v-if="course.credits"></p> -->
                </div>
              </details>
            </div>
          </div>
          <h2 class="text-xl font-text font-bold mt-5">Selected Courses</h2>
          <p class="my-3" v-if="chosen_courses.length !== 0">
            <span @click="copyToClipboard" class="underline cursor-pointer">Copy to Clipboard</span>
            | Total Credits:
            {{ totalCreditsSelected }}
          </p>
          <p v-if="chosen_courses.length == 0" class="mt-3">No courses have been selected yet</p>
          <div v-else>
            <div v-for="course in chosen_courses">
              <div class="flex mt-2 items-center gap-4">
                <img
                  :src="CancelIcon"
                  class="w-3 cursor-pointer"
                  @click="() => removeCourse(course)"
                  alt="Cancel Icon"
                />
                <p>
                  {{ course.course_name }} - {{ course.subject }} {{ course.course_number }} - CRN
                  {{ course.course_reference_number }} ({{ course.credits ?? 'No' }}
                  credits)
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="w-full">
          <vue-cal
            :events="events"
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
      </div>
    </section>
    <div class="absolute bottom-5 right-3">
      <button
        @click="feedback_popup_is_visible = true"
        class="bg-udmercy-blue text-white font-text shadow-md font-medium px-5 text-sm py-3 rounded-full cursor-pointer"
      >
        Feedback/Comments
      </button>
    </div>

    <Dialog
      v-model:visible="feedback_popup_is_visible"
      modal
      header="Feedback/Comments"
      :style="{ width: '25rem', 'font-family': 'Raleway' }"
    >
      <span class="text-surface-500 font-medium dark:text-surface-400 block mb-8"
        >Provide feedback, comments, or bugs!</span
      >
      <textarea
        name="feedback"
        placeholder="Enter Feedback"
        v-model="feedback_message"
        class="border border-gray-300 mt-[-10px] box-border p-3 rounded-md block w-full h-40"
        id="text-area"
      ></textarea>
      <button
        @click="sendFeedback"
        class="bg-udmercy-blue mt-6 text-white font-text shadow-md font-medium px-5 text-sm py-3 rounded-full cursor-pointer"
      >
        Send Feedback
      </button>
    </Dialog>
  </main>
</template>

<script lang="ts" setup>
// @ts-expect-error
import VueCal from 'vue-cal'
import CancelIcon from '../assets/cancel-icon.png'
import axios from 'axios'
import Dialog from 'primevue/dialog'
import { useClipboard } from '@vueuse/core'
import { computed, onMounted, ref } from 'vue'
import { TYPE, useToast } from 'vue-toastification'

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
const feedback_message = ref<string>('')
const events = ref<any>([])
const ordered_course_list = ref<any>({})
const chosen_courses = ref<any>([])
const jsessionid = ref('')
const course_types = ref<any>([])
const awsalb = ref('')
const awsalbcors = ref('')
const use_cache = ref<boolean>(true)
const search_by_name_field = ref<string>('')
const search_by_attribute_field = ref<string>('')
const search_by_course_no_field = ref<string>('')
const search_by_course_type = ref<string | null>(null)
const feedback_popup_is_visible = ref<boolean>(false)

function onEventClick(event: any) {
  // console.log(event)
}

const filtered_course_list = computed(() => {
  let filtered_courses = { ...ordered_course_list.value }

  // Filter by course name
  if (search_by_name_field.value.trim() !== '') {
    for (let key in filtered_courses) {
      filtered_courses[key] = filtered_courses[key].filter((course: any) =>
        course.course_name.toLowerCase().includes(search_by_name_field.value.toLowerCase()),
      )
    }
  }

  // Filter by attribute
  if (search_by_attribute_field.value.trim() !== '') {
    for (let key in filtered_courses) {
      filtered_courses[key] = filtered_courses[key].filter((course: any) =>
        course.attributes.some((attribute: any) =>
          attribute.code.toLowerCase().includes(search_by_attribute_field.value.toLowerCase()),
        ),
      )
    }
  }

  // Filter by course number
  if (search_by_course_no_field.value.trim() !== '') {
    for (let key in filtered_courses) {
      filtered_courses[key] = filtered_courses[key].filter((course: any) =>
        course.course_number.toLowerCase().includes(search_by_course_no_field.value.toLowerCase()),
      )
    }
  }

  // Filter by course type
  if (search_by_course_type.value && search_by_course_type.value.trim() !== '') {
    for (let key in filtered_courses) {
      filtered_courses[key] = filtered_courses[key].filter((course: any) =>
        // @ts-ignore
        course.subject.toLowerCase().includes(search_by_course_type.value.toLowerCase()),
      )
    }
  }

  return filtered_courses
})

function formatCourseAttributes(course: any) {
  const attrs: any = []
  course.attributes.forEach((attr: any) => {
    attrs.push(attr.code.replace('KA', ''))
  })

  return attrs.join(' | ')
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

function formatMeetingTime(meeting: any) {
  if (meeting.meeting_begin_time === null) {
    return 'No time specified'
  }

  const meeting_time = `${meeting.meeting_begin_time.slice(0, 2)}:${meeting.meeting_begin_time.slice(2)} - ${meeting.meeting_end_time.slice(0, 2)}:${meeting.meeting_end_time.slice(2)}`

  return meeting_time
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

  if (days.length === 0) {
    return ''
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
    const course_categories: any = {}

    courses.forEach((course: any) => {
      if (!course_categories[course.subject]) {
        course_categories[course.subject] = course.course_description
      }

      if (!ordered_course_list.value[course.course_description]) {
        ordered_course_list.value[course.course_description] = [course]
      } else {
        ordered_course_list.value[course.course_description].push(course)
      }
    })

    course_types.value = course_categories

    // After fetching the course
    courses_are_being_fetched.value = false
    courses_have_been_fetched.value = true
  } catch (err) {
    alert(err)
    console.log(err)
  }
}

function formatCourseTime(meeting: any) {
  if (!meeting.meeting_begin_time) {
    return 'No meeting time was specified'
  }

  let beginTimeC = meeting.meeting_begin_time
  let begintime = beginTimeC.slice(0, 2) + ':' + beginTimeC.slice(2)

  let endTimeC = meeting.meeting_end_time
  let endtime = endTimeC.slice(0, 2) + ':' + endTimeC.slice(2)

  return `${meeting.meeting_type_description}: ${begintime} - ${endtime}. Days: ${formatCourseDays(meeting)} `
}

const totalCredits = computed(() => {
  let total_creds = 0
  chosen_courses.value.forEach((course: any) => {
    total_creds += course.credits
  })

  return total_creds
})

const toast = useToast()

function copyToClipboard() {
  let final_course_content = ''
  chosen_courses.value.forEach((course: any) => {
    let meeting_times = ''

    course.meeting_times.forEach((meeting: any) => {
      meeting_times += formatCourseTime(meeting) + '\n'
    })

    final_course_content += `Course Name: ${course.course_name} (${course.subject} ${course.course_number})

Meeting Times:
${meeting_times}
Credits: ${course.credits}
Section: ${course.section}
CRN: ${course.course_reference_number}

---------------------------

`
  })

  final_course_content += `Total Credits: ${totalCredits.value}`

  const source = ref(final_course_content)
  const { text, copy, copied, isSupported } = useClipboard({ source })
  copy(final_course_content)

  if (isSupported) {
    toast.clear()
    toast('Successfully copied to clipboard', {
      type: TYPE.INFO,
    })
  } else {
    toast('Copying is not supported', {
      type: TYPE.INFO,
    })
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
    events.value = events.value.filter((classs: any) => classs.course_id !== course.course_id)
    return
  }

  course.is_selected = true
  chosen_courses.value.push(course)

  course.meeting_times.forEach((meeting: any) => {
    if (meeting.meeting_begin_time) {
      let beginTimeC = meeting.meeting_begin_time
      let begintime = beginTimeC.slice(0, 2) + ':' + beginTimeC.slice(2)

      let endTimeC = meeting.meeting_end_time
      let endtime = endTimeC.slice(0, 2) + ':' + endTimeC.slice(2)

      let days = []

      if (meeting.monday) {
        days.push('05')
      }
      if (meeting.tuesday) {
        days.push('06')
      }
      if (meeting.wednesday) {
        days.push('07')
      }
      if (meeting.thursday) {
        days.push('08')
      }
      if (meeting.friday) {
        days.push('09')
      }
      if (meeting.saturday) {
        days.push('10')
      }
      if (meeting.sunday) {
        days.push('11')
      }

      days.forEach((day) => {
        let starttime = '2025-05-' + day + ' ' + begintime
        let endtimes = '2025-05-' + day + ' ' + endtime

        events.value.push({
          start: starttime,
          end: endtimes,
          title: `${course.subject} ${course.course_number} - ${course.course_name}`,
          content: `<p>${meeting.meeting_type_description}</p>`,
          class: 'health',
          course_id: course.course_id,
        })
      })
    }
  })
}

const totalCreditsSelected = computed(() => {
  let sum = 0
  chosen_courses.value.forEach((course: any) => {
    sum += course.credits
  })
  return sum
})

async function sendFeedback() {
  try {
    let res = await axios.post(`${import.meta.env.VITE_API_URL}/send_feedback`, {
      feedback_message: feedback_message.value,
    })

    alert('Feedback sent successfully')

    feedback_message.value = ''
    feedback_popup_is_visible.value = false
  } catch (err) {
    alert('An unexpected error occured')
  }
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
  background-color: rgba(2, 35, 99, 0.9);
  border: 1px solid rgba(2, 35, 99, 0.9);
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
<!-- convert json to sql -->
