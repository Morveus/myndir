# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir Flask Pillow watchdog

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN rm source/ optimized/ -fR 
# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run app.py when the container launches
CMD ["python", "app.py"]
