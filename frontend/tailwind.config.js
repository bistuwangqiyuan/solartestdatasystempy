/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0E7FFF',
          dark: '#1B2951',
          light: '#3D9AFF',
        },
        accent: '#FF6B35',
        background: {
          DEFAULT: '#0F1419',
          secondary: '#1A1F27',
          tertiary: '#252B36',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#9CA3AF',
          tertiary: '#6B7280',
        },
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { 'box-shadow': '0 0 5px rgb(14, 127, 255, 0.5)' },
          '100%': { 'box-shadow': '0 0 20px rgb(14, 127, 255, 0.8), 0 0 35px rgb(14, 127, 255, 0.5)' },
        },
      },
    },
  },
  plugins: [],
}