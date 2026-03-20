/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // One Dark theme colors
        'od-bg': '#282c34',
        'od-bg2': '#21252b',
        'od-fg': '#abb2bf',
        'od-accent': '#61afef',
        'od-green': '#98c379',
        'od-orange': '#e5c07b',
        'od-red': '#e06c75',
        'od-purple': '#c678dd',
        'od-cyan': '#56b6c2',
        'od-border': '#3e4451',
        // Light theme (clean whites + amber accent matching prompt)
        'lt-bg': '#f8fafc',
        'lt-bg2': '#f1f5f9',
        'lt-fg': '#1e293b',
        'lt-border': '#e2e8f0',
        'lt-accent': '#f59e0b',
        'lt-sidebar': '#0f172a',
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
