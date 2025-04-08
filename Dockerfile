FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY frontend ./frontend
COPY backend ./backend

# Build frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Create static directory and copy frontend build files
WORKDIR /app
RUN mkdir -p backend/static
RUN cp -r frontend/build/* backend/static/

# Set working directory to backend for running the app
WORKDIR /app/backend

# Set environment variable to run in headless mode
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app