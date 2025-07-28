# Use an official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install required packages
RUN pip install pymupdf sentence-transformers

# Copy your code into the container
COPY main.py .

# Run the script
CMD ["python", "main.py"]
