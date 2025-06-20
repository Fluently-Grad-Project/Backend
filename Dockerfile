# -------- Stage 1: Build stage --------
    FROM python:3.11-slim as builder

    WORKDIR /install
    
    #install build dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt .
    
    #install dependencies to a temporary directory
    RUN pip install --upgrade pip && \
        pip install --prefix=/install/deps --no-cache-dir -r requirements.txt
    
    # -------- Stage 2: Runtime stage --------
    FROM python:3.11-slim
    
    WORKDIR /app
    
    #the installed packages from builder stage
    COPY --from=builder /install/deps /usr/local
    
    #application code
    COPY . .
    
    EXPOSE 8000
    
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]    