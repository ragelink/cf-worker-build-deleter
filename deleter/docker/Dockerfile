FROM python:3.11-slim

WORKDIR /app

# Create source directory structure
RUN mkdir -p src

# Copy requirements first for better caching
COPY src/requirements.txt src/
RUN pip install --no-cache-dir -r src/requirements.txt

# Copy the Python package files
COPY src/__init__.py src/
COPY src/delete_deployments.py src/
COPY README.md .

# Make the script executable
RUN chmod +x src/delete_deployments.py

# Create a non-root user to run the script
RUN useradd -m deleter
USER deleter

# Set up entrypoint and default command
ENTRYPOINT ["python3", "-m", "src.delete_deployments"]

# By default, show help
CMD ["--help"] 