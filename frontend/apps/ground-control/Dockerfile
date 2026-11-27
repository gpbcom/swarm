FROM node:22.21-alpine3.22 AS build
RUN npm install --global pnpm@12.21.0
WORKDIR /repo
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend ./frontend
COPY qa/e2e/package.json ./qa/e2e/package.json
RUN pnpm install --frozen-lockfile --filter @swarm/ground-control...
RUN pnpm --filter @swarm/ground-control build
RUN if [ ! -f frontend/apps/ground-control/dist/config.json ]; then \
      printf '%s' '{"liveUrl":"ws://localhost:8080/v1/live","missionId":null,"tilesUrl":"tiles/basemap.pmtiles","metricsUrl":null,"metricsIntervalS":60,"cell":null,"livePath":"edge"}' \
      > frontend/apps/ground-control/dist/config.json; \
    fi

FROM nginxinc/nginx-unprivileged:1.27-alpine3.21
COPY frontend/apps/ground-control/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /repo/frontend/apps/ground-control/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
