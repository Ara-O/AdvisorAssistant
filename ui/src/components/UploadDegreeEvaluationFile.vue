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
      To convert your degree evaluation to a .mhtml/.mht format, go to the degree evaluation page,
      and click CTRL S. Make sure to save the webpage as one file (in .mhtml format).
      <span class="font-semibold">
        Your degree evaluation file is not saved anywhere (except in the process of extracting your
        courses, after which it is permanently deleted)</span
      >
    </p>

    <p class="text-blue-700 cursor-pointer underline" @click="help_popup_is_visible = true">
      Need help generating the .mhtml file?
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

  <Dialog
    v-model:visible="help_popup_is_visible"
    modal
    :dismissable-mask="true"
    header="MHTML Guide"
    :style="{ width: '25rem', 'font-family': 'Raleway' }"
  >
    <p class="font-medium underline">If you are using Chrome:</p>
    <p class="font-medium my-2 leading-7">
      Step 1: Install the Chrome extension '
      <a
        class="text-blue-800 underline"
        target="_blank"
        href="https://chromewebstore.google.com/detail/save-as-mhtml/ahgakckdonjmnpnegjcamhagackmjpei?hl=en&pli=1"
        >Save as mHTML</a
      >'
    </p>

    <p class="my-2 font-medium leading-7">
      Step 2: On Chrome, open your portal -
      <a href="https://my.udmercy.edu" target="_blank" class="underline text-blue-800"
        >https://my.udmercy.edu</a
      >
    </p>

    <p class="my-2 font-medium leading-7">
      Step 3: Open your degree evaluation page, and click the extension. This will download a .mht
      file
    </p>
    <p class="my-2 font-medium">Step 4: Upload that file here</p>
    <hr class="mt-5 mb-5" />
    <p class="my-2 font-medium">
      Alternatively, or if you are not on Chrome. On your degree evaluation page, click Ctrl S
    </p>
    <p class="my-2 font-medium">
      This should give you open a menu asking what name to save the file. On the type of the file,
      select "single file." This should save the page as a .mhtml or .mht file.
    </p>
    <p class="mt-4 mb-4">
      <a
        target="_blank"
        class="underline"
        href="https://www.pcworld.com/article/436648/how-to-save-a-webpage-as-a-pdf-or-mht-file.html"
        >Additional tutorial</a
      >
    </p>
  </Dialog>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { FileUpload } from 'primevue'
import { TYPE, useToast } from 'vue-toastification'
import { Dialog } from 'primevue'

const help_popup_is_visible = ref<boolean>(false)
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
