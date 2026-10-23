# ---- Stage 1: build the React application ----
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# ---- Stage 2: serve the static bundle with an unprivileged Nginx ----
FROM nginxinc/nginx-unprivileged:1.31-alpine

LABEL org.opencontainers.image.title="stockpilot-frontend" \
      org.opencontainers.image.description="StockPilot inventory dashboard (React + Nginx)" \
      org.opencontainers.image.authors="Vibhuti Bhatnagar (24bcs10288)" \
      org.opencontainers.image.source="https://github.com/vibhuti-scaler/stockpilot"

# Backend upstream; overridden per environment (Compose / Helm)
ENV BACKEND_URL=http://backend:8000

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# nginx-unprivileged already runs as UID 101 (nginx) and listens on 8080
USER 101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/nginx-health >/dev/null 2>&1 || exit 1
