# Use Node.js as base image since we need it for the frontend
FROM node:18 AS frontend-builder

# Set working directory
WORKDIR /app

# Copy frontend files and build
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Switch to Playwright image for Python/backend
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./backend

# Copy built frontend from the first stage
COPY --from=frontend-builder /app/frontend/build ./backend/static

# Set working directory to backend
WORKDIR /app/backend

# Set environment variable for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app