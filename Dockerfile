FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir pytelegrambotapi pandas aiohttp torchtext==0.17.2 openpyxl

RUN apt update
RUN apt install -y wget

RUN chmod +x ./update_model.sh
RUN ./update_model.sh

RUN export TELEBOT_API_TOKEN='your_actual_token_here'

CMD ["python3", "bot.py"]