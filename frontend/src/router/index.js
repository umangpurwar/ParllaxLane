import { createRouter, createWebHistory } from "vue-router"

import HomeView from "../views/HomeView.vue"
import LoginView from "../views/LoginView.vue"
import RegisterView from "../views/RegisterView.vue"
import ExamDashboard from "../views/ExamDashboard.vue"
import ExamPage from "../views/ExamPage.vue"
import AdminDashboard from "../views/AdminDashboard.vue"
import UnauthorizedView from "../views/UnauthorizedView.vue"

import OrgCreateView from "../views/OrgCreateView.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/login", name: "Login", component: LoginView },
  { path: "/register", component: RegisterView },
  { path: "/unauthorized", component: UnauthorizedView },

  { path: "/create-org", component: OrgCreateView },

  { path: "/dashboard", component: ExamDashboard, meta: { requiresAuth: true } },
  { path: "/exam/:id", name: "Exam", component: ExamPage, meta: { requiresAuth: true } },

  { path: "/admin", component: AdminDashboard, meta: { requiresAuth: true, isAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let isBrowserNavigation = false

window.addEventListener('popstate', () => {
  isBrowserNavigation = true
})

/* ✅ Helper: clear ONLY exam-related data */
const clearExamState = () => {
  localStorage.removeItem("attempt_id")
  localStorage.removeItem("active_exam_id")

  // remove all exam_state_* keys
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith("exam_state_")) {
      localStorage.removeItem(key)
    }
  })
}

router.beforeEach((to, from) => {
  const token = localStorage.getItem("access_token") || localStorage.getItem("token")
  const orgSlug = localStorage.getItem("org_slug")
  const orgRole = localStorage.getItem("org_role")

  const isAdmin = orgRole === "owner" || orgRole === "admin"

  /* ✅ FIXED: Smart Back Button Handling */
  if (isBrowserNavigation && token) {
    isBrowserNavigation = false

    // ONLY trigger if user is coming FROM exam page
    if (from.path.startsWith("/exam")) {
      clearExamState()

      // redirect safely
      return "/dashboard"
    }
  }

  isBrowserNavigation = false

  // Auth Check
  if (to.meta.requiresAuth && !token) {
    if (to.path !== '/login' && to.path !== '/') {
      return "/unauthorized"
    }
    return "/login"
  }

  // Org onboarding check
  if (token && !orgSlug) {
    if (to.path !== "/create-org") {
      return "/create-org"
    }
  }

  // Prevent going back to create-org
  if (token && orgSlug && to.path === "/create-org") {
    return "/dashboard"
  }

  // Admin check
  if (to.meta.isAdmin && !isAdmin) {
    return "/unauthorized"
  }

  return true
})

export default router