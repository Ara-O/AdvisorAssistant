<template>
  <button
    @click="showDialog"
    class="bg-udmercy-blue absolute bottom-4 right-4 mt-6 text-white font-text shadow-md font-medium px-5 text-sm py-3 rounded-full cursor-pointer"
  >
    Send Feedback
  </button>
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
      class="border border-gray-300 min-h-22 mt-[-10px] box-border p-3 rounded-md block w-full h-40"
      id="text-area"
    ></textarea>

    <button
      @click="sendFeedback"
      class="bg-udmercy-blue mt-6 text-white font-text shadow-md font-medium px-5 text-sm py-3 rounded-full cursor-pointer"
    >
      Send Feedback
    </button>
  </Dialog>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { Dialog } from 'primevue'
import axios from 'axios'
import { useToast, TYPE } from 'vue-toastification'

const feedback_popup_is_visible = ref<boolean>(false)
const feedback_message = ref<string>('')
const toast = useToast()

function showDialog() {
  feedback_popup_is_visible.value = true
}

async function sendFeedback() {
  try {
    await axios.post(`${import.meta.env.VITE_API_URL}/send_feedback`, {
      feedback_message: feedback_message.value,
    })

    toast.clear()
    toast('Feedback sent successfully', {
      type: TYPE.INFO,
    })

    feedback_message.value = ''
    feedback_popup_is_visible.value = false
  } catch (err) {
    toast('An unexpected error occured when sending your feedback. Please try again later', {
      type: TYPE.ERROR,
    })
  }
}
</script>
