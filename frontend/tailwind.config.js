/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        // Body / UI. Load Inter (variable) with opsz + tnum support for best results.
        sans: ['Inter var', 'Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        // Headlines and hero numbers. Load "Instrument Serif" from Google Fonts.
        display: ['Instrument Serif', 'Iowan Old Style', 'Palatino Linotype', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },

      fontSize: {
        // [size, { lineHeight, letterSpacing }]: tighter tracking as type grows
        xs: ['0.75rem', { lineHeight: '1.1rem', letterSpacing: '0.005em' }],
        sm: ['0.8125rem', { lineHeight: '1.25rem', letterSpacing: '0' }],
        base: ['0.9375rem', { lineHeight: '1.5rem', letterSpacing: '-0.006em' }],
        lg: ['1.0625rem', { lineHeight: '1.6rem', letterSpacing: '-0.011em' }],
        xl: ['1.25rem', { lineHeight: '1.75rem', letterSpacing: '-0.016em' }],
        '2xl': ['1.5rem', { lineHeight: '1.95rem', letterSpacing: '-0.021em' }],
        '3xl': ['1.875rem', { lineHeight: '2.2rem', letterSpacing: '-0.026em' }],
        '4xl': ['2.375rem', { lineHeight: '2.6rem', letterSpacing: '-0.03em' }],
        '5xl': ['3.25rem', { lineHeight: '3.4rem', letterSpacing: '-0.035em' }],
      },

      colors: {
        // Deep ink-navy, slightly cooler and darker than before for real depth
        navy: {
          950: '#050A14',
          900: '#0A1220',
          800: '#101B2E',
          700: '#17273F',
          600: '#213653',
          500: '#324B6E',
          400: '#5A7396',
          300: '#8CA0BC',
          200: '#BCC8DA',
          100: '#E1E7F0',
        },
        // The single accent: a muted champagne brass. Use sparingly (focus, key numbers, one CTA).
        brass: {
          700: '#7A6234',
          600: '#957A41',
          500: '#B0904F',
          400: '#C8A965',
          300: '#DCC48D',
          200: '#EBDDB8',
          100: '#F6EFDC',
        },
        line: '#E4E9F0',
        'line-soft': '#EEF1F6',
        canvas: '#F6F8FB',
        paper: '#FFFFFF',
        // Text tones on light surfaces
        ink: {
          DEFAULT: '#0B1424',
          muted: '#4A5871',
          subtle: '#7A8799',
        },
        // Quiet, desaturated status colors (no neon)
        positive: '#2F7D62',
        caution: '#A8742A',
        negative: '#B04A4A',
      },

      borderRadius: {
        // A real scale: small controls tighter, surfaces larger
        control: '10px',
        card: '16px',
        panel: '22px',
      },

      boxShadow: {
        // Layered shadows: a hairline, a tight contact shadow, and a wide soft ambient one
        card:
          '0 0 0 1px rgba(11, 20, 36, 0.04), 0 1px 2px rgba(11, 20, 36, 0.04), 0 8px 24px -8px rgba(11, 20, 36, 0.08)',
        lift:
          '0 0 0 1px rgba(11, 20, 36, 0.05), 0 2px 4px rgba(11, 20, 36, 0.05), 0 16px 40px -12px rgba(11, 20, 36, 0.16)',
        pop:
          '0 0 0 1px rgba(11, 20, 36, 0.06), 0 4px 8px rgba(9, 18, 32, 0.06), 0 24px 64px -16px rgba(9, 18, 32, 0.28)',
        // Bright top edge for elements on dark navy surfaces
        'inset-top': 'inset 0 1px 0 rgba(255, 255, 255, 0.07)',
        'inset-edge': 'inset 0 0 0 1px rgba(255, 255, 255, 0.06)',
        // Focus ring in brass
        focus: '0 0 0 2px #FFFFFF, 0 0 0 4px rgba(176, 144, 79, 0.65)',
      },

      backgroundImage: {
        // Dark surface with a faint top-left light source
        'navy-sheen':
          'radial-gradient(120% 80% at 0% 0%, rgba(90, 115, 150, 0.22) 0%, rgba(10, 18, 32, 0) 55%), linear-gradient(180deg, #0B1424 0%, #070D18 100%)',
        // Thin brass hairline for dividers and key edges
        'brass-line': 'linear-gradient(90deg, rgba(200,169,101,0) 0%, rgba(200,169,101,0.7) 50%, rgba(200,169,101,0) 100%)',
        // Subtle grain-free paper lift for light cards
        'paper-lift': 'linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%)',
      },

      transitionTimingFunction: {
        // Smooth, decisive deceleration; avoids the stock "ease" feel
        premium: 'cubic-bezier(0.22, 1, 0.36, 1)',
        'premium-in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
      },
      transitionDuration: {
        250: '250ms',
        400: '400ms',
      },

      keyframes: {
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(6px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in': {
          from: { opacity: '0', transform: 'translateX(20px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.97)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        'sheen-sweep': {
          from: { backgroundPosition: '-200% 0' },
          to: { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fade-in 400ms cubic-bezier(0.22, 1, 0.36, 1) both',
        'slide-in': 'slide-in 400ms cubic-bezier(0.22, 1, 0.36, 1) both',
        'scale-in': 'scale-in 250ms cubic-bezier(0.22, 1, 0.36, 1) both',
        // For skeleton loaders: a slow, restrained shimmer
        sheen: 'sheen-sweep 2.4s cubic-bezier(0.65, 0, 0.35, 1) infinite',
      },
    },
  },
  plugins: [],
};
