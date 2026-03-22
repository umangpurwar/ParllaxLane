<template>
  <div class="relative w-full h-screen overflow-hidden bg-brutal-paper font-sans">
    
    <transition name="reveal" appear>
      <div class="relative z-10 w-full h-full flex flex-col overflow-hidden">
        
        <div class="absolute inset-0 pointer-events-none z-0">
            <div class="grid-line-v left-[30%]"></div>
            <div class="grid-line-v left-[65%]"></div>
            <div class="grid-line-h top-[12%]"></div>
        </div>

        <header class="absolute top-0 left-0 w-full h-[12%] flex z-20">
            <div class="w-[30%] h-full flex items-center px-8 font-bold tracking-super-wide text-[13px] text-black">
                PARALLAXLANE
            </div>
            <div class="w-[35%] h-full flex items-center px-8 text-[9px] uppercase tracking-widest font-semibold text-gray-700">
                STUDENT DASHBOARD
            </div>
            <div class="w-[35%] h-full flex items-center px-8 justify-end">
                <button @click="logout" class="text-[9px] uppercase tracking-widest font-bold text-brutal-red hover:text-brutal-ink transition-colors pointer-events-auto">
                    LOG OUT
                </button>
            </div>
        </header>

        <main class="absolute top-[12%] bottom-0 left-0 w-full flex z-10 pointer-events-auto">
            
            <div class="w-[30%] h-full p-8 md:p-12 flex flex-col border-r border-transparent">
                <p class="text-[9px] uppercase tracking-wide-ish font-semibold text-gray-600 mb-4">
                    Candidate Profile
                </p>
                <h1 class="text-[2.5rem] lg:text-[3rem] font-medium tracking-tighter leading-none text-brutal-ink mb-12 capitalize">
                    Welcome,<br>{{ username }}
                </h1>

                <div class="mt-auto mb-8">
                    <p class="text-[9px] uppercase tracking-wide-ish font-bold text-brutal-red mb-4 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-brutal-red animate-pulse"></span>
                        Action Required
                    </p>
                    <div class="bg-brutal-ink text-brutal-paper p-8 shadow-2xl">
                        <h3 class="text-xl font-medium tracking-tight mb-2">Advanced Computer Science Final</h3>
                        <p class="text-xs text-gray-400 mb-6">Proctoring: Enabled • Duration: 120 mins</p>
                        <button class="w-full bg-brutal-red hover:bg-white hover:text-brutal-ink text-white py-3 text-[10px] uppercase tracking-super-wide font-bold transition-all duration-300">
                            Begin Exam Now
                        </button>
                    </div>
                </div>
            </div>

            <div class="w-[35%] h-full p-8 md:p-12 flex flex-col">
                <p class="text-[9px] uppercase tracking-wide-ish font-semibold text-gray-600 mb-8">
                    Upcoming Evaluations
                </p>
                
                <div class="flex flex-col gap-6">
                    <div class="group cursor-pointer">
                        <p class="text-[10px] font-bold text-gray-500 mb-1">TOMORROW • 10:00 AM</p>
                        <h4 class="text-lg font-medium tracking-tight text-brutal-ink group-hover:text-brutal-red transition-colors">Data Structures Midterm</h4>
                        <div class="h-[1px] w-full bg-brutal-border mt-4 opacity-50"></div>
                    </div>
                    
                    <div class="group cursor-pointer">
                        <p class="text-[10px] font-bold text-gray-500 mb-1">OCT 14 • 2:00 PM</p>
                        <h4 class="text-lg font-medium tracking-tight text-brutal-ink group-hover:text-brutal-red transition-colors">Software Engineering Ethics</h4>
                        <div class="h-[1px] w-full bg-brutal-border mt-4 opacity-50"></div>
                    </div>

                     <div class="group cursor-pointer">
                        <p class="text-[10px] font-bold text-gray-500 mb-1">OCT 18 • 9:00 AM</p>
                        <h4 class="text-lg font-medium tracking-tight text-brutal-ink group-hover:text-brutal-red transition-colors">Machine Learning Basics</h4>
                        <div class="h-[1px] w-full bg-brutal-border mt-4 opacity-50"></div>
                    </div>
                </div>
            </div>

            <div class="w-[35%] h-full p-8 md:p-12 flex flex-col relative">
                <p class="text-[9px] uppercase tracking-wide-ish font-semibold text-gray-600 mb-8">
                    Verified Results
                </p>

                <div class="flex flex-col gap-4">
                    <div class="flex justify-between items-end pb-4 border-b border-brutal-border border-opacity-50">
                        <div>
                            <h4 class="text-md font-medium tracking-tight text-brutal-ink">Database Systems</h4>
                            <p class="text-[9px] uppercase tracking-widest text-gray-500 mt-1">Completed Sep 22</p>
                        </div>
                        <span class="text-2xl font-medium tracking-tighter text-brutal-ink">92%</span>
                    </div>

                    <div class="flex justify-between items-end pb-4 border-b border-brutal-border border-opacity-50">
                        <div>
                            <h4 class="text-md font-medium tracking-tight text-brutal-ink">Calculus III</h4>
                            <p class="text-[9px] uppercase tracking-widest text-gray-500 mt-1">Completed Sep 10</p>
                        </div>
                        <span class="text-2xl font-medium tracking-tighter text-brutal-ink">88%</span>
                    </div>

                    <div class="flex justify-between items-end pb-4 border-b border-brutal-border border-opacity-50">
                        <div>
                            <h4 class="text-md font-medium tracking-tight text-brutal-ink">Introduction to Algorithms</h4>
                            <p class="text-[9px] uppercase tracking-widest text-gray-500 mt-1">Completed Aug 30</p>
                        </div>
                        <span class="text-2xl font-medium tracking-tighter text-brutal-ink">95%</span>
                    </div>
                </div>

                <div class="mt-auto pb-4">
                    <p class="text-[9px] uppercase tracking-wide-ish leading-[1.6] font-semibold text-gray-500">
                        All evaluations secured and verified<br>by ParallaxLane Protocol.
                    </p>
                </div>
            </div>

        </main>
        
        <div class="absolute bottom-6 right-8 pointer-events-none text-[9px] uppercase tracking-super-wide font-bold text-gray-500 z-30">
            &copy; UMNG
        </div>
        
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const username = ref("Student")

onMounted(() => {
    const storedName = localStorage.getItem("username")
    if (storedName) {
        username.value = storedName
    }
})

const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("is_admin")
    localStorage.removeItem("username")
    router.push("/login")
}
</script>