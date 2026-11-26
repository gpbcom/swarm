// Assemble the pages the Tauri shell serves: one folder per app under `frontend/apps/desktop/dist/`.
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const desktop = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const frontends = resolve(desktop, "..");
const dist = join(desktop, "dist");
const apps = ["ground-control", "mission-studio"];

for (const app of apps) {
  const build = join(frontends, app, "dist");
  if (!existsSync(join(build, "index.html"))) {
    console.error(`The build of ${app} is missing: run \`pnpm --filter @swarm/${app} build\` first (${build}).`);
    process.exit(1);
  }
}

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });
for (const app of apps) {
  cpSync(join(frontends, app, "dist"), join(dist, app), { recursive: true });
  console.log(`Assembled ${app} into ${join(dist, app)}.`);
}
