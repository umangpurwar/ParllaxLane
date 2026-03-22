<template>
  <div class="relative w-full h-screen overflow-hidden bg-brutal-dark font-sans">
    <div class="fixed inset-0 z-0 bg-brutal-maroon overflow-hidden">
        <div class="absolute top-[-10%] left-[0%] w-[80%] h-[80%] bg-brutal-glow1 rounded-full mix-blend-screen filter blur-[140px] opacity-70 animate-pulse"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[70%] h-[70%] bg-brutal-glow2 rounded-full mix-blend-screen filter blur-[150px] opacity-80"></div>
    </div>

    <transition name="reveal" appear>
      <div class="relative z-10 w-[92vw] max-w-[1600px] h-[90vh] mx-auto mt-[5vh] bg-brutal-paper shadow-2xl flex flex-col overflow-hidden">
        
        <div class="absolute inset-0 pointer-events-none z-0">
            <div class="grid-line-v left-[25%] hidden md:block"></div>
            <div class="grid-line-v left-[50%]"></div>
            <div class="grid-line-v left-[75%] hidden lg:block"></div>
            <div class="grid-line-h top-[20%]"></div>
        </div>

        <header class="absolute top-0 left-0 w-full h-[20%] flex z-20">
            <div class="w-full md:w-[25%] h-full flex items-center justify-center md:justify-start md:px-8 font-bold tracking-super-wide text-[13px] text-black bg-brutal-paper md:bg-transparent">
                PARALLAXLANE
            </div>
            <div class="hidden md:flex w-[75%] h-full items-center px-8 justify-end">
                <router-link to="/" class="text-[9px] uppercase tracking-widest font-semibold text-gray-700 hover:text-brutal-red transition-colors pointer-events-auto">
                    RETURN HOME
                </router-link>
            </div>
        </header>

        <main class="absolute top-[20%] bottom-0 left-0 w-full flex flex-col md:flex-row z-10">
            
            <div class="hidden md:flex w-[50%] h-full flex-col justify-center px-12 md:px-16 lg:px-24 pointer-events-auto bg-brutal-paper/80 backdrop-blur-sm md:bg-transparent md:backdrop-blur-none">
                <p class="text-[9px] uppercase tracking-wide-ish font-bold text-brutal-red mb-6">
                    Candidate Registration
                </p>
                <h1 class="text-[3rem] lg:text-[4rem] font-medium tracking-tighter leading-none text-brutal-ink mb-8">
                    Secure.<br>Fair.<br>Unbiased.
                </h1>
                <p class="text-[1.1rem] lg:text-[1.25rem] font-medium tracking-tight leading-[1.4] text-[#333] max-w-md">
                    Welcome to ParallaxLane. We transform exams into trusted evaluations where <span class="text-brutal-red font-semibold">integrity</span> is built in. Create your profile to let your merit speak for itself.
                </p>
            </div>
            
            <div class="w-full md:w-[50%] lg:w-[25%] h-full flex flex-col justify-center px-8 md:px-12 pointer-events-auto bg-brutal-paper">
                <h2 class="text-[2rem] font-medium tracking-tighter leading-none text-brutal-ink mb-10 md:hidden">
                    Register
                </h2>
                
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
                            v-model="email" 
                            type="email" 
                            placeholder="EMAIL" 
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
                        @click="register" 
                        class="mt-6 w-full bg-brutal-ink hover:bg-brutal-red text-brutal-paper py-4 text-[10px] uppercase tracking-super-wide font-bold transition-all duration-300"
                    >
                        Create Profile
                    </button>

                    <button 
                        @click="$router.push('/login')" 
                        class="mt-2 text-[9px] uppercase tracking-widest font-semibold text-gray-600 hover:text-brutal-red transition-colors text-left"
                    >
                        Already have an account? Log In
                    </button>
                </div>
            </div>

            <div class="hidden lg:block w-[25%] h-full"></div>
            
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
const email = ref("")
const password = ref("")

const register = async () => {
  try {
    await api.post("accounts/register/", {
      username: username.value,
      email: email.value,
      password: password.value
    })

    alert("Registered successfully. Please log in.")
    router.push("/login")

  } catch (error) {
    console.error("Registration error:", error)
    alert("Registration failed. Please try again.")
  }
}
</script>