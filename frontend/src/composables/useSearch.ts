import { ref, watch } from 'vue'

export function useSearch(onSearch: (query: string) => void, delay = 400) {
  const query = ref('')
  let timer: ReturnType<typeof setTimeout> | null = null

  watch(query, (val) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => onSearch(val), delay)
  })

  function clear() {
    query.value = ''
  }

  return { query, clear }
}
