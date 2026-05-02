<template>
  <div class="relative w-full h-screen overflow-hidden bg-brutal-dark font-sans">
    <div class="fixed inset-0 z-0 bg-brutal-maroon overflow-hidden">
        <div class="absolute top-[-10%] left-[0%] w-[80%] h-[80%] bg-brutal-glow1 rounded-full mix-blend-screen filter blur-[140px] opacity-70 animate-pulse"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[70%] h-[70%] bg-brutal-glow2 rounded-full mix-blend-screen filter blur-[150px] opacity-80"></div>
    </div>

    <transition name="reveal" appear>
      <div class="relative z-10 w-[92vw] max-w-[1600px] h-[90vh] mx-auto [5vh] bg-brutal-paper shadow-2xl flex flex-col overflow-hidden">
        
        <div class="absolute inset-0 pointer-events-none z-0">
            <div class="grid-line-v left-[25%]"></div>
            <div class="grid-line-v left-[50%]"></div>
            <div class="grid-line-v left-[75%] hidden lg:block"></div>
            <div class="grid-line-h top-[20%]"></div>
        </div>

        <header class="absolute top-0 left-0 w-full h-[20%] flex z-20">
          <!-- LEFT BLOCK -->
          <div class="w-[25%] h-full flex items-center justify-center font-bold tracking-super-wide text-[13px] text-black">
            PARALLAXLANE
          </div>

          <!-- CENTER BLOCK  -->
          <div class="w-[50%] h-full flex items-center px-8">
            <h1 class="text-[2rem] font-medium tracking-tighter text-brutal-ink">
              Log In
            </h1>
          </div>

          <!-- RIGHT BLOCK -->
          <div class="w-[25%] h-full flex items-center justify-end px-8">
            <router-link to="/" class="text-[9px] uppercase tracking-widest font-semibold text-gray-700 hover:text-brutal-red transition-colors pointer-events-auto">
                RETURN HOME
            </router-link>
          </div>
        </header>

        <main class="absolute top-[20%] bottom-0 left-0 w-full flex z-10">
            
            <!-- LEFT COLUMN: Branding Spacer -->
            <div class="hidden lg:block w-[25%] h-full"></div>
            
            <!-- CENTER COLUMN: Login Form -->
            <div class="w-full md:w-[60%] lg:w-[50%] h-full flex flex-col justify-center px-8 sm:px-12 lg:px-24 pointer-events-auto border-r-0 lg:border-r border-brutal-border/30">
                
                <div class="flex flex-col gap-6 w-full max-w-md mx-auto">
                    
                    <div class="relative">
                        <input 
                            v-model="email" 
                            type="text" 
                            :placeholder="isOtpFlow ? 'EMAIL ADDRESS' : 'USERNAME OR EMAIL'" 
                            class="w-full bg-transparent border-b-2 border-brutal-border py-3 text-brutal-ink font-medium tracking-widest text-[12px] placeholder-gray-500 focus:outline-none focus:border-brutal-red transition-colors"
                            :disabled="isLoading"
                        />
                    </div>
                    
                    <div class="relative" v-if="!isOtpFlow">
                        <input 
                            v-model="password" 
                            type="password" 
                            placeholder="PASSWORD" 
                            class="w-full bg-transparent border-b-2 border-brutal-border py-3 text-brutal-ink font-medium tracking-widest text-[12px] placeholder-gray-500 focus:outline-none focus:border-brutal-red transition-colors"
                            :disabled="isLoading"
                        />
                    </div>

                    <div class="relative" v-if="isOtpFlow && otpSent">
                        <input 
                            v-model="otpCode" 
                            type="text" 
                            placeholder="ENTER 6-DIGIT OTP" 
                            maxlength="6"
                            class="w-full bg-transparent border-b-2 border-brutal-border py-3 text-brutal-ink font-medium tracking-widest text-[12px] placeholder-gray-500 focus:outline-none focus:border-brutal-red transition-colors text-center"
                            :disabled="isLoading"
                        />
                    </div>

                    <div class="captcha-theme-wrapper  p-1">
                        <CaptchaBox ref="captchaRef" @verified="captchaVerified = $event" />
                    </div>

                    <p v-if="errorMessage" class="text-[10px] uppercase tracking-widest font-bold text-brutal-red leading-tight">
                        {{ errorMessage }}
                    </p>

                    <button 
                        @click="handleMainAction" 
                        :disabled="!captchaVerified || isLoading"
                        class="mt-2 w-full py-4 text-[10px] uppercase tracking-super-wide font-bold transition-all duration-300"
                        :class="(captchaVerified && !isLoading) ? 'bg-brutal-ink hover:bg-brutal-red text-brutal-paper cursor-pointer' : 'bg-gray-300 text-gray-500 cursor-not-allowed'"
                    >
                        {{ primaryButtonText }}
                    </button>
                </div>
            </div>

            <!-- RIGHT COLUMN: Secondary Actions -->
            <div class="w-full md:w-[40%] lg:w-[25%] h-full flex flex-col justify-center px-8 sm:px-12 pointer-events-auto">
                <div class="flex flex-col gap-5 w-full max-w-xs mx-auto">
                    
                    <button 
                     @click="triggerGoogleLogin" 
                    type="button" 
                    class="flex items-center justify-center gap-3 w-full py-4 px-4 text-[10px] uppercase tracking-super-wide font-bold border border-brutal-ink bg-transparent hover:bg-brutal-ink hover:text-brutal-paper transition-all duration-300 text-brutal-ink"
                    :disabled="isLoading"
                      >
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21.35 11.1h-9.18v2.98h5.26c-.23 1.25-1.4 3.67-5.26 3.67-3.17 0-5.75-2.62-5.75-5.85s2.58-5.85 5.75-5.85c1.8 0 3 .77 3.69 1.43l2.52-2.44C17.06 3.36 14.9 2.5 12.17 2.5 6.98 2.5 2.77 6.77 2.77 12s4.21 9.5 9.4 9.5c5.43 0 9.02-3.82 9.02-9.2 0-.62-.07-1.08-.16-1.5z"/>
                    </svg>
                      Continue with Google
                      </button>
                    <button 
                        @click="toggleOtpFlow" 
                        type="button"
                        class="flex items-center justify-center w-full py-4 px-4 border border-[#ccc] bg-[#f4f1ea] hover:bg-[#e8e4d9] transition-colors text-[10px] font-bold tracking-widest uppercase text-brutal-ink"
                        :disabled="isLoading"
                    >
                        {{ isOtpFlow ? 'Use Password Login' : 'Login with OTP' }}
                    </button>
                    
                    <div class="h-[1px] w-full bg-brutal-border/40 my-3"></div>
                    
                    <button 
                        @click="$router.push('/register')" 
                        type="button"
                        class="text-[10px] uppercase tracking-widest font-semibold text-gray-600 hover:text-brutal-red transition-colors text-center"
                    >
                        New user? Register here
                    </button>

                </div>
            </div>

        </main>

        <div class="absolute bottom-6 right-8 z-30 pointer-events-none text-[9px] uppercase tracking-super-wide font-bold text-gray-500">
            &copy; UMNG & KUSIK
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import api from "../services/api"
import CaptchaBox from "../components/CaptchaBox.vue"

