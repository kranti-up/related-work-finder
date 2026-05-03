FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies first (caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Hugging Face Spaces runs as a non-root user (user ID 1000).
# We must give permission to write the database and download the BibTeX files.
RUN chmod -R 777 /app/backend

# Switch to the backend directory where main.py lives
WORKDIR /app/backend

# HF Spaces requires the application to listen on port 7860
EXPOSE 7860

# Give KeyBERT a writable temp folder to download the transformer models
ENV TRANSFORMERS_CACHE="/tmp"
ENV HF_HOME="/tmp"

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
