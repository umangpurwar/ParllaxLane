/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // call custom palette "brutal"
        brutal: {
          dark: '#0a0000',       // Main background
          maroon: '#4a0b00',     // Glow background
          paper: '#e3dfd5',      // Main card/UI background
          red: '#ef3f23',        // Primary accent/buttons
          border: '#b5b0a6',     // Grid lines and borders
          ink: '#222222',        // Primary text
          glow1: '#ff2a00',      // Background blob 1
          glow2: '#ff6600',      // Background blob 2
        }
      },
      fontFamily: {
        // Overrides the default Tailwind sans-serif
        sans: ['Inter', 'sans-serif'],
      },
      letterSpacing: {
        // Your custom tracking values
        'super-wide': '0.2em',
        'wide-ish': '0.15em',
      },
      // for adding custom reveal animations here
      animation: {
        'reveal': 'reveal 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards',
      },
      keyframes: {
        reveal: {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        }
      }
    },
  },
  plugins: [],
}