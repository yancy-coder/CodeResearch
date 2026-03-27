/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Endfield color system
        endfield: {
          bg: {
            primary: '#0a0a0f',
            secondary: '#12121a',
            card: '#1a1a25',
            hover: '#222230'
          },
          accent: {
            DEFAULT: '#ff6b35',
            hover: '#ff8555',
            dim: '#cc5529',
            glow: 'rgba(255, 107, 53, 0.3)'
          },
          border: {
            DEFAULT: '#2a2a3a',
            accent: '#ff6b35'
          },
          text: {
            primary: '#ffffff',
            secondary: '#a0a0b0',
            muted: '#606070'
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(255, 107, 53, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(255, 107, 53, 0.4)' }
        }
      }
    },
  },
  plugins: [],
}
