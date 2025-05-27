# Reference: https://docs.docker.com/reference/dockerfile/
FROM node:23.8-alpine AS builder

ARG VITE_API_URL
COPY frontend/hethongphatnguoi/user /app

WORKDIR /app
RUN npm install
RUN npm run build

FROM nginx:1.27-alpine AS runner

COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /app
