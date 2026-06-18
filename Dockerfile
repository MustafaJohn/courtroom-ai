FROM python:3.11-slim

WORKDIR /app

# Install dependencies first — separate layer so code changes don't
# force a reinstall of unchanged dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY agents/ ./agents/
COPY core/ ./core/
COPY graph/ ./graph/
COPY cases/ ./cases/
COPY main.py .
COPY streamlit_app.py .

# Output directory is created at runtime by main.py, but pre-create it
# so it exists with correct permissions even before the first run.
RUN mkdir -p output

ENTRYPOINT ["python", "main.py"]