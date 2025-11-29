/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Account priority colors
        'priority-very-high': '#10B981',
        'priority-high': '#3B82F6',
        'priority-medium': '#F59E0B',
        'priority-low': '#6B7280',
        // MEDDIC role tier colors
        'tier-entry-point': '#8B5CF6',
        'tier-middle-decider': '#F97316',
        'tier-economic-buyer': '#06B6D4',
        // Infrastructure category colors
        'infra-gpu': '#EF4444',
        'infra-vendor': '#EC4899',
        'infra-power': '#F59E0B',
        'infra-cooling': '#3B82F6',
        'infra-dcim': '#10B981',
      },
    },
  },
  plugins: [],
}
