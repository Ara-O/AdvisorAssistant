<template>
  <main>
    <!-- Select term -->
    <select-term @term-has-been-selected="onTermHasBeenSelected" v-if="progress === 0"
      >Pick the semester you need advising for.</select-term
    >

    <upload-degree-evaluation-file v-if="progress === 1"></upload-degree-evaluation-file>
  </main>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import SelectTerm from '@/components/SelectTerm.vue'
import FileUpload from 'primevue/fileupload'
import UploadDegreeEvaluationFile from '@/components/UploadDegreeEvaluationFile.vue'
import { Dialog } from 'primevue'
import { useToast, TYPE } from 'vue-toastification'
import CancelIcon from '../assets/cancel-icon.png'
import axios from 'axios'
import { useClipboard } from '@vueuse/core'

import type { Term } from '@/types/types'

const selected_term = ref<Term>()
const progress = ref<number>(0)

const course_history_verified = ref<boolean>(false)
const requirements_satisfied = ref<any>([])
const requirements_not_satisfied = ref<any>([])
const processed_requirements = ref()
const course_info_is_visible = ref<boolean>(false)
const toast = useToast()

const events = ref<any>([])
const course_types = ref<any>([])

const hide_courses_not_offered = ref<boolean>(true)
const course_viewer_popup_is_visible = ref<boolean>(false)
const chosen_courses = ref<any>([])
const course_prerequisites = ref<any>([])
const course_corequisites = ref<any>([])
const course_to_add = ref({})
const search_by_name_field = ref<string>('')
const search_by_attribute_field = ref<string>('')
const search_by_course_no_field = ref<string>('')
const search_by_course_type = ref<string | null>(null)
const add_course_number = ref<string>('')
const add_course_subject = ref<string | null>(null)

function onTermHasBeenSelected(term: Term, refresh_data: boolean) {
  console.log(term, refresh_data)
  progress.value++
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
      processed_requirements.value[`${add_course_subject.value} ${add_course_number.value}`] =
        res.data

      toast.clear()
      toast('Course Added to List', {
        type: TYPE.INFO,
        timeout: 10000,
      })
    }

    // courses.forEach((course: any) => {
    //   // processed_requirements
    //   if (!course_categories[course.subject]) {
    //     course_categories[course.subject] = course.course_description
    //   }

    //   if (!ordered_course_list.value[course.course_description]) {
    //     ordered_course_list.value[course.course_description] = [course]
    //   } else {
    //     ordered_course_list.value[course.course_description].push(course)
    //   }
    // })

    console.log(res)
  } catch (err) {}
}

const retrieved_terms = ref({})

const ordered_course_list = ref<any>({})

onMounted(async () => {
  let res = await axios.get(`${import.meta.env.VITE_API_URL}/fetch_courses`, {
    params: {
      term_name: 'Fall 2025',
      term_code: '202610',
      use_cache: true,
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

  console.log(ordered_course_list.value)
})

const feedback_message = ref<string>('')

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

// function parseSatisfiedAttrs(req: any): string {
//   if (req.attributes_satisfied.length == 0) {
//     return 'No attributes found (may not be updated)'
//   }

//   return req.attributes_satisfied.join(' | ')
// }

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

  return days.join(' | ')
}

async function addCourse(course: any) {
  try {
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

    toast.clear()
    toast('Verifying if you can take the course...', {
      type: TYPE.INFO,
      timeout: 10000,
    })

    let res = await axios.post(`${import.meta.env.VITE_API_URL}/check_course_validity`, {
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

function userHasAddedCourse(course: any) {
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
          content: `<p>${meeting.meeting_type_description} </p>`,
          class: 'health',
          course_id: course.course_id,
        })
      })
    }
  })
  course_to_add.value = {}
  course_info_is_visible.value = false
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
  chosen_courses.value.forEach((course: any) => {
    total_creds += course.credits
  })

  return total_creds
})

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
  }
}

function saveAsTxtFile() {
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
