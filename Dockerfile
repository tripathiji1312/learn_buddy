# Use an official lightweight Python image as a starting point.
FROM python:3.10-slim

# Set the working directory inside the container to /app.
WORKDIR /app

# Copy the dependencies file first. This is a clever trick for faster builds.
COPY requirements.txt .

# Install the Python libraries listed in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container.
COPY . .

# Tell Docker what command to run when the container starts.
# This starts your FastAPI server.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
