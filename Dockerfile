FROM python:3.12-slim

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# Set the working directory in the container
WORKDIR /usr/src/app

# Create a non-root user
RUN adduser --disabled-password --gecos '' containeruser

# Change ownership of the working directory to the non-root user
RUN chown -R containeruser:containeruser /usr/src/app

# Copy the dependencies file to the working directory
COPY requirements.in ./

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.in

# Copy the project code into the working directory
COPY . .

# Switch to the non-root user
USER containeruser

# Expose the Flask port
EXPOSE 8000

# Run the Flask application for development
CMD ["flask", "run"]