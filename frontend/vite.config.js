import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd(), "");
    var apiTarget = env.VITE_API_TARGET || "http://localhost:8000";
    return {
        plugins: [react()],
        resolve: {
            alias: {
                "@app": fileURLToPath(new URL("./src/app", import.meta.url)),
                "@pages": fileURLToPath(new URL("./src/pages", import.meta.url)),
                "@features": fileURLToPath(new URL("./src/features", import.meta.url)),
                "@shared": fileURLToPath(new URL("./src/shared", import.meta.url))
            }
        },
        server: {
            port: 5173,
            proxy: {
                "/api": {
                    target: apiTarget,
                    changeOrigin: true
                }
            }
        }
    };
});
