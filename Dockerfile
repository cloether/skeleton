FROM python:3.13-alpine
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]
COPY . .
ENV PYTHONPATH="/app"
RUN addgroup -S projects && adduser -S -H projects -G projects
RUN chown -R projects:projects /app
USER projects