import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#030a14',
          900: '#07111f',
          800: '#0b1629',
          700: '#0d1c33',
          600: '#102240',
          500: '#133059',
        },
        electric: {
          blue:   '#53b6ff',
          cyan:   '#35e0b8',
          purple: '#7c5cff',
          red:    '#ff5b76',
          green:  '#37d39a',
          amber:  '#f8bf4c',
        },
        tcai: {
          text:   'rgba(245,248,255,.96)',
          muted:  'rgba(200,214,236,.72)',
          faint:  'rgba(200,214,236,.48)',
          border: 'rgba(130,164,220,.16)',
          'border-strong': 'rgba(130,164,220,.28)',
          panel:  'rgba(10,19,37,.82)',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'ui-sans-serif', 'system-ui', '-apple-system'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas'],
      },
      borderRadius: {
        '2xl':  '1rem',
        '3xl':  '1.5rem',
        '4xl':  '2rem',
        '5xl':  '2.5rem',
      },
      boxShadow: {
        'glow-blue':   '0 0 20px rgba(83,182,255,.35), 0 0 60px rgba(83,182,255,.12)',
        'glow-cyan':   '0 0 20px rgba(53,224,184,.35)',
        'glow-purple': '0 0 20px rgba(124,92,255,.35)',
        'panel':       '0 22px 60px rgba(0,0,0,.35)',
        'card':        '0 8px 32px rgba(0,0,0,.30)',
        'card-hover':  '0 16px 48px rgba(0,0,0,.40), 0 0 0 1px rgba(83,182,255,.15)',
        'btn-glow':    '0 4px 24px rgba(83,182,255,.40)',
        'inset-top':   'inset 0 1px 0 rgba(255,255,255,.04)',
      },
      backgroundImage: {
        'app-bg': 'radial-gradient(1000px 600px at 10% -10%, rgba(83,182,255,.18) 0%, transparent 58%), radial-gradient(900px 700px at 100% 0%, rgba(124,92,255,.16) 0%, transparent 52%), radial-gradient(900px 600px at 50% 120%, rgba(53,224,184,.10) 0%, transparent 60%), linear-gradient(180deg, #07111f, #0b1629)',
        'card-gradient': 'linear-gradient(135deg, rgba(255,255,255,.05), rgba(255,255,255,.02))',
        'btn-primary':   'linear-gradient(135deg, rgba(83,182,255,.92), rgba(124,92,255,.86))',
        'btn-primary-hover': 'linear-gradient(135deg, rgba(100,196,255,1.00), rgba(140,110,255,.95))',
        'hero-glow':     'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(83,182,255,.22), transparent)',
        'hero-glow-2':   'radial-gradient(ellipse 60% 40% at 80% 50%, rgba(124,92,255,.18), transparent)',
        'panel-gradient':'linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02))',
        'side-bg':       'linear-gradient(180deg, rgba(8,17,33,.94), rgba(10,19,37,.86))',
        'active-nav':    'linear-gradient(135deg, rgba(83,182,255,.14), rgba(124,92,255,.10))',
      },
      animation: {
        'pulse-slow':  'pulse 4s cubic-bezier(0.4,0,0.6,1) infinite',
        'glow-pulse':  'glow-pulse 3s ease-in-out infinite',
        'float':       'float 6s ease-in-out infinite',
        'scan-line':   'scan-line 4s linear infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 10px rgba(83,182,255,.2)' },
          '50%':       { boxShadow: '0 0 30px rgba(83,182,255,.6), 0 0 60px rgba(83,182,255,.2)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':       { transform: 'translateY(-12px)' },
        },
        'scan-line': {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
