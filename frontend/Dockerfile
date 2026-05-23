# Stage 1: Build the React app
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build
# Output is in /app/dist

# Stage 2: Serve with nginx
FROM nginx:1.27-alpine

# Copy built React app into nginx's web root
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom nginx config for the frontend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
