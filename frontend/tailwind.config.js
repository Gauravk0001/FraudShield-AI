/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#2563EB',
          600: '#1D4ED8',
          700: '#1E40AF',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          secondary: '#F1F5F9',
          bg: '#F8FAFC',
          border: '#E2E8F0',
          dark: '#0F172A',
          darkSecondary: '#1E293B',
          darkBg: '#0B0F17',
          darkBorder: '#334155',
        },
        slateText: {
          primary: '#0F172A',
          secondary: '#475569',
          muted: '#94A3B8',
          darkPrimary: '#F8FAFC',
          darkSecondary: '#94A3B8',
          darkMuted: '#64748B',
        },
        risk: {
          critical: '#991B1B',
          criticalBg: '#FEE2E2',
          high: '#DC2626',
          highBg: '#FEF2F2',
          medium: '#D97706',
          mediumBg: '#FEF3C7',
          low: '#16A34A',
          lowBg: '#DCFCE7',
          neutral: '#64748B',
          neutralBg: '#F1F5F9',
        }
      },
      borderRadius: {
        'btn': '8px',
        'input': '8px',
        'card': '12px',
        'modal': '16px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
