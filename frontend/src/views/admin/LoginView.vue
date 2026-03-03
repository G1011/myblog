<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/common/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!email.value || !password.value) {
    error.value = '请填写邮箱和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect as string || '/admin'
    router.push(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败，请检查账号密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-[#0a0a0a]">
    <!-- Top bar -->
    <div class="absolute top-4 left-4">
      <RouterLink
        to="/"
        class="text-xs text-gray-400 dark:text-gray-600 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
      >
        ← 回到首页
      </RouterLink>
    </div>
    <div class="absolute top-4 right-4">
      <ThemeToggle />
    </div>

    <div class="w-full max-w-sm px-6">
      <div class="mb-10 text-center">
        <RouterLink to="/" class="text-xl font-bold text-gray-900 dark:text-gray-100">MyBlog</RouterLink>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">管理员登录</p>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">邮箱</label>
          <input
            v-model="email"
            type="email"
            autocomplete="email"
            class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600 transition-colors"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">密码</label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-800 rounded bg-white dark:bg-[#111] focus:outline-none focus:border-gray-400 dark:focus:border-gray-600 transition-colors"
          />
        </div>

        <div v-if="error" class="text-xs text-red-500 py-1">{{ error }}</div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2.5 text-sm font-medium bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:opacity-80 disabled:opacity-50 transition-opacity"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>
