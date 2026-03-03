# Standalone frontend Dockerfile (for local development builds)
# In production, the nginx/Dockerfile handles both frontend build and serving

FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
