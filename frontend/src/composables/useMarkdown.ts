import { computed, type Ref } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'

// Configure marked with syntax highlighting
marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderer = new marked.Renderer()
renderer.code = function ({ text, lang }) {
  const language = hljs.getLanguage(lang || '') ? lang! : 'plaintext'
  const highlighted = hljs.highlight(text, { language }).value
  return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
}
marked.use({ renderer })

export function useMarkdown(source: Ref<string>) {
  const html = computed(() => {
    if (!source.value) return ''
    return marked.parse(source.value) as string
  })
  return { html }
}

export function renderMarkdown(source: string): string {
  if (!source) return ''
  return marked.parse(source) as string
}
