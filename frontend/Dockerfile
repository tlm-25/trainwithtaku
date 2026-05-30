#Frontend docker image - This docker image is a multi-stage build - first stage for buildin 

#Stage 1 - build stage
#base image - using node which is what react runs on
FROM node:22-alpine as build 

#set working directory inside container
WORKDIR /app 

#Copy the depencencies from page.json and pckage-lock.json in working directory
COPY ./package*.json ./
#Install dependencies
RUN npm install 


#copy all files from local directory into container directory (i.e. "app" directory)
COPY . .
# declare build arg and expose as env var so Vite can read it during build
ARG VITE_BASE_URL
ENV VITE_BASE_URL=$VITE_BASE_URL

RUN npm run build && ls -la /app


#Stage 2 - production/serving stage - image to serve the static files 

#base image for ngnix - used to server static files (HTML/CSS/JS)
FROM nginx:stable-alpine AS production

#copy build output from previous stage - dist is output build folder if using vite 
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

#RUN ngnix in the foreground to serve the static files in the front end 
CMD ["nginx", "-g", "daemon off;"]