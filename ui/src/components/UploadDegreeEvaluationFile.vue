<template>
  <section class="w-full text-center h-screen flex flex-col gap-4 justify-center items-center">
    <router-link
      to="/"
      class="font-text underline font-medium text-gray-600 absolute top-6 cursor-pointer left-10"
      >Return To Home</router-link
    >
    <h1 class="font-title font-medium text-4xl">Upload your Student Evaluation</h1>
    <p class="font-text font-medium">Upload your student evaluation file as an MHTML file</p>
    <p class="max-w-4xl leading-8">
      To convert your degree evaluation to a .mhtml format, go to the degree evaluation page, and
      click CTRL S. Make sure to save the webpage as one file (in .mhtml format).
      <span class="font-semibold">
        Your degree evaluation file is not saved anywhere (except in the process of extracting your
        courses, after which it is permanently deleted)</span
      >
    </p>

    <FileUpload
      ref="fileupload"
      mode="basic"
      name="degree_eval"
      :url="upload_url"
      @upload="onUpload"
      @error="handleUploadError"
      class="!bg-udmercy-blue !border-udmercy-blue"
    />
    <button
      class="bg-udmercy-blue cursor-pointer font-semibold text-sm px-6 py-3 rounded-md mt-1 font-text text-white"
      @click="upload"
    >
      Upload File
    </button>
  </section>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { FileUpload } from 'primevue'
import { TYPE, useToast } from 'vue-toastification'

const requirements_satisfied = ref<any>([])
const requirements_not_satisfied = ref<any>([])
const fileupload = ref<any>(null)
const toast = useToast()

const upload_url = computed(() => {
  return `${import.meta.env.VITE_API_URL}/api/upload_degree_evaluation`
})

const emits = defineEmits(['on-file-has-been-parsed'])

// Upload degree eval file
const upload = () => {
  if (fileupload.value) {
    if (fileupload.value.files.length === 0) {
      toast.clear()
      toast('Please upload a file.', {
        type: TYPE.ERROR,
      })
      return
    }

    toast.clear()
    toast('Uploading file...', {
      timeout: false,
      type: TYPE.INFO,
    })

    fileupload.value.upload()
  }
}

function onUpload(event: any) {
  try {
    const response = JSON.parse(event.xhr.response)
    toast.clear()
    emits('on-file-has-been-parsed', response)
  } catch (err) {
    console.log('ERROR')
    console.log(err)
    toast('An unexpected error occured. Please try again later', {
      type: TYPE.ERROR,
    })
  }
}

function handleUploadError(evt: any) {
  toast.clear()
  toast('An unexpected error occured. Please try again later', {
    type: TYPE.ERROR,
  })
}
</script>
