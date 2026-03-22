<template>
  <div class="relative w-full h-screen overflow-hidden bg-brutal-dark font-sans">
    <div class="fixed inset-0 z-0 bg-brutal-maroon overflow-hidden">
        <div class="absolute top-[-10%] left-[0%] w-[80%] h-[80%] bg-brutal-glow1 rounded-full mix-blend-screen filter blur-[140px] opacity-70 animate-pulse"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[70%] h-[70%] bg-brutal-glow2 rounded-full mix-blend-screen filter blur-[150px] opacity-80"></div>
    </div>

    <transition name="reveal" appear>
      <div class="relative z-10 w-[92vw] max-w-[1600px] h-[90vh] mx-auto mt-[5vh] bg-brutal-paper shadow-2xl flex flex-col overflow-hidden">
        
        <div class="absolute inset-0 pointer-events-none z-0">
            <div class="grid-line-v left-[25%]"></div>
            <div class="grid-line-v left-[50%]"></div>
            <div class="grid-line-v left-[75%] hidden lg:block"></div>
            <div class="grid-line-h top-[20%]"></div>
        </div>

        <header class="absolute top-0 left-0 w-full h-[20%] flex z-20">
            <div class="w-[25%] h-full flex items-center justify-center font-bold tracking-super-wide text-[13px] text-black">PARALLAXLANE</div>
            <div class="w-[75%] h-full flex items-center px-8 justify-end">
                <router-link to="/" class="text-[9px] uppercase tracking-widest font-semibold text-gray-700 hover:text-brutal-red transition-colors pointer-events-auto">
                    RETURN HOME
                </router-link>
            </div>
        </header>

        <main class="absolute top-[20%] bottom-0 left-0 w-full flex z-10">
            <div class="hidden md:block w-[25%] h-full"></div>
            
            <div class="w-full md:w-[50%] lg:w-[25%] h-full flex flex-col justify-center px-12 md:px-16 lg:px-12 pointer-events-auto">
                <h1 class="text-[3rem] font-medium tracking-tighter leading-none text-brutal-ink mb-12">
                    Log In
                </h1>
                
                <div class="flex flex-col gap-8">
                    <div class="relative">
                        <input 
                            v-model="username" 
                            type="text" 
                            placeholder="USERNAME" 
                            class="w-full bg-transparent border-b-2 border-brutal-border py-3 text-brutal-ink font-medium tracking-widest text-[10px] uppercase placeholder-gray-500 focus:outline-none focus:border-brutal-red transition-colors"
                        />
                    </div>
                    
                    <div class="relative">
                        <input 
                            v-model="password" 
                            type="password" 
                            placeholder="PASSWORD" 
                            class="w-full bg-transparent border-b-2 border-brutal-border py-3 text-brutal-ink font-medium tracking-widest text-[10px] uppercase placeholder-gray-500 focus:outline-none focus:border-brutal-red transition-colors"
                        />
                    </div>

                    <button 
                        @click="login" 
                        class="mt-6 w-full bg-brutal-ink hover:bg-brutal-red text-brutal-paper py-4 text-[10px] uppercase tracking-super-wide font-bold transition-all duration-300"
                    >
                        Access Dashboard
                    </button>

                    <button 
                        @click="$router.push('/register')" 
                        class="mt-2 text-[9px] uppercase tracking-widest font-semibold text-gray-600 hover:text-brutal-red transition-colors text-left"
                    >
                        New user? Register here
                    </button>
                </div>
            </div>
        </main>

        <div class="absolute bottom-6 right-8 z-30 pointer-events-none text-[9px] uppercase tracking-super-wide font-bold text-gray-500">
            &copy; UMNG
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import api from "../services/api"

const router = useRouter()
const username = ref("")
const password = ref("")

const login = async () => {
  try {
    const response = await api.post("login/", {
      username: username.value,
      password: password.value
    })

    localStorage.setItem("access_token", response.data.access)
    if (response.data.refresh) {
      localStorage.setItem("refresh_token", response.data.refresh)
    }
    
    localStorage.setItem("username", username.value)
    localStorage.setItem("is_admin", String(response.data.is_admin))
    localStorage.removeItem("token")
    
    if (response.data.is_admin) {
      router.push("/admin")
    } else {
      router.push("/dashboard")
    }
  } catch (error) {
    alert("Login failed. Please check your credentials.")
    console.error(error)
  }
}
</script>