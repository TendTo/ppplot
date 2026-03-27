import { defineConfig } from "vite";

export default defineConfig({
  root: "web",
  base: "/ppplot/",
  publicDir: "../docs/_static",
  server: {
    port: 5173,
    open: false,
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
