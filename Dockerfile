FROM wheelwisebase

# Change working directory to app folder
WORKDIR /app-docker

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the requirements
RUN pip3 install -r requirements.txt

# Copy the rest of the files to the working directory except the ones in .dockerignore
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the app
CMD python3 -m flask run --host=0.0.0.0