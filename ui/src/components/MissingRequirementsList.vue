<template>
  <div class="w-lg">
    <div class="h-[75vh] pb-10 box-border overflow-auto">
      <h1 class="font-title text-2xl mb-3 font-medium">Missing Requirements</h1>
      <div class="mb-3 cursor-pointer">
        <label for="hide_courses_not_offered">Hide Courses that are not Offered</label>
        <input
          type="checkbox"
          class="ml-4"
          id="hide_courses_not_offered"
          v-model="hide_courses_not_offered"
        />
      </div>
      <div>
        <p>Add a Course not shown below</p>
        <div class="flex gap-4 h-9 mt-3 mb-5">
          <select
            id="subject_search"
            v-model="add_course_subject"
            class="border border-solid h-10 px-3 w-36 font-text text-sm py-2 border-gray-300 rounded-sm"
            placeholder="Search By Subject"
          >
            <option :value="null">Subject</option>
            <option :value="acronym" v-for="(full_title, acronym) in course_categories">
              {{ acronym }}: {{ full_title }}
            </option>
          </select>
          <input
            type="text"
            v-model="add_course_number"
            class="border border-solid px-3 w-full h-10 font-text text-sm py-2 border-gray-300 rounded-sm"
            placeholder="Course Number"
          />
          <button
            @click="fetchCourseWithSubjectAndNumber"
            class="bg-udmercy-blue w-30 h-10 cursor-pointer rounded-md text-2xl text-white"
          >
            <p class="text-4xl">+</p>
          </button>
        </div>
      </div>
      <!-- <p class="underline cursor-pointer mb-4" @click="course_viewer_popup_is_visible = true">
               Viewer
            </p> -->
      <!-- <p class="mb-3">
              Outstanding courses are automatically fetched based on either their course subject or
              the necessary attributes
            </p> -->
      <div class="max-h-[85vh] w-96">
        <div v-for="(val, key) in processed_requirements">
          <details v-if="val.length > 0 || hide_courses_not_offered === false">
            <summary class="font-title text-xl my-2">{{ key }}</summary>
            <div v-if="val.length > 0">
              <div
                v-for="course in val"
                class="border box-border px-3 pb-5 cursor-pointer pt-4 my-2 rounded-md border-gray-300"
                @click="() => addCourse(course)"
                :class="{ 'selected-course': course.is_selected }"
              >
                <p
                  class="font-medium overflow-ellipsis w-80"
                  v-html="`${course.subject} ${course.course_number} - ${course.course_name}`"
                ></p>
                <p class="text-md">
                  Course Number: {{ course.course_number }} | Section {{ course.section }}
                </p>

                <p class="text-[15px]" v-for="meeting in course.meeting_times">
                  {{ meeting.meeting_type_description }} Times: {{ formatMeetingTime(meeting) }}.
                  {{ formatCourseDays(meeting) !== '' ? `Days: ${formatCourseDays(meeting)}` : '' }}
                </p>
                <p v-if="course.attributes && course.attributes.length > 0" class="text-[15px]">
                  Attributes: {{ formatCourseAttributes(course) }}
                </p>
                <p v-if="course.credits" class="text-[15px]">Credits: {{ course.credits }}</p>
                <p v-if="course.faculty && course.faculty.length > 0" class="text-[15px]">
                  Faculty: {{ course.faculty.join(', ') }}
                </p>
              </div>
            </div>

            <p class="text-md" v-else>Not Offered</p>
          </details>
        </div>
      </div>
    </div>
    <div class="h-0.5 my-5 bg-gray-200 rounded-sm"></div>
    <div>
      <h1 class="font-title text-2xl mb-3 font-medium">
        Chosen Courses ({{ totalCredits }} credits)
      </h1>
      <p class="">
        <span class="underline cursor-pointer" @click="saveAsTxtFile">
          Click to save as a .txt file</span
        >
        |
        <span class="cursor-pointer underline" @click="copyToClipboard"> Copy to Clipboard</span>
      </p>
      <ul class="mt-3 max-h-30 overflow-auto">
        <li v-for="course in chosen_courses" class="font-text mb-3 flex items-center gap-4">
          <img
            :src="CancelIcon"
            alt="Cancel Icon"
            class="w-3 cursor-pointer"
            @click="removeCourse(course)"
          />
          <div>
            <p class="font-medium">
              {{ course.course_name }} ({{ course.subject }} {{ course.course_number }}) - CRN
              {{ course.course_reference_number }}
            </p>
            <!-- <p>{{ formatCourseTime(course.meeting_times) }}</p> -->
          </div>
        </li>
      </ul>
    </div>
    <Dialog
      v-model:visible="course_info_is_visible"
      modal
      header="Course Information"
      :style="{ width: '25rem', 'font-family': 'Raleway' }"
    >
      <p class="text-surface-500 font-semibold dark:text-surface-400 block mt-[-5px]">
        Prerequisites
      </p>
      <div class="mt-2" v-if="course_prerequisites !== 'No prerequisite information available.'">
        <p v-if="course_prerequisites.length == 0">No prerequitie information available</p>
        <div v-else>
          <div v-for="req in course_prerequisites" class="leading-8">
            <p v-if="req === 'and'">and</p>
            <p v-else-if="req === 'or'">or</p>

            <template v-else>
              <p>{{ req.subject }} {{ req.course_number }}. Minimum Grade: {{ req.min_grade }}</p>
              <p>
                Requirement Satisfied: {{ checkForSatisfiedReq(req.subject, req.course_number) }}
              </p>
            </template>
            <hr class="my-3 text-gray-300" />
          </div>
        </div>
      </div>
      <p class="mt-2" v-else>No prerequisites were found</p>
      <p class="text-surface-500 mt-4 font-semibold dark:text-surface-400 block">Corequisites</p>

      <p class="mt-2">
        {{
          course_corequisites === 'No co reqs information available.'
            ? 'No corequisites were found'
            : course_corequisites.join(', ')
        }}
      </p>

      <button
        class="bg-udmercy-blue mt-6 text-white font-text shadow-md font-medium px-5 text-sm py-3 rounded-full cursor-pointer"
        @click="() => userHasAddedCourse(course_to_add)"
      >
        Add Course
      </button>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import { useToast, TYPE } from 'vue-toastification'
