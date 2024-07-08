FROM python:3.12-slim

ARG REQUIREMENTS=requirements_production.txt

# Set environment variables
ENV FLASK_APP=govuk-frontend-flask.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000
ENV PYTHONUNBUFFERED=1

RUN apt-get install tzdata

# Create a non-root user
RUN adduser --disabled-password app && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

RUN mkdir /home/app/access
WORKDIR /home/app/access

# Install node
RUN apt-get update \
  && apt-get -y install nodejs npm \
  && apt-get clean
COPY package*.json .
RUN npm install

COPY requirements/generated/$REQUIREMENTS requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY app ./app
COPY govuk-frontend-flask.py .

RUN npm run build

# Change ownership of the working directory to the non-root user
RUN chown -R app:app /home/app

# Switch to the non-root user
USER app

# Expose the Flask port
EXPOSE 8000

# Run the Flask application for development
CMD ["flask", "run"]
