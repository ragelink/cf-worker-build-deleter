FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script and other files
COPY delete_deployments.py .
COPY README.md .

# Make the script executable
RUN chmod +x delete_deployments.py

# Create a non-root user to run the script
RUN useradd -m deleter
USER deleter

# Set up entrypoint and default command
ENTRYPOINT ["python3", "delete_deployments.py"]

# By default, show help
CMD ["--help"] 