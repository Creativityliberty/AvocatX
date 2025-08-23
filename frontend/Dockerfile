# Stage 1: Build React app
FROM node:20-alpine AS build
WORKDIR /app

# Install deps
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

# Build-time API URL (can be overridden by build args)
ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Build static site
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy build to nginx html dir
COPY --from=build /app/build /usr/share/nginx/html

# SPA routing config
RUN printf 'server {\n  listen 80;\n  server_name _;\n  root /usr/share/nginx/html;\n  index index.html;\n  location / {\n    try_files $$uri /index.html;\n  }\n  location /static/ {\n    expires 1y;\n    add_header Cache-Control "public";\n  }\n}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
