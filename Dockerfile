# Dockerfile

# Use an official Python runtime as the base image
FROM h4ckermike/swarms-api:experimental

# Set environment variables to ensure output is not buffered
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
#ENV OPENAI_API_KEY="your_key"
ENV WORKSPACE_DIR="agent_workspace"

# Set the working directory inside the container
WORKDIR /opt/mcs/api

# Install dependencies
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends build-essential

# Update and install required system packages
#RUN apt-get install -y --no-install-recommends sqlite3     libsqlite3-dev

# Copy only requirements first (for better caching)
#COPY ./api/requirements.txt /app/requirements.txt

#RUN pip install --no-cache-dir -r requirements.txt 

# we can remove the build essential after the fact so we can build the reqs apart
#RUN apt-get remove -y build-essential 

RUN mkdir -p /opt/mcs
# Copy the rest of the application code
COPY ./api /opt/mcs/api

# Make the bootup script executable
#RUN chmod +x bootup.sh

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["bash -x /opt/mcs/api/bootup.sh"]
