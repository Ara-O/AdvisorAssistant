<template>
  <div class="max-w-[400px] w-full min-w-[300px]">
    <h2 class="text-xl font-text font-bold mb-1">All Courses</h2>
    <div class="flex gap-3 mt-3 mb-3">
      <div class="w-full">
        <label for="subject_search" class="block font-semibold">Subject</label>
        <select
          type="text"
          id="subject_search"
          v-model="search_by_course_subject"
          class="border border-solid mt-2 px-3 w-full h-9 font-text max-w-48 text-sm py-2 border-gray-300 rounded-sm"
          :class="search_by_course_subject === null ? 'text-gray-500' : ''"
          placeholder="Subject"
        >
          <option :value="null">Show all Subjects</option>
          <option :value="acronym" v-for="(full_title, acronym) in props.course_categories">
            {{ acronym }}: {{ full_title }}
          </option>
        </select>
      </div>
      <div class="w-full">
        <label for="course_no_search" class="block font-semibold">Course Number</label>
        <input
          type="text"
          id="course_no_search"
          v-model="search_by_course_no_field"
          class="border border-solid mt-2 px-3 h-9 w-full max-w-48 font-text text-sm py-2 border-gray-300 rounded-sm"
          placeholder="Search By No."
        />
      </div>
    </div>
    <div class="mt-3 mb-3 gap-3 flex">
      <div>
        <label for="name_search" class="block font-semibold">Course Title</label>
        <input
          type="text"
          id="name_search"
          v-model="search_by_name_field"
          class="border border-solid mt-2 px-3 w-full h-9 max-w-48 font-text text-sm py-2 border-gray-300 rounded-sm"
          placeholder="Search By Course Title"
        />
      </div>
      <div>
        <label for="name_search" class="block font-semibold">Attribute</label>
        <input
          type="text"
          id="name_search"
          v-model="search_by_attribute_field"
          class="border border-solid mt-2 px-3 w-full h-9 font-text max-w-48 text-sm py-2 border-gray-300 rounded-sm"
          placeholder="Search By Attribute"
        />
      </div>
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
              v-html="course.course_name + ' - ' + course.subject + ' ' + course.course_number + ''"
            ></p>
            <p class="text-[15px]" v-for="meeting in course.meeting_times">
              {{ meeting.meeting_type_description }} Times: {{ formatMeetingTime(meeting) }}.
              {{ formatCourseDays(meeting) !== '' ? `Days: ${formatCourseDays(meeting)}` : '' }}
            </p>
            <p class="text-[15px]">Section {{ course.section }} | Credits: {{ course.credits }}</p>
            <p v-if="course.attributes && course.attributes.length > 0" class="text-[15px]">
              Attributes: {{ formatCourseAttributes(course) }}
            </p>
            <p v-if="course.faculty && course.faculty.length > 0" class="text-[15px]">
              Faculty: {{ course.faculty.join(', ') }}
            </p>
            <!-- <p v-if="course.credits"></p> -->
          </div>
        </details>
      </div>
    </div>
    <div class="h-0.5 bg-blue-50 my-5 rounded-full"></div>
    <h2 class="text-xl font-text font-bold">Selected Courses</h2>
    <p class="my-3" v-if="props.chosen_courses.length !== 0">
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
            @click="() => emits('remove-course', course)"
            alt="Cancel Icon"
          />
          <p>
            {{ course.course_name }} - {{ course.subject }} {{ course.course_number }} ({{
              course.section
            }}) - CRN {{ course.course_reference_number }} ({{ course.credits ?? 'No' }}
            credits)
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import CancelIcon from '../assets/cancel-icon.png'
import { useClipboard } from '@vueuse/core'
import { computed, ref } from 'vue'
import { TYPE, useToast } from 'vue-toastification'

const props = defineProps(['courses_data', 'course_categories', 'events', 'chosen_courses'])
const emits = defineEmits(['add-course', 'remove-course'])

const search_by_name_field = ref<string>('')
const search_by_attribute_field = ref<string>('')
const search_by_course_no_field = ref<string>('')
const search_by_course_subject = ref<string | null>(null)

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
  props.chosen_courses.forEach((course: any) => {
    total_creds += course.credits
  })

  return total_creds
})

const toast = useToast()

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

const filtered_course_list = computed(() => {
  let filtered_courses = { ...props.courses_data }

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
  if (search_by_course_subject.value && search_by_course_subject.value.trim() !== '') {
    for (let key in filtered_courses) {
      filtered_courses[key] = filtered_courses[key].filter((course: any) =>
        // @ts-ignore
        course.subject.toLowerCase().includes(search_by_course_subject.value.toLowerCase()),
      )
    }
  }

  console.log(filtered_courses)
  return filtered_courses
})

function formatCourseAttributes(course: any) {
  const attrs: any = []
  course.attributes.forEach((attr: any) => {
    attrs.push(attr.code.replace('KA', ''))
  })

  return attrs.join(' | ')
}

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
    props.chosen_courses.value = props.chosen_courses.filter(
      (coursed: any) => coursed.course_id !== course.course_id,
    )

    console.log(props.events)

    emits('remove-course', { course_id: course.course_id })
    return
  }

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

      let overlap = false
      let overlap_course: any = {}

      if (overlap) {
        toast(`There is an overlap with ${overlap_course?.title || 'another course'}`, {
          type: TYPE.ERROR,
        })
        course.is_selected = false
        props.chosen_courses.pop()
      } else {
        days.forEach((day) => {
          let starttime = '2025-05-' + day + ' ' + begintime
          let endtimes = '2025-05-' + day + ' ' + endtime

          emits('add-course', {
            start: starttime,
            end: endtimes,
            title: `${course.subject} ${course.course_number} - ${course.course_name}`,
            content: ``,
            class: 'valid',
            course_id: course.course_id,
          })
        })
      }
    }
  })
}

const totalCreditsSelected = computed(() => {
  let sum = 0
  props.chosen_courses.forEach((course: any) => {
    sum += course.credits
  })
  return sum
})
</script>
