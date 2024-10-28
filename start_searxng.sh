#!/bin/bash

# sudo lsof -i :8080
# sudo kill -9 <PID>

PID_=$(sudo lsof -t -i :8080)
sudo kill -9 $PID_
echo "Killed process $PID_ running on port 8080."

cd /home/krish/my-instance

export PORT=8080

# Pull the latest searxng/searxng Docker image
# docker pull searxng/searxng

# Run the Docker container
sudo docker run --rm \
           -d -p ${PORT}:8080 \
           -v "${PWD}/searxng:/etc/searxng" \
           -e "BASE_URL=http://localhost:$PORT/" \
           -e "INSTANCE_NAME=my-instance" \
           searxng/searxng


# Make the script executable before running
# chmod +x start_searxng.sh

# Running this .sh file will start the searxng instance
# sh ./start_searxng.sh