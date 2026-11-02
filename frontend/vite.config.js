import {defineConfig} from 'vite';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({plugins:[tailwindcss()],base:'/static/workspace/',build:{outDir:'../src/atlas/static/workspace',emptyOutDir:true},server:{proxy:{'/fixtures':'http://127.0.0.1:8030','/visualization':'http://127.0.0.1:8030','/networks':'http://127.0.0.1:8030','/generate':'http://127.0.0.1:8030'}}});
