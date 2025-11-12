#Docker Multistage Build (Production)
#===============================================
#Build Stage
#===============================================
FROM node:22-alpine AS build
# Set the working directory inside the container
WORKDIR /app
# Copy package.json and package-lock.json
COPY package*.json ./
# Use ci in CI/prod for reproducible installs (falls back to install if no lock)
RUN npm ci || npm install
#Provide a build-time API URL (default can be localhost for dev)
ARG REACT_APP_API_URL=http://localhost:5000/api
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
# Copy the rest of your application files
COPY . .
# Build the react application
RUN npm run build
#===============================================    
# Production Stage
#===============================================
FROM nginx:alpine  AS production
# Copy the build output to replace the default nginx contents.
COPY --from=build /app/build /usr/share/nginx/html
# Expose the port your app runs on
EXPOSE 80
# Define the command to run your app
CMD ["nginx", "-g", "daemon off;"]
#===============================================