FROM python:3.12-slim

# Create non-root user (required by HF Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install dependencies first (cached layer)
COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY --chown=user . /app

# Create uploads folder
RUN mkdir -p /app/uploads

# HF Spaces requires port 7860
EXPOSE 7860

# gunicorn timeout 120s gives model time to load on first request
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "app:app"]
