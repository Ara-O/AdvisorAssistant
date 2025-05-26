<template>
  <section class="h-screen flex-col items-center flex justify-center">
    <router-link
      to="/"
      class="font-text underline font-medium text-gray-600 absolute top-6 cursor-pointer left-10"
      >Return To Home</router-link
    >
    <h1 class="font-title font-medium text-4xl mb-3">Choose A Term</h1>
    <p><slot></slot></p>
    <select
      class="border font-text text-center rounded-sm h-10 mt-3 w-64 border-gray-400"
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

    <span class="flex mt-5 gap-3">
      <input type="checkbox" id="refresh_course_data" v-model="refresh_course_data" />
      <label for="refresh_course_data">Refresh course data (may take 2–3 minutes)</label>
    </span>
    <button
      @click="selectTerm"
      class="bg-udmercy-blue cursor-pointer font-semibold text-sm px-6 py-3 rounded-md mt-5 font-text text-white"
    >
      Select Term
    </button>
  </section>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { TYPE, useToast } from 'vue-toastification'
import axios from 'axios'

type Term = {
  code: string
  description: string
}

const toast = useToast()
const retrieved_terms = ref<Term[]>([])
const refresh_course_data = ref<boolean>(false)
const selected_term = ref<null | Term>(null)

const emits = defineEmits(['termHasBeenSelected'])

async function selectTerm() {
  if (selected_term.value === null) {
    toast.clear()
    toast('Please select a term.', {
      type: TYPE.ERROR,
    })
    return
  }

  emits('termHasBeenSelected', selected_term.value, refresh_course_data.value)
}

// Fetch the terms
onMounted(async () => {
  try {
    let res = await axios.get(`${import.meta.env.VITE_API_URL}/api/fetch_all_terms`)
    retrieved_terms.value = res.data
  } catch (err) {
    toast('An unexpected error occured when fetching the terms. Please try again later', {
      type: TYPE.ERROR,
    })
    console.log(err)
  }
})
</script>
