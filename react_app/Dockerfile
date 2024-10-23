# Use an official Node.js image from Docker Hub
FROM node:14-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the React application
COPY . .

# Build the React app
RUN npm run build

# Expose the port the React app will run on
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
