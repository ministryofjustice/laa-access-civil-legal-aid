ARG BASE_IMAGE=python:3.12-slim

FROM node:lts-iron as node_build
WORKDIR /home/node
COPY esbuild.config.js package.json package-lock.json ./
COPY app/static/src app/static/src
RUN npm install
RUN npm run build


FROM $BASE_IMAGE AS base
ARG REQUIREMENTS_FILE=requirements-production.txt

# Set environment variables
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=${FLASK_RUN_PORT:-8000}
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN adduser --disabled-password app -u 1000 && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

RUN mkdir /home/app/access
WORKDIR /home/app/access

COPY --from=node_build /home/node/app/static/dist/ app/static/dist/

COPY requirements/generated/$REQUIREMENTS_FILE requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app ./app

# Change ownership of the working directory to the non-root user
RUN chown -R app:app /home/app

# Cleanup container
RUN rm -rf /var/lib/apt/lists/*

# Switch to the non-root user
USER app

# Expose the Flask port
EXPOSE $FLASK_RUN_PORT

# Run the Flask application for production
FROM base AS production
# TODO: Use a production ready WSGI
CMD ["flask", "run"]

# Run the Flask application for development
FROM base AS development
CMD ["flask", "run", "--debug"]
