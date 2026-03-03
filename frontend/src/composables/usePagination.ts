import { ref, computed } from 'vue'

export function usePagination(defaultSize = 10) {
  const currentPage = ref(1)
  const pageSize = ref(defaultSize)
  const total = ref(0)
  const totalPages = ref(1)

  function setFromResponse(data: { total: number; page: number; size: number; pages: number }) {
    total.value = data.total
    currentPage.value = data.page
    pageSize.value = data.size
    totalPages.value = data.pages
  }

  function goToPage(page: number) {
    currentPage.value = Math.max(1, Math.min(page, totalPages.value))
  }

  return { currentPage, pageSize, total, totalPages, setFromResponse, goToPage }
}
