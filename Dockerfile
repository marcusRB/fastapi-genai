# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for MLflow and JupyterLab
RUN pip install mlflow jupyterlab

# Expose ports for FastAPI, JupyterLab, and MLflow
EXPOSE 80
EXPOSE 8888
EXPOSE 5000

# Set environment variables for MLflow
ENV MLFLOW_SERVER_HOST=0.0.0.0
ENV MLFLOW_SERVER_PORT=5000

# Command to run FastAPI app, JupyterLab, or MLflow based on the SERVICE environment variable
CMD if [ "$SERVICE" = "mlflow" ]; then \
        mlflow server --host 0.0.0.0 --port 5000; \
    else \
        uvicorn src.main:app --host 0.0.0.0 --port 80 & jupyter lab --ip 0.0.0.0 --port 8888 --no-browser --allow-root; \
    fi
