/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SWARM_IDENTITY_URL?: string;
  readonly VITE_SWARM_GATEWAY_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
