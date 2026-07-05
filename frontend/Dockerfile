FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
ARG NPM_CONFIG_REGISTRY=https://registry.npmmirror.com
RUN npm config set registry "${NPM_CONFIG_REGISTRY}" \
    && if [ -f package-lock.json ]; then npm ci; else npm install; fi

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
