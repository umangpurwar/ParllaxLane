import { createRouter, createWebHistory } from "vue-router"

import HomeView from "../views/HomeView.vue"
import LoginView from "../views/LoginView.vue"
import RegisterView from "../views/RegisterView.vue"
import ExamDashboard from "../views/ExamDashboard.vue"
import ExamPage from "../views/ExamPage.vue"
import AdminDashboard from "../views/AdminDashboard.vue" //  ADD

const routes = [
  { path: "/", component: HomeView },
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },

  { path: "/dashboard", component: ExamDashboard, meta: { requiresAuth: true } },
  { path: "/exam/:id", component: ExamPage, meta: { requiresAuth: true } },

  { path: "/admin", component: AdminDashboard, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ROUTE GUARD
router.beforeEach((to) => {
  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token")
  const isAdmin = localStorage.getItem("is_admin") === "true"

  if (to.meta.requiresAuth && !token) {
    return "/login"
  }

  if (to.path === "/admin" && !isAdmin) {
    return "/dashboard"
  }

  return true
})

export default router
