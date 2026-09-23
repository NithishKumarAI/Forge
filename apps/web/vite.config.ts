import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteStaticCopy } from "vite-plugin-static-copy";
import { fileURLToPath } from "node:url";
import { createReadStream } from "node:fs";

const apiTarget = process.env.FORGE_API_PROXY_TARGET ?? "http://127.0.0.1:8000";
const pyodideDirectory = fileURLToPath(new URL("./node_modules/pyodide/", import.meta.url)).replaceAll("\\", "/");
const pyodideFiles = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"];

export default defineConfig({
  plugins: [react(), viteStaticCopy({ targets: [{
    src: pyodideFiles.map((name) => `${pyodideDirectory}/${name}`),
    dest: "assets/pyodide",
  }] }), {
    name: "serve-pyodide-core-in-dev",
    configureServer(server) {
      server.middlewares.use("/assets/pyodide/", (request, response, next) => {
        const name = (request.url ?? "").replace(/^\//, "");
        if (!pyodideFiles.includes(name)) return next();
        response.setHeader("Content-Type", name.endsWith(".mjs") ? "text/javascript" : name.endsWith(".wasm") ? "application/wasm" : name.endsWith(".json") ? "application/json" : "application/zip");
        createReadStream(`${pyodideDirectory}/${name}`).pipe(response);
      });
    },
  }],
  optimizeDeps: { exclude: ["pyodide"] },
  server: {
    port: 5173,
    proxy: {
      "/api": apiTarget,
      "/health": apiTarget,
    },
  },
});
