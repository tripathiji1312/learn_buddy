# Use an official lightweight Python image as a starting point.
FROM python:3.10-slim

# Set the working directory inside the container to /app.
WORKDIR /app

# --- OPTIMIZED INSTALLATION ---

# 1. Install the HEAVY libraries first to create a stable, cached layer.
# Copy only the heavy requirements file first.
COPY requirements-heavy.txt .
# Run pip install for just the heavy libraries. This layer will be cached
# unless requirements-heavy.txt itself changes.
RUN pip install --no-cache-dir -r requirements-heavy.txt

# 2. Install the REST of the libraries.
# Now copy the main requirements file.
COPY requirements.txt .
# Run pip install again. Pip is smart and will only install the
# missing packages, making this step very fast.
RUN pip install --no-cache-dir -r requirements.txt

# --- END OPTIMIZED INSTALLATION ---

# Copy the rest of your application code into the container.
# This step will re-run when you change your .py files, but the slow
# pip installs above will be cached.
COPY . .

# Tell Docker what command to run when the container starts.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:7860", "src.main:app"]