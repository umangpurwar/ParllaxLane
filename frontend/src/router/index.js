import { createRouter, createWebHistory } from "vue-router"

import HomeView from "../views/HomeView.vue"
import LoginView from "../views/LoginView.vue"
import RegisterView from "../views/RegisterView.vue"
import ExamDashboard from "../views/ExamDashboard.vue"
import ExamPage from "../views/ExamPage.vue"
import AdminDashboard from "../views/AdminDashboard.vue"
import UnauthorizedView from "../views/UnauthorizedView.vue"

const routes = [
  { path: "/", component: HomeView },
  { path: "/login", name: "Login", component: LoginView },
  { path: "/register", component: RegisterView },
  { path: "/unauthorized", component: UnauthorizedView },

  { path: "/dashboard", component: ExamDashboard, meta: { requiresAuth: true } },
  { path: "/exam/:id", name: "Exam", component: ExamPage, meta: { requiresAuth: true } },

  { path: "/admin", component: AdminDashboard, meta: { requiresAuth: true, isAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let isBrowserNavigation = false;

window.addEventListener('popstate', () => {
  isBrowserNavigation = true;
});

router.beforeEach((to, from) => {
  const token = localStorage.getItem("access_token") || localStorage.getItem("token")
  const isAdmin = localStorage.getItem("is_admin") === "true"

  // 1. Physical Back/Forward Button Trap
  if (isBrowserNavigation && token) {
    isBrowserNavigation = false; 
    localStorage.clear(); 
    return "/unauthorized"; 
  }
  
  isBrowserNavigation = false; 

  // 2. Auth Check
  if (to.meta.requiresAuth && !token) {
    if (to.path !== '/login' && to.path !== '/') {
       return "/unauthorized";
    }
    return "/login"
  }

  // 3. Admin Check
  if (to.meta.isAdmin && !isAdmin) {
    return "/unauthorized" 
  }
  return true 
})

export default router