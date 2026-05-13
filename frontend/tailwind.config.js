/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // TruthLens brand palette
        primary:  { DEFAULT: '#6366f1', dark: '#4f46e5', light: '#818cf8' },
        accent:   { DEFAULT: '#22d3ee', dark: '#0ea5e9', light: '#67e8f9' },
        danger:   { DEFAULT: '#ef4444', dark: '#dc2626', light: '#f87171' },
        success:  { DEFAULT: '#22c55e', dark: '#16a34a', light: '#4ade80' },
        warning:  { DEFAULT: '#f59e0b', dark: '#d97706', light: '#fbbf24' },
        glass:    { DEFAULT: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.1)' },
        dark: {
          900: '#0a0a0f',
          800: '#0f0f1a',
          700: '#13131f',
          600: '#1a1a2e',
          500: '#1e1e3a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'neon-gradient':  'linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)',
        'danger-gradient':'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)',
        'success-gradient':'linear-gradient(135deg, #22c55e 0%, #15803d 100%)',
        'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        'glow-radial':    'radial-gradient(circle at 50% 50%, rgba(99,102,241,0.15) 0%, transparent 70%)',
      },
      boxShadow: {
        'neon-blue':   '0 0 20px rgba(99,102,241,0.4), 0 0 40px rgba(99,102,241,0.1)',
        'neon-red':    '0 0 20px rgba(239,68,68,0.4),  0 0 40px rgba(239,68,68,0.1)',
        'neon-green':  '0 0 20px rgba(34,197,94,0.4),  0 0 40px rgba(34,197,94,0.1)',
        'neon-cyan':   '0 0 20px rgba(34,211,238,0.4), 0 0 40px rgba(34,211,238,0.1)',
        'glass':       '0 4px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)',
      },
      animation: {
        'pulse-slow':   'pulse 3s ease-in-out infinite',
        'glow':         'glow 2s ease-in-out infinite alternate',
        'float':        'float 6s ease-in-out infinite',
        'scan':         'scan 2s linear infinite',
        'fade-in':      'fadeIn 0.5s ease-out',
        'slide-up':     'slideUp 0.4s ease-out',
        'slide-in-left':'slideInLeft 0.4s ease-out',
      },
      keyframes: {
        glow: {
          '0%':   { boxShadow: '0 0 5px rgba(99,102,241,0.2)' },
          '100%': { boxShadow: '0 0 30px rgba(99,102,241,0.6), 0 0 60px rgba(99,102,241,0.2)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':      { transform: 'translateY(-10px)' },
        },
        scan: {
          '0%':   { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '0% 100%' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          from: { opacity: '0', transform: 'translateX(-20px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
}
