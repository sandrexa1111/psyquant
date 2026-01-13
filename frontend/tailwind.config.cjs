/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#3b82f6', // Example blue
                secondary: '#64748b', // Slate
                success: '#10b981', // Emerald
                warning: '#f59e0b', // Amber
                danger: '#ef4444', // Red
                dark: {
                    bg: '#0f172a',
                    surface: '#1e293b',
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
