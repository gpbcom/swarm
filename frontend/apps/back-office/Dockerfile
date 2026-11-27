FROM node:22.21-alpine3.22 AS build
RUN npm install --global pnpm@12.21.0
WORKDIR /repo
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend/apps/back-office/package.json ./frontend/apps/back-office/package.json
COPY frontend ./frontend
COPY qa/e2e/package.json ./qa/e2e/package.json
RUN pnpm install --frozen-lockfile --filter @swarm/back-office...
RUN pnpm --filter @swarm/back-office build

FROM nginxinc/nginx-unprivileged:1.31.7-alpine3.24
# Security fixes the base image does not carry yet: take every Alpine update as root, then run unprivileged again.
USER root
RUN apk upgrade --no-cache
COPY --from=build /repo/frontend/apps/back-office/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/frontend/apps/back-office/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
