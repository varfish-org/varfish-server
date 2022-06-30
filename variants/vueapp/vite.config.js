import { fileURLToPath, URL } from "url";
const { resolve } = require("path");
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    // generate manifest.json in outDir
    manifest: true,
    // overwrite default .html entry
    outDir: "static",
    assetsDir: "variants",
    rollupOptions: {
      input: [resolve(__dirname, "./src/main.js")],
    },
  },
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
