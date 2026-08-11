# ============================================================
# Stage 1: Build dependencies in an isolated virtual environment
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install only what pip needs to build wheels (none for pure-Python
# deps, but kept for future C-extension packages).
COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Slim runtime image
# ============================================================
FROM python:3.11-slim

# Create a non-root user and group
RUN groupadd --system app && \
    useradd --system --gid app --create-home app

WORKDIR /home/app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy only the application package (no tests, no dotfiles)
COPY app/ ./app/

# Make venv binaries the default
ENV PATH="/opt/venv/bin:$PATH"

# Declare the port (informational — does not publish)
EXPOSE 8000

# Switch to the non-root user
USER app

# Run the server (no --reload — production mode)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
