# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the local directory contents into the container
COPY . .

# Install any needed packages specified in requirements
RUN pip install --no-cache-dir torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir pytelegrambotapi pandas aiohttp torchtext==0.17.2 openpyxl

# Make the model update script executable and run it
RUN chmod +x ./update_model.sh
RUN ./update_model.sh

# Run bot.py when the container launches
CMD ["python3", "bot.py"]