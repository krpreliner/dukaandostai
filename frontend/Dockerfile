# Multi-stage Dockerfile for DukaanDost AI Frontend
# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package.json ./
# If package-lock.json exists, copy it, else npm install
COPY frontend/package*.json ./

RUN npm install

COPY frontend/ ./

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
