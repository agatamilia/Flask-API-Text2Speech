# Gunakan base image Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy aplikasi Flask
COPY . /app

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Command untuk menjalankan aplikasi Flask
CMD ["python", "app.py"]

