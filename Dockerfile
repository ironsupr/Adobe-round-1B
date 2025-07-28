# Adobe Hackathon Challenge 1B - Dockerfile
# Optimized for CPU-only execution with fast startup and execution

FROM python:3.9-slim

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies (minimal set for PyMuPDF)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY main_1b_dynamic.py .

# Copy the docudots_module directory
COPY docudots_module/ ./docudots_module/

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set proper permissions
RUN chmod +x main_1b_dynamic.py

# Health check to ensure the container is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import docudots_module.core; print('Container ready')" || exit 1

# Default command to run the main script
# Note: Users should mount their input files and override this command
# Build and run commands:
# docker build --platform linux/amd64 -t docudots-challenge1b:v1.0 .
# docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none docudots-challenge1b:v1.0

CMD ["python", "main_1b_dynamic.py", "--input", "/app/input/challenge1b_input.json"]

# Metadata
LABEL maintainer="Adobe Hackathon Challenge 1B"
LABEL description="Document Analysis System for Adobe Hackathon Challenge 1B"
LABEL version="1.0"
LABEL constraints="CPU-only, <1GB model size, <60s execution time"
