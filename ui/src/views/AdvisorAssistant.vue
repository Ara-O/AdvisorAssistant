<template>
  <main>
    <section
      v-if="!degree_evaluation_was_uploaded"
      class="w-full text-center h-screen flex flex-col gap-4 justify-center items-center"
    >
      <h1 class="font-title font-medium text-4xl">Upload your Student Evaluation</h1>
      <p class="font-text font-medium">Upload your student evaluation file as an MHTML file</p>
      <p class="max-w-3xl leading-8">
        To convert your degree evaluation to a .mhtml format, go to the degree evaluation page, and
        click CTRL S. Make sure to save the webpage as one file (in .mhtml format). Your degree
        evaluation file is not saved anywhere (except in the process of extracting your courses,
        after which it is permanently deleted)
      </p>

      <FileUpload
        ref="fileupload"
        mode="basic"
        name="degree_eval"
        :url="upload_url"
        @upload="onUpload"
        class="!bg-udmercy-blue !border-udmercy-blue"
      />
      <button
        class="bg-udmercy-blue cursor-pointer font-semibold text-sm px-6 py-3 rounded-md mt-1 font-text text-white"
        @click="upload"
      >
        Upload File
      </button>
    </section>
    <section v-else>
      <section
        class="flex items-center flex-col justify-center h-screen"
        v-if="!course_history_verified"
      >
        <div class="text-center flex flex-col gap-5 px-15">
          <h1 class="font-title font-medium text-4xl">Verify your Course History</h1>
          <p class="text-md leading-8">
            The course extraction may not be perfect. Look through the courses to make sure they
            match, or at least look good enough
          </p>
          <section class="flex justify-center gap-20">
            <article class="w-1/3">
              <p class="font-medium text-xl underline mb-5">Requirements Not Satisfied:</p>
              <div class="max-h-[50vh] overflow-auto px-5">
                <details v-for="requirement in requirements_not_satisfied" class="mb-5">
                  <summary class="font-text cursor-pointer text-md font-medium leading-8">
                    {{ requirement.caption }}
                  </summary>
                  <div class="mt-5">
                    <p>Missing Courses: {{ requirement.courses.join(', ') }}</p>
                  </div>
                </details>
              </div>
            </article>
            <div class="h-full w-0.5 bg-gray-300 rounded-md"></div>
            <article class="max-w-1/3">
              <p class="font-medium text-xl underline mb-5">Requirements Satisfied:</p>
              <div class="max-h-[50vh] px-5 overflow-auto flex flex-wrap justify-between gap-5">
                <span
                  v-for="req in requirements_satisfied"
                  class="flex gap-4 justify-center items-center"
                >
                  <img
                    :src="CancelIcon"
                    alt="Cancel Icon"
                    class="w-3 cursor-pointer"
                    @click="() => removeSatisfiedReq(req)"
                  />
                  <p
                    class="w-22 whitespace-nowrap overflow-hidden text-ellipsis"
                    :title="req.course"
                  >
                    {{ req.course }}:
                  </p>
                  <input
                    type="text"
                    v-model="req.grade"
                    class="w-10 border-b outline-0 text-center"
                  />
                </span>
              </div>
            </article>
          </section>
        </div>
        <button
          class="bg-udmercy-blue mt-5 cursor-pointer font-semibold text-sm px-6 py-3 rounded-md font-text text-white"
          @click="startAdvisorAssistant"
        >
          Looks Good!
        </button>
      </section>
      <!-- PROCESSED REQS SECTION -->
      <section class="p-5 flex gap-8" v-else>
        <div class="w-lg">
          <h1 class="font-title text-2xl mb-3 font-medium">Missing Requirements</h1>
          <p>
            Outstanding courses are automatically fetched based on either their course code or the
            necessary attributes
          </p>
          <div class="max-h-[85vh] overflow-auto">
            <div v-for="(val, key) in processed_requirements">
              <details>
                <summary class="font-title text-xl my-2">{{ key }}</summary>
                <div v-if="val.length > 0">
                  <div
                    v-for="course in val"
                    class="border box-border px-3 pb-5 pt-4 my-2 rounded-md border-gray-300"
                    @click="() => addCourse(course)"
                    :class="{ 'selected-course': course.is_selected }"
                  >
                    <p class="font-medium overflow-ellipsis w-80">
                      {{ course.subject }} {{ course.course_number }} - {{ course.course_name }}
                    </p>
                    <p class="text-md">
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
                        course.meeting_end_time.slice(0, 2) +
                        ':' +
                        course.meeting_end_time.slice(2)
                      }}. Days: {{ formatCourseDays(course) }}.
                    </p>
                    <p v-else>This course does not have a set meeting time</p>
                    <p v-if="course.attributes && course.attributes.length > 0">
                      Attributes: {{ formatCourseAttributes(course) }}
                    </p>
                    <p v-if="course.credits">Credits: {{ course.credits }}</p>
                  </div>
                </div>

                <p class="text-md" v-else>Not Offered</p>
              </details>
            </div>
          </div>
        </div>
        <div class="w-full h-screen">
          <h1 class="font-title text-2xl mb-4 font-medium">Course Calendar</h1>
          <vue-cal
            :events="events"
            selected-date="2025-05-05"
            :time-from="8 * 60"
            hide-view-selector
            :time-cell-height="60"
            hide-title-bar
            :time-to="23 * 60"
            :disable-views="['years', 'year', 'month']"
          >
          </vue-cal>
        </div>
      </section>
    </section>
  </main>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import FileUpload from 'primevue/fileupload'
import CancelIcon from '../assets/cancel-icon.png'
import axios from 'axios'
// @ts-ignore
import VueCal from 'vue-cal'

const degree_evaluation_was_uploaded = ref<boolean>(false)
const course_history_verified = ref<boolean>(false)
const requirements_satisfied = ref<any>([])
const requirements_not_satisfied = ref<any>([])
const processed_requirements = ref()

const fileupload = ref()
const events = ref<any>([])
const chosen_courses = ref<any>([])

const upload_url = computed(() => {
  return `${import.meta.env.VITE_API_URL}/upload_degree_evaluation`
})

const upload = () => {
  fileupload.value.upload()
}

function formatCourseAttributes(course: any) {
  const attrs: any = []
  course.attributes.forEach((attr: any) => {
    attrs.push(attr.code.replace('KA', ''))
  })

  return attrs.join(' | ')
}

function onUpload(event: any) {
  const response = JSON.parse(event.xhr.response)
  requirements_satisfied.value = response.requirements_satisfied
  requirements_not_satisfied.value = response.requirements_not_satisfied
  degree_evaluation_was_uploaded.value = true
  console.log(response)
}

function removeSatisfiedReq(req_param: any) {
  requirements_satisfied.value = requirements_satisfied.value.filter(
    (req: any) => !(req.course === req_param.course && req.grade === req_param.grade),
  )
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

  let enddate = course.start_date.split('/')
  let formattedEndDate = enddate[2] + '-' + enddate[1] + '-' + enddate[0]
  let startdate = course.end_date.split('/')
  let formattedStartDate = startdate[2] + '-' + startdate[1] + '-' + startdate[0]

  if (course.meeting_begin_time) {
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
}

async function startAdvisorAssistant() {
  try {
    course_history_verified.value = true

    let res = await axios.post(`${import.meta.env.VITE_API_URL}/start-assistant`, {
      requirements_not_satisfied: requirements_not_satisfied.value,
      requirements_satisfied: requirements_satisfied.value,
    })

    processed_requirements.value = res.data
  } catch (err) {}
}
</script>
