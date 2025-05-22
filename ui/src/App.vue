<template>
  <Analytics />
  <RouterView />
  <FeedbackDialog />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Analytics } from '@vercel/analytics/vue'
import FeedbackDialog from './components/FeedbackDialog.vue'
</script>
