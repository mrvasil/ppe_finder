# PPE Classificator

## About

The bot provides functionality to help classify Personal Protective Equipment (PPE) items from a general list of purchase items. It can process Excel files and provide categorization results directly in Telegram.


## Usage

You can interact with this bot on Telegram by searching for [@ppe_find_bot](https://t.me/ppe_find_bot)



## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.8 or higher
- Docker (for Docker deployment)

## Running the Project with Docker

To run this project using Docker, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/mrvasil/ppe_finder.git
   cd ppe_finder
   ```

2. Run the update model script:
   ```bash
   chmod +x ./update_model.sh
   ./update_model.sh
   ```

3. Build the Docker image:
   ```bash
   docker build -t ppe_finder .
   ```

4. Run the Docker container, replacing `your_actual_token_here` with your Telegram bot token:
   ```bash
   docker run -e TELEBOT_API_TOKEN='your_actual_token_here' ppe_finder
   ```

This will pull the necessary images, install all dependencies, run the update script, and start the bot.

## Running the Project on Your Host System

To run this project on your host system, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/mrvasil/ppe_finder.git
   cd ppe_finder
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   #For Linux (CPU)
   pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu
   pip install pytelegrambotapi pandas aiohttp torchtext==0.17.2 openpyxl
   ```

4. Set the environment variable for the Telegram bot API token:
   ```bash
   export TELEBOT_API_TOKEN='your_actual_token_here'
   ```

5. Run the update model script:
   ```bash
   chmod +x ./update_model.sh
   ./update_model.sh
   ```

6. Start the bot:
   ```bash
   python3 bot.py
   ```



Project for 1bit company.