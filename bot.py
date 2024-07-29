import telebot
from telebot import types, async_telebot
import asyncio
import torch
import re
import os

import pandas as pd
import csv
import random
from io import BytesIO
from models import extra_model, base_model, text_pipeline_extra, text_pipeline_base, TextClassificationModel

API_TOKEN = os.getenv('TELEBOT_API_TOKEN')
bot = async_telebot.AsyncTeleBot(API_TOKEN)
user_choice = {}
extra_model.load_state_dict(torch.load("extra.pt"))
extra_model.eval()
base_model.load_state_dict(torch.load("base.pt"))
base_model.eval()
extra_model = extra_model.to("cpu")
base_model = base_model.to("cpu")
keys = pd.read_csv('keys.csv', sep=';')
keys_dict = {
}

for i in keys.iloc:
    keys_dict.update({i[0]: i[1]})

stopwords = ['разм', 'для', 'под', 'чер', 'леди', 'бел', 'син', 'модель', 'мод']


def clear_string(description):
    s = description
    s = re.sub('"(.+)"', '\\1', s, 1)
    s = re.sub('""', '"', s)
    s = re.sub('(.+)"(.+)"(.+)', '\\1\\3', s)
    s = " " + s + " "
    s = re.sub('[\\d\'"()-/;%abcdefghijklmnopqrstuvwxyz™]+', ' ', s, flags=re.IGNORECASE)
    s = re.sub('(\\w) ', '\\1  ', s, flags=re.IGNORECASE)
    s = re.sub(' \\w\\w? ', ' ', s, flags=re.IGNORECASE)
    s = re.sub(' +', ' ', s).strip().lower()
    s = remove_blacklisted_words(s)
    return s


def remove_blacklisted_words(description):
    query_words = description.split()
    result_words = [word for word in query_words if word.lower() not in stopwords]
    return ' '.join(result_words)


def predict_extra(text):
    with torch.no_grad():
        text = torch.tensor(text_pipeline_extra(clear_string(text)))
        output = extra_model(text, torch.tensor([0]))
        return output.argmax(1).item()


def predict_base(text):
    with torch.no_grad():
        text = torch.tensor(text_pipeline_base(clear_string(text)))
        output = base_model(text, torch.tensor([0]))
        return keys_dict[output.argmax(1).item()]


async def work_with_file(bot, message, file_name, downloaded_file, work_type):
    try:
        if file_name.endswith('.xlsx') and work_type == 'select_ppe':
            df = pd.read_excel(BytesIO(downloaded_file))
            a = [
            ]
            for j in range(len(df)):
                to_predict = df.values[j][0]
                extra_pred = predict_extra(to_predict)
                if extra_pred == 0:
                    a.append("-")
                else:
                    a.append(predict_base(to_predict))
            df['СИЗ'] = a
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            output.name = "new_table.xlsx"
            return output
        elif file_name.endswith('.xlsx') and work_type == 'use_regexp':
            df = pd.read_excel(BytesIO(downloaded_file))
            df['Размеры'] = df.iloc[:, 0].apply(lambda x: ''.join(filter(str.isdigit, str(x))))
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            output.name = "sizes_extracted.xlsx"
            return output
        else:
            await bot.reply_to(message, "Неправильный формат файла")
            return
    except Exception as e:
        print(e)
        await bot.reply_to(message, "Возникла ошибка при обрабоке файла.")


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Разделить номенклатуры", callback_data="select_ppe")
    btn2 = types.InlineKeyboardButton("Отделить размеры", callback_data="use_regexp")
    markup.add(btn1, btn2)
    await bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_choice[call.from_user.id] = call.data
    await bot.answer_callback_query(call.id, "Опция выбрана: {}".format(call.data))
    if (call.data == "select_ppe") or (call.data == "use_regexp"):
        with open('example.png', 'rb') as image:
            await bot.send_photo(call.message.chat.id, image)
        await bot.send_message(call.message.chat.id, "*Теперь вы можете отправить файл .xlsx* \n\nФайл должен выглядеть как один столбец, первая строчка которого это его название.", parse_mode='Markdown')
    else:
        user_choice[call.from_user.id] = None
        await bot.send_message(call.message.chat.id, "Функция не доступна")

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
            await bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате .xlsx")
    else:
        await bot.send_message(message.chat.id, "Пожалуйста, сначала выберите опцию.")

async def main():
    await bot.polling()

if __name__ == '__main__':
    asyncio.run(main())
#%%
