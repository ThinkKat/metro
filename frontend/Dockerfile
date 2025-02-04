# React 프론트엔드
FROM node:18

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 설치 및 빌드
COPY . .
RUN npm install
RUN npm run build

# Nginx로 배포
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
