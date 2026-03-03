# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app

COPY frontend/package.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ .
RUN npm run build

# Stage 2: Nginx with built frontend
FROM nginx:1.25-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy nginx config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

EXPOSE 80
