<template>
  <main>
    <div
      v-if="!degree_evaluation_was_uploaded"
      class="w-full text-center h-screen flex flex-col gap-4 justify-center items-center"
    >
      <h1 class="font-title font-medium text-4xl">Upload your Student Evaluation</h1>
      <p class="font-text font-medium">Upload your student evaluation file as a .mhtml file</p>
      <p>To convert your degree evaluation to a .mhtml format, do ...</p>

      <FileUpload
        ref="fileupload"
        mode="basic"
        name="demo[]"
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
    </div>
  </main>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import FileUpload from 'primevue/fileupload'
const degree_evaluation_was_uploaded = ref<boolean>(false)

const fileupload = ref()

const upload_url = computed(() => {
  return `${import.meta.env.VITE_API_URL}/upload_degree_evaluation`
})

const upload = () => {
  fileupload.value.upload()
}

function onUpload() {
  console.log('Uploaded Successfully')
}
</script>