const router = useRouter()

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

// Form State
const email = ref("")
const password = ref("")
const errorMessage = ref("")
const isLoading = ref(false)

// OTP State
const isOtpFlow = ref(false)
const otpSent = ref(false)
const otpCode = ref("")

// Captcha
const captchaVerified = ref(false)
const captchaRef = ref(null)

onMounted(() => {
  captchaRef.value?.generateCaptcha?.()
})

// ----------------------
// MAIN FLOW
// ----------------------

const primaryButtonText = computed(() => {
  if (isLoading.value) return "Processing..."
  if (!captchaVerified.value) return "Verification Required"
  if (!isOtpFlow.value) return "Access Dashboard"
  if (isOtpFlow.value && !otpSent.value) return "Send OTP"
  return "Verify OTP"
})

const toggleOtpFlow = () => {
  isOtpFlow.value = !isOtpFlow.value
  otpSent.value = false
  otpCode.value = ""
  errorMessage.value = ""
}

const validateForm = () => {
  errorMessage.value = ""

  if (!email.value) {
    errorMessage.value = isOtpFlow.value ? "Email is required." : "Username or email is required."
    return false
  }

  if (!isOtpFlow.value && !password.value) {
    errorMessage.value = "Password is required."
    return false
  }

  if (isOtpFlow.value && otpSent.value && !otpCode.value) {
    errorMessage.value = "OTP code is required."
    return false
  }

  if (!captchaVerified.value) {
    errorMessage.value = "Please complete the security directive."
    return false
  }

  return true
}

