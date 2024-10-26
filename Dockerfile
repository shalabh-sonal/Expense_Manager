FROM python:3.9-slim

WORKDIR /expense_manager

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \            
    gcc \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first to leverage Docker cache
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

# also can use ADD but it is slow but use if (want to copy files 
# from a URL directly / or extract and add a zip file) 
COPY . .

# not work as defined in docker-compose
ENV FLASK_APP=run.py  
ENV PYTHONUNBUFFERED=1 


# Create an entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/bin/sh", "./entrypoint.sh"]