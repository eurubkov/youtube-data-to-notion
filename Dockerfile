# Use an official Python runtime as a parent image
FROM python:3.11

RUN apt-get update && apt-get install -y zip && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install AWS CDK globally
RUN npm install -g aws-cdk

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Keep the container running indefinitely to allow users to interact with it
CMD ["tail", "-f", "/dev/null"]