import CancelIcon from '../assets/cancel-icon.png'
import { Dialog } from 'primevue'
import { useClipboard } from '@vueuse/core'

const props = defineProps(['events', 'selected_term', 'processed_requirements', 'chosen_courses'])

const emits = defineEmits(['add-course', 'remove-course'])
const search_by_name_field = ref<string>('')
const search_by_attribute_field = ref<string>('')
const search_by_course_no_field = ref<string>('')
const search_by_course_type = ref<string | null>(null)
const add_course_number = ref<string>('')
const add_course_subject = ref<string | null>(null)
const hide_courses_not_offered = ref<boolean>(true)
const toast = useToast()

const course_categories = ref<any>([])
const requirements = ref()
const course_prerequisites = ref<any>([])
const course_corequisites = ref<any>([])
const course_to_add = ref({})

const ordered_course_list = ref<any>({})
const course_history_verified = ref<boolean>(false)
const requirements_satisfied = ref<any>([])
const requirements_not_satisfied = ref<any>([])
const course_info_is_visible = ref<boolean>(false)

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

function formatMeetingTime(meeting: any) {
  if (meeting.meeting_begin_time === null) {
    return 'No time specified'
  }

  const meeting_time = `${meeting.meeting_begin_time.slice(0, 2)}:${meeting.meeting_begin_time.slice(2)} - ${meeting.meeting_end_time.slice(0, 2)}:${meeting.meeting_end_time.slice(2)}`

  return meeting_time
}

async function addCourse(course: any) {
  try {
    if (course.is_selected) {
      // Deselect the course and remove it from the chosen courses list if it
      course.is_selected = false

      emits('remove-course', { course_id: course.course_id })

      // propsevents = events.value.filter((classs: any) => classs.course_id !== course.course_id)
      return
    }

    toast.clear()
    toast('Verifying if you can take the course...', {
      type: TYPE.INFO,
      timeout: 10000,
    })

    let res = await axios.post(`${import.meta.env.VITE_API_URL}/api/check-course-validity`, {
      course: course,
      requirements_satisfied: requirements_satisfied.value,
    })

    course_corequisites.value = res.data.corequisites
    course_prerequisites.value = res.data.prerequisites
    course_info_is_visible.value = true

    course_to_add.value = course
  } catch (err) {
    console.log(err)
    alert(err)
  }
}
function removeCourse(course: any) {
  // Deselect the course and remove it from the chosen courses list if it
  course.is_selected = false
  // @ts-ignore
  props.chosen_courses = props.chosen_courses.filter(
    (coursed: any) => coursed.course_id !== course.course_id,
  )

  emits('remove-course', { course_id: course.course_id })
  // events.value = events.value.filter((classs: any) => classs.course_id !== course.course_id)
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

function userHasAddedCourse(course: any) {
  course.is_selected = true
  props.chosen_courses.push(course)

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

        emits('add-course', {
          start: starttime,
          end: endtimes,
          title: `${course.subject} ${course.course_number} - ${course.course_name}`,
          content: `<p>${meeting.meeting_type_description} </p>`,
          class: 'valid',
          course_id: course.course_id,
        })
      })
    }
  })
  course_to_add.value = {}
  course_info_is_visible.value = false
}

