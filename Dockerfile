# Use the official lightweight Python image.
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source files and datasets into the container
COPY election_results_2021.csv .
COPY election_results_2026.csv .
COPY constituency_master.csv .
COPY app.py .

# Expose port 8080 (Cloud Run's default port)
EXPOSE 8080

# Configure Streamlit settings for deployment
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Start Streamlit when the container launches
CMD ["streamlit", "run", "app.py"]
