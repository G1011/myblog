import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    // Public routes
    {
      path: '/',
      component: () => import('@/layouts/PublicLayout.vue'),
      children: [
        {
          path: '',
          name: 'about',
          component: () => import('@/views/public/AboutView.vue'),
        },
        {
          path: 'blog',
          name: 'blog',
          component: () => import('@/views/public/BlogView.vue'),
        },
        {
          path: 'blog/:slug',
          name: 'article',
          component: () => import('@/views/public/ArticleDetailView.vue'),
        },
        {
          path: 'category/:slug',
          name: 'category',
          component: () => import('@/views/public/CategoryView.vue'),
        },
        {
          path: 'tag/:slug',
          name: 'tag',
          component: () => import('@/views/public/TagView.vue'),
        },
        {
          path: 'search',
          name: 'search',
          component: () => import('@/views/public/SearchView.vue'),
        },
      ],
    },
    // Admin login (standalone, no layout wrapper)
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
    },
    // Admin routes (protected)
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardView.vue'),
        },
        {
          path: 'articles',
          name: 'admin-articles',
          component: () => import('@/views/admin/ArticlesView.vue'),
        },
        {
          path: 'articles/new',
          name: 'admin-article-new',
          component: () => import('@/views/admin/ArticleEditView.vue'),
        },
        {
          path: 'articles/:id/edit',
          name: 'admin-article-edit',
          component: () => import('@/views/admin/ArticleEditView.vue'),
        },
        {
          path: 'categories',
          name: 'admin-categories',
          component: () => import('@/views/admin/CategoriesView.vue'),
        },
        {
          path: 'tags',
          name: 'admin-tags',
          component: () => import('@/views/admin/TagsView.vue'),
        },
        {
          path: 'comments',
          name: 'admin-comments',
          component: () => import('@/views/admin/CommentsView.vue'),
        },
      ],
    },
    // 404
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/public/NotFoundView.vue'),
    },
  ],
})

// Route guard
router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')

  if (to.meta.requiresAuth && !token) {
    return { path: '/admin/login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'admin-login' && token) {
    return { path: '/admin' }
  }
})

export default router