function checkForSatisfiedReq(subject: any, course_number: any) {
  const course_mappings = {
    ACC: 'Accounting',
    ADS: 'Addiction Studies',
    AEV: 'Advanced Electric Vehicle',
    AAS: 'African-American Studies',
    ALCP: 'American Language & Culture',
    ANE: 'Anesthesiology',
    ARB: 'Arabic',
    AENG: 'Architectural Engineering',
    ARCH: 'Architecture',
    BIO: 'Biology',
    BUS: 'Business Administration',
    CCPD: 'Career & Prof Development',
    CAS: 'Catholic Studies',
    CHM: 'Chemistry',
    CHI: 'Chinese',
    CIVE: 'Civil Engineering',
    CST: 'Communication Studies',
    COM: 'Community Dentistry',
    MCD: 'Community Development',
    CSSE: 'Comp Sci/Software Engineering',
    CIS: 'Computer & Information Systems',
    CNS: 'Counseling',
    CJS: 'Criminal Justice',
    CYBE: 'Cybersecurity',
    DATA: 'Data Analytics',
    DENT: 'Dental General',
    ECN: 'Economics',
    ELEE: 'Electrical Engineering',
    ENGR: 'Engineering',
    CTA: 'Engineering Co-op',
    ENL: 'English',
    ETHL: 'Ethical Leadership',
    ETH: 'Ethics',
    FINA: 'Fine Arts',
    FRE: 'French',
    GEO: 'Geography',
    GER: 'German',
    GRA: 'Graduate Assistant',
    HLH: 'Health Professions',
    HSA: 'Health Services Administration',
    HIS: 'History',
    HON: 'Honors',
    INT: 'Intelligence Analysis',
    ISLM: 'Islamic Studies',
    JPN: 'Japanese',
    KOR: 'Korean',
    LAT: 'Latin',
    LAW: 'Law',
    LEAD: 'Leadership',
    LST: 'Legal Studies',
    MLS: 'Liberal Studies',
    MBA: 'MBA',
    MTH: 'Mathematics',
    MENG: 'Mechanical Engineering',
    MUSM: 'Museum Studies',
    MUS: 'Music',
    NUR: 'Nursing',
    PHL: 'Philosophy',
    PAS: 'Physician Assistant',
    PHY: 'Physics',
    PLS: 'Polish',
    POL: 'Political Science',
    MPD: 'Product Development',
    PYC: 'Psychology',
    RELS: 'Religious Studies',
    SCIE: 'Science',
    SWK: 'Social Work',
    SOC: 'Sociology',
    SPA: 'Spanish',
    STA: 'Statistics',
    TRE: 'Theatre',
    UAS: 'University Academic Services',
    VCE: 'Vehicle Cyber Engineering',
    WGS: "Women's & Gender Studies",
  }

  const reverse_course_mappings = Object.fromEntries(
    Object.entries(course_mappings).map(([key, value]) => [value, key]),
  )

  // console.log(subject)
  const subject_title = reverse_course_mappings[subject]

  if (subject_title === undefined) {
    return "Can't verify"
  }

  let grade_gotten = ''
  requirements_satisfied.value.forEach((req: any) => {
    let course_name = `${subject_title} ${course_number}`
    console.log(`Requirement: "${String(req.requirement)}" (${String(req.requirement).length})`)
    console.log(`Course Name: "${course_name}" (${course_name.length})`)
    if (
      String(req.requirement).replace(/\s+/g, ' ').trim() ===
      course_name.replace(/\s+/g, ' ').trim()
    ) {
      console.log('ALE')
      grade_gotten = req.grade
    }
  })

  if (grade_gotten === '') {
    return 'Not satisfied'
  }

  return `Satisfied with a grade of ${grade_gotten}`
}

const totalCredits = computed(() => {
  let total_creds = 0
  props.chosen_courses.forEach((course: any) => {
    total_creds += course.credits
  })

  return total_creds
})

function copyToClipboard() {
  let final_course_content = ''
  props.chosen_courses.forEach((course: any) => {
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
  }
}

function saveAsTxtFile() {
  let final_course_content = ''
  props.chosen_courses.forEach((course: any) => {
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

  const blob = new Blob([final_course_content], { type: 'text/plain' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'course_selection.txt' // Set file name

  // Trigger download
  document.body.appendChild(link)
  link.click()

  // Cleanup
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
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

const feedback_popup_is_visible = ref<boolean>(false)

function formatCourseAttributes(course: any) {
  const attrs: any = []
  course.attributes.forEach((attr: any) => {
    attrs.push(attr.code.replace('KA', ''))
  })

  return attrs.join(' | ')
}

async function fetchCourseWithSubjectAndNumber() {
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/fetch_course`, {
      params: {
        subject: add_course_subject.value,
        number: add_course_number.value,
      },
    })

    if (res.data.length !== 0) {
      props.processed_requirements[`${add_course_subject.value} ${add_course_number.value}`] =
        res.data

      toast.clear()
      toast('Course Added to List', {
        type: TYPE.INFO,
        timeout: 10000,
      })
    }

    console.log(res)
  } catch (err) {}
}

onMounted(async () => {
  let res = await axios.get(`${import.meta.env.VITE_API_URL}/api/fetch_courses`, {
    params: {
      term_name: props.selected_term.description,
      term_code: props.selected_term.code,
      refresh_course_data: false,
    },
  })

  const courses = res.data
  const categories: any = {}

  courses.forEach((course: any) => {
    if (!categories[course.subject]) {
      categories[course.subject] = course.course_description
    }

    if (!ordered_course_list.value[course.course_description]) {
      ordered_course_list.value[course.course_description] = [course]
    } else {
      ordered_course_list.value[course.course_description].push(course)
    }
  })

  course_categories.value = categories
})
</script>