// ----------------------
// AUTH
// ----------------------

const handleAuthSuccess = (data) => {
  localStorage.setItem("access_token", data.access)
  localStorage.setItem("org_role", data.org_role)
  localStorage.setItem("org_slug", data.org_slug)

  if (data.org_role === "owner" || data.org_role === "admin") {
    router.push("/admin")
  } else {
    router.push("/dashboard")
  }
}

const login = async () => {
  isLoading.value = true
  try {
    const res = await api.post("login/", {
      email: email.value,
      password: password.value
    })
    handleAuthSuccess(res.data)
  } catch (e) {
    if (e.response && e.response.data) {
      const msg = e.response.data.detail || e.response.data.error || ""
      if (msg.toLowerCase().includes("no active account") ||
          msg.toLowerCase().includes("not found")) {
        errorMessage.value = "Account not found. Please register first."
      } else {
        errorMessage.value = "Invalid email or password."
      }
    } else {
      errorMessage.value = "Login failed. Try again."
    }
  } finally {
    isLoading.value = false
  }
}

// ----------------------
// OTP
// ----------------------

const sendOtp = async () => {
  isLoading.value = true
  errorMessage.value = ""

  try {
    await api.post("accounts/send-otp/", { email: email.value })
    otpSent.value = true
  } catch (e) {
    if (e.response && e.response.data) {
      const msg = (e.response.data.error || "").toLowerCase()

      if (msg.includes("not registered")) {
        errorMessage.value = "Account not found. Please register first."
      } 
      else if (msg.includes("required")) {
        errorMessage.value = "Please enter your email."
      } 
      else {
        errorMessage.value = "Could not send OTP. Try again."
      }
    } else if (e.request) {
      // request made but no response
      errorMessage.value = "Network error. Check your connection."
    } else {
      // something else
      errorMessage.value = "Something went wrong. Try again."
    }
  } finally {
    isLoading.value = false
  }
}

const verifyOtp = async () => {
  isLoading.value = true
  try {
    const res = await api.post("accounts/verify-otp/", {
      email: email.value,
      otp: otpCode.value
    })
    handleAuthSuccess(res.data)
  } catch (e) {
    if (e.response && e.response.data) {
      errorMessage.value = e.response.data.error || "Invalid OTP"
    } else {
      errorMessage.value = "OTP verification failed"
    }
  } finally {
    isLoading.value = false
  }
}

const handleMainAction = () => {
  if (!validateForm()) return

  if (!isOtpFlow.value) login()
  else if (!otpSent.value) sendOtp()
  else verifyOtp()
}

// ----------------------
// GOOGLE LOGIN
// ----------------------

const triggerGoogleLogin = () => {
  window.location.href =
    "https://accounts.google.com/o/oauth2/v2/auth?" +
    new URLSearchParams({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      redirect_uri: window.location.origin + "/auth/google",
      response_type: "id_token",
      scope: "openid email profile",
      nonce: "random_nonce_123456"
    })
}
</script>

<style scoped>
/* Override CaptchaBox internal white backgrounds to match off-white theme */
.captcha-theme-wrapper :deep(.bg-white) {
    background-color: transparent !important;
}
.captcha-theme-wrapper :deep(input) {
    background-color: rgba(255, 255, 255, 0.4) !important;
    border-color: #ccc !important;
}
</style>