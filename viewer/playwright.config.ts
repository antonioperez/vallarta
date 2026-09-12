import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/browser",
  // Software WebGL on shared CI runners can take longer between interactions.
  timeout: process.env.CI ? 60_000 : 30_000,
  use: {
    baseURL: process.env.VIEWER_URL || "http://127.0.0.1:4173",
    viewport: { width: 1440, height: 1000 },
    screenshot: "only-on-failure",
  },
  webServer: process.env.VIEWER_URL
    ? undefined
    : {
        command: "npm run preview -- --port 4173",
        url: "http://127.0.0.1:4173",
        reuseExistingServer: !process.env.CI,
      },
});
