<template>
  <div class="space-y-16">
    <!-- Bio -->
    <section class="space-y-4">
      <!-- Avatar + Name row -->
      <div class="flex items-center gap-4">
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
            Full-Stack Software Engineer · AI Engineer · Architect
          </p>
        </div>
      </div>

      <!-- Description + Social -->
      <div>
        <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed max-w-prose">
          A full-stack software engineer and architect transitioning into AI research and application development, dedicated to building production-grade AI systems across diverse scenarios. 
          <br>
          <br>
          I hold a dual-focus degree in Computer Science & AI from UNSW(2017-2020) and currently work at Huawei Technologies(2020-present).
          <br>
          <br>
          I’m passionate about exploring the new，technologies, and ways of life. Enjoy travel and culinary experiences — Sharing stories from the journey. 
          Always open to connecting with like-minded professionals for learning and collaboration. 
        </p>

        <!-- Social links -->
        <div class="mt-5">
          <p class="text-xs text-gray-400 dark:text-gray-600 mb-3">My Social Channel</p>
          <div class="flex items-center gap-4">
            <a
              v-for="link in socialLinks"
              :key="link.label"
              :href="link.url"
              :target="link.label === 'Email' ? '_self' : '_blank'"
              rel="noopener noreferrer"
              :title="link.label"
              class="text-gray-400 dark:text-gray-600 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
            >
              <span class="sr-only">{{ link.label }}</span>
              <component :is="link.icon" class="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- Projects -->
    <section>
      <h2 class="text-xs font-semibold uppercase tracking-widest text-gray-900 dark:text-gray-100 mb-4">
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
      <!-- More button -->
      <div class="mt-4">
        <a
          href="https://github.com/G1011?tab=repositories"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-600 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
        >
          more
          <svg class="w-3 h-3" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 6h8M6 2l4 4-4 4" />
          </svg>
        </a>
      </div>
    </section>

    <!-- Timeline -->
    <section>
      <h2 class="text-xs font-semibold uppercase tracking-widest text-blue-500 dark:text-blue-400 mb-6">
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
import { defineComponent, h } from 'vue'

const avatarSrc = '/avatar.svg'

function onAvatarError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = '/avatar.svg'
}

// SVG icon components
const IconEmail = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('rect', { x: '2', y: '4', width: '20', height: '16', rx: '2' }),
    h('path', { d: 'M2 7l10 7 10-7' }),
  ]),
})

const IconGitHub = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
    h('path', { d: 'M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z' }),
  ]),
})

const IconWeChat = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
    h('path', { d: 'M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-5.972 2.975-7.928C11.151 2.626 9.941 2.188 8.691 2.188zm-2.184 4.49c.538 0 .976.435.976.97a.976.976 0 0 1-.976.973.976.976 0 0 1-.975-.973c0-.535.438-.97.975-.97zm4.39 0c.537 0 .976.435.976.97a.976.976 0 0 1-.976.973.976.976 0 0 1-.975-.973c0-.535.438-.97.975-.97zM23.548 13.14c0-3.497-3.516-6.33-7.853-6.33-4.338 0-7.854 2.833-7.854 6.33 0 3.498 3.516 6.332 7.854 6.332.914 0 1.802-.13 2.633-.361a.722.722 0 0 1 .598.082l1.584.927a.274.274 0 0 0 .14.047c.133 0 .24-.107.24-.247 0-.06-.024-.117-.04-.176l-.325-1.233a.491.491 0 0 1 .177-.553c1.528-1.13 2.506-2.819 2.506-4.818h-.66zm-10.545-1.024a.813.813 0 0 1-.814-.811c0-.449.364-.812.814-.812.449 0 .813.363.813.812a.813.813 0 0 1-.813.811zm5.382 0a.813.813 0 0 1-.813-.811c0-.449.363-.812.813-.812.449 0 .813.363.813.812a.813.813 0 0 1-.813.811z' }),
  ]),
})

const IconInstagram = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
    h('path', { d: 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z' }),
  ]),
})

const IconTikTok = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
    h('path', { d: 'M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.27 6.27 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.69a8.2 8.2 0 0 0 4.78 1.52V6.75a4.85 4.85 0 0 1-1.01-.06z' }),
  ]),
})

const socialLinks = [
  { label: 'Email',     url: 'mailto:466799665@qq.com',                  icon: IconEmail },
  { label: 'GitHub',    url: 'https://github.com/G1011',                 icon: IconGitHub },
  { label: 'WeChat',    url: '#',                                         icon: IconWeChat },
  { label: 'Instagram', url: 'https://www.instagram.com/',               icon: IconInstagram },
  { label: 'TikTok',    url: 'https://www.tiktok.com/',                  icon: IconTikTok },
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
  { year: '2020 — present', description: 'Full-stack software engineer at Huawei Technologies' },
]
</script>
