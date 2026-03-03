<template>
  <div class="space-y-16">
    <!-- Bio -->
    <section class="flex items-start gap-5">
      <div class="w-16 h-16 rounded-full shrink-0 bg-gray-100 dark:bg-gray-800 flex items-center justify-center overflow-hidden">
        <img
          :src="avatarSrc"
          alt="Avatar"
          class="w-full h-full object-cover"
          @error="onAvatarError"
        />
      </div>
      <div>
        <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100 tracking-tight">
          PG GUAN
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
          Software Engineer · AI Engineer · Architecture
        </p>
        <p class="mt-3 text-sm text-gray-600 dark:text-gray-400 leading-relaxed max-w-prose">
          白天搭架构、写代码，晚上调模型、刷论文；志在用 AI 重塑世界，现实是先用 Bug 磨砺意志。
          这里是我沉淀技术感悟与踩坑经验的小站，欢迎一同探索软件与 AI 的边界——
          如有商业合作意向，欢迎随时联系。
        </p>
        <!-- Social links -->
        <div class="mt-4 flex items-center gap-4">
          <a
            v-for="link in socialLinks"
            :key="link.label"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs text-gray-400 dark:text-gray-600 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          >
            {{ link.label }}
          </a>
        </div>
      </div>
    </section>

    <!-- Projects -->
    <section>
      <h2 class="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-600 mb-4">
        Projects
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <a
          v-for="project in projects"
          :key="project.name"
          :href="project.url"
          target="_blank"
          rel="noopener noreferrer"
          class="group block border border-gray-100 dark:border-gray-900 rounded-lg p-4 hover:border-gray-300 dark:hover:border-gray-700 transition-colors"
        >
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors">
            {{ project.name }}
          </div>
          <div class="mt-1 text-xs text-gray-500 dark:text-gray-500 leading-relaxed">
            {{ project.description }}
          </div>
        </a>
      </div>
    </section>

    <!-- Timeline -->
    <section>
      <h2 class="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-600 mb-6">
        Timeline
      </h2>
      <div class="relative pl-4 space-y-0">
        <!-- vertical line -->
        <div class="absolute left-0 top-2 bottom-2 w-px bg-gray-100 dark:bg-gray-900" />
        <div v-for="(event, i) in timeline" :key="i" class="relative flex gap-5 pb-6 last:pb-0">
          <!-- dot -->
          <div class="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full border-2 border-blue-500 dark:border-blue-400 bg-white dark:bg-[#0a0a0a]" />
          <div class="pl-4">
            <span class="text-xs tabular-nums text-gray-400 dark:text-gray-600">{{ event.year }}</span>
            <p class="mt-0.5 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{{ event.description }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const avatarSrc = '/avatar.svg'

function onAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = '/avatar.svg'
}

const socialLinks = [
  { label: 'GitHub', url: 'https://github.com/G1011' },
  { label: 'Email',  url: 'mailto:466799665@qq.com' },
]

const projects = [
  {
    name: 'Project Alpha',
    description: 'An open-source tool for doing amazing things.',
    url: 'https://github.com/G1011',
  },
  {
    name: 'Project Beta',
    description: 'A framework for building scalable systems.',
    url: 'https://github.com/G1011',
  },
]

const timeline = [
  { year: '2020 — 至今', description: '加入华为，深耕软件工程与 AI 基础设施建设。' },
]
</script>
