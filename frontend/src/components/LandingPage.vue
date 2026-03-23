<template>
  <div class="relative w-full h-screen overflow-hidden bg-brutal-dark font-sans">
    <div class="fixed inset-0 z-0 bg-brutal-maroon overflow-hidden">
        <div class="absolute top-[-10%] left-[0%] w-[80%] h-[80%] bg-brutal-glow1 rounded-full mix-blend-screen filter blur-[140px] opacity-70 animate-pulse"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[70%] h-[70%] bg-brutal-glow2 rounded-full mix-blend-screen filter blur-[150px] opacity-80"></div>
    </div>

    <transition name="reveal" appear>
        <div v-if="!isLoading" class="relative z-10 w-[92vw] max-w-[1600px] h-[90vh] mx-auto mt-[5vh] bg-brutal-paper shadow-2xl flex flex-col overflow-hidden">
            <div class="absolute inset-0 pointer-events-none z-0">
                <div class="grid-line-v left-[25%]"></div>
                <div class="grid-line-v left-[50%]"></div>
                <div class="grid-line-h top-[35%]"></div>
                <div class="grid-line-h top-[65%]"></div>
            </div>

            <header class="absolute top-0 left-0 w-full h-[12%] flex z-20">
                <div class="w-[25%] h-full flex items-center justify-center font-bold tracking-super-wide text-[13px] text-black">PARALLAXLANE</div>
                <div class="w-[25%] h-full flex items-center px-8 text-[9px] uppercase tracking-widest font-semibold text-gray-700">Abilities</div>
                <div class="w-[50%] h-full flex items-center px-8 justify-between text-[9px] uppercase tracking-widest font-semibold text-gray-700">
                    <router-link to="/register" class="hover:text-black transition-colors pointer-events-auto z-50">REGISTER</router-link>
                    <router-link to="/login" class="hover:text-black transition-colors pointer-events-auto z-50">LOG IN</router-link>
                </div>
            </header>

            <main class="relative flex-1">
                <div class="absolute top-[35%] left-8 transform -translate-y-[150%] pointer-events-auto text-[9px] uppercase tracking-wide-ish font-semibold text-gray-700">
                    See results<br>that stand true.
                </div>

                <div ref="threeCanvasContainer" class="absolute top-[35%] left-0 w-[50%] h-[30%] pointer-events-auto z-10"></div>

                <div class="absolute bottom-[5%] lg:bottom-10 left-8 w-max pointer-events-auto z-20">
                    <h1 class="text-[1.8rem] md:text-[2.2rem] lg:text-[2.6rem] xl:text-[3rem] font-medium tracking-tighter leading-none text-brutal-ink whitespace-nowrap">
                        Meet ParallaxLane
                    </h1>
                </div>

                <div class="absolute top-[65%] right-8 transform -translate-y-[150%] scale-[0.4] origin-right pointer-events-auto text-[9px] uppercase tracking-wide-ish font-semibold text-gray-700">
                    Scroll Down
                </div>

                <div class="absolute top-[65%] left-[50%] w-[50%] h-[35%] flex items-center px-12 pointer-events-auto">
                    <p class="text-[1.15rem] md:text-[1.25rem] lg:text-[1.4rem] font-medium tracking-tight leading-[1.3] text-[#333] max-w-lg">
                        ParallaxLane transforms exams into fair, trusted evaluations, where <span class="text-brutal-red font-semibold">integrity</span> is built in and results speak for themselves.
                    </p>
                </div>

                <div class="absolute bottom-6 right-8 pointer-events-auto text-[9px] uppercase tracking-super-wide font-bold text-gray-400">
                    &copy; UMNG
                </div>
            </main>
        </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';

const isLoading = ref(true);
const threeCanvasContainer = ref(null);

let scene, camera, renderer, animationId;

const handleResize = () => {
    if (!threeCanvasContainer.value || !camera || !renderer) return;
    camera.aspect = threeCanvasContainer.value.clientWidth / threeCanvasContainer.value.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(threeCanvasContainer.value.clientWidth, threeCanvasContainer.value.clientHeight);
};

const initThree = () => {
    if (!threeCanvasContainer.value) return;
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, threeCanvasContainer.value.clientWidth / threeCanvasContainer.value.clientHeight, 0.1, 100);
    camera.position.z = 24;
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(threeCanvasContainer.value.clientWidth, threeCanvasContainer.value.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    threeCanvasContainer.value.appendChild(renderer.domElement);

    const uniforms = { u_time: { value: 0.0 } };
    const material = new THREE.ShaderMaterial({
        wireframe: true, transparent: true, opacity: 0.7, uniforms,
        vertexShader: `varying vec3 vPos; void main() { vPos = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
        fragmentShader: `uniform float u_time; varying vec3 vPos; void main() { vec3 c1 = vec3(0.25); vec3 c2 = vec3(0.98, 0.35, 0.15); float w = sin(vPos.y * 0.15 - u_time * 2.5); gl_FragColor = vec4(mix(c1, c2, smoothstep(-0.6, 0.6, w)), 0.85); }`
    });

    const createPipe = (y) => {
        const g = new THREE.Group();
        const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 38, 16, 64, true), material);
        const p2 = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 38, 16, 64, true), material);
        const p3 = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 38, 16, 64, true), material);
        g.add(p1, p2, p3); g.rotation.z = Math.PI/2; g.position.y = y;
        scene.add(g); return [p1, p2, p3];
    };

    const tLanes = createPipe(3.5); 
    const bLanes = createPipe(-3.5);
    const animate = () => {
        animationId = requestAnimationFrame(animate);
        uniforms.u_time.value += 0.01;
        tLanes.forEach((l, i) => l.rotation.y -= 0.008 + (i*0.004));
        bLanes.forEach((l, i) => l.rotation.y += 0.008 + (i*0.004));
        renderer.render(scene, camera);
    };
    animate();
    window.addEventListener('resize', handleResize);
};

onMounted(() => {
    setTimeout(() => { 
        isLoading.value = false; 
        setTimeout(initThree, 100); 
    }, 1000);
});

onUnmounted(() => {
    if (animationId) cancelAnimationFrame(animationId);
    if (renderer) renderer.dispose();
    window.removeEventListener('resize', handleResize);
});
</script>