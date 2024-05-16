FROM python:3.12-slim
USER 1000

# Set the working directory in the container
WORKDIR /usr/src/app

# Create a non-root user
RUN adduser --disabled-password --gecos '' containeruser

# Change ownership of the working directory to the non-root user
RUN chown -R containeruser:containeruser /usr/src/app

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.in

# Switch to the non-root user
USER containeruser

# Expose the Flask port
EXPOSE 8000

# Run the Flask application for development
CMD ["flask", "run", "--cert=adhoc"]