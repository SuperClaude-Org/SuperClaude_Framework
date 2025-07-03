import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts", "src/main.ts"],
  format: ["cjs", "esm"],
  dts: true,
  clean: true,
  minify: process.env.NODE_ENV === "production",
  target: "node18",
  outDir: "dist",
  sourcemap: true,
  esbuildOptions(options) {
    options.platform = "node";
  },
});
