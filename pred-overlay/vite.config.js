import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
    plugins: [react()],
    build: {
        outDir: 'dist',
        rollupOptions: {
            input: 'src/content-script.tsx',
            output: {
                entryFileNames: 'content-script.js',
                format: 'iife', // Chrome requires IIFE for content scripts
                name: 'ContentScript'
            }
        }
    }
});
