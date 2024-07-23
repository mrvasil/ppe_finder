import telebot
from telebot import types, async_telebot
import asyncio

import pandas as pd
import csv
import random
from io import BytesIO

API_TOKEN = '6928281910:AAE_vQmCivZfB9IEpK3BzuDHmEIv6zzzJr0'
bot = async_telebot.AsyncTeleBot(API_TOKEN)
user_choice = {}

async def work_with_file(bot, message, file_name, downloaded_file, work_type):
    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(downloaded_file))  
            df['Random_SIZ'] = [random.randint(0, 1) for _ in range(len(df))]
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            output.name = "new_table.xlsx"
            return output
        elif file_name.endswith('.csv'):
            with downloaded_file as r_file:
                file_reader = csv.reader(r_file, delimiter = "\n")
                for row in file_reader:
                    print(row[0])
            return downloaded_file
        else:
            await bot.reply_to(message, "Неподдерживаемый формат файла.")
            return
    except Exception as e:
        print(e)
        await bot.reply_to(message, "Ошибка при обработке файла.")
        return

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Выделить СИЗы", callback_data="select_ppe")
    btn2 = types.InlineKeyboardButton("Разделить СИЗ на категории", callback_data="ppe_category")
    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_choice[call.from_user.id] = call.data
    await bot.answer_callback_query(call.id, "Опция выбрана: {}".format(call.data))
    with open('example.png', 'rb') as image:
        await bot.send_photo(call.message.chat.id, image)
    await bot.send_message(call.message.chat.id, "*Теперь вы можете отправить файл .xlsx или .csv.* \n\nФайл должен выглядеть как один столбец, первая строчка которого это его название.", parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
async def handle_docs(message):
    if message.from_user.id in user_choice and user_choice[message.from_user.id]:
        if message.document.mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']:
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            file_name = message.document.file_name

            output_file = await work_with_file(bot, message, file_name, downloaded_file, user_choice[message.from_user.id])
            await bot.send_document(message.chat.id, output_file, caption="Новый файл:")

            user_choice[message.from_user.id] = None
            await bot.send_message(message.chat.id, "Обработать файл заново - /start")
        else:
            await bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате .xlsx или .csv.")
    else:
        await bot.send_message(message.chat.id, "Пожалуйста, сначала выберите опцию.")

async def main():
    await bot.polling()

if __name__ == '__main__':
    asyncio.run(main())