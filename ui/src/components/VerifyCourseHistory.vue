<template>
  <section class="flex items-center flex-col justify-center h-screen">
    <div class="text-center flex flex-col gap-5 px-10">
      <h1 class="font-title font-medium text-4xl">Verify your Course History</h1>
      <p class="text-md leading-8">
        The course extraction may not be perfect. Look through the courses to make sure they match,
        or at least look good enough
      </p>
      <section class="flex justify-center gap-20">
        <article class="px-10 w-1/3">
          <p class="font-medium text-xl underline mb-4">Requirements Not Satisfied:</p>
          <p class="mb-4">These reflect how they are shown in your Degree Evaluation</p>
          <button
            @click="removeCoursesWithUnsatisfiedPrereqs"
            class="bg-udmercy-blue mt-0 cursor-pointer font-semibold text-sm px-6 py-3 rounded-md font-text text-white"
          >
            Remove courses with unsatisfied prerequisites
          </button>
          <div class="max-h-[50vh] overflow-auto px-5">
            <p
              v-for="requirement in props.requirements.requirements_not_satisfied"
              class="font-text text-left mb-5 cursor-pointer text-md font-medium leading-8"
            >
              - {{ requirement }}
            </p>
            <!-- <div class="mt-5">
                    <p>Missing Courses: {{ requirement.courses.join(', ') }}</p>
                  </div> -->
          </div>
        </article>
        <div class="h-full w-0.5 bg-gray-300 rounded-md"></div>
        <article class="w-1/3">
          <p class="font-medium text-xl underline mb-4">Requirements Satisfied:</p>
          <p class="mb-4">Hover over a course to see the attributes it satisfies</p>
          <div class="max-h-[50vh] px-5 overflow-auto flex flex-wrap justify-start gap-5 gap-x-10">
            <span
              v-for="req in props.requirements.requirements_satisfied"
              class="flex gap-4 justify-center items-center"
            >
              <img :src="GreenCheck" alt="Check Icon" class="w-3" />
              <input
                type="text"
                :value="req.grade || 'In Prog'"
                class="w-15 border-b outline-0 font-text text-center"
              />
              <p
                class="w-96 whitespace-nowrap text-start cursor-pointer text-ellipsis"
                :title="req.attributes"
              >
                ({{ req.requirement }}) - {{ req.title }}
                {{ req.attributes.length > 0 ? '(' + req.attributes + ')' : '' }}
              </p>
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
</template>

<script lang="ts" setup>
import GreenCheck from '@/assets/green-logo.webp'
import axios from 'axios'

const props = defineProps(['requirements', 'selected_term'])
const emits = defineEmits(['start-advisor-assistant'])

function startAdvisorAssistant() {
  emits('start-advisor-assistant')
}

async function removeCoursesWithUnsatisfiedPrereqs() {
  try {
    await axios.post(
      `${import.meta.env.VITE_API_URL}/api/remove-courses-with-unsatisfied-prereqs`,
      {
        requirements: props.requirements,
        term: props.selected_term,
      },
    )
  } catch (err) {
    console.log(err)
  }
}
</script>
