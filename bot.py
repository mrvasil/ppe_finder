import telebot
from telebot import types, async_telebot
import asyncio
import re
import os
import requests
import pandas as pd
from io import BytesIO

API_TOKEN = os.getenv('TELEBOT_API_TOKEN')
bot = async_telebot.AsyncTeleBot(API_TOKEN)
user_choice = {}


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



async def work_with_file(bot, message, file_name, downloaded_file, work_type):
    try:
        if file_name.endswith('.xlsx') and work_type == 'select_ppe':
            df = pd.read_excel(BytesIO(downloaded_file))
            items = df.iloc[:, 0].tolist()
            chunks = [items[i:i + 100] for i in range(0, len(items), 100)]
            a = []
            for j in chunks:
                #j = "Сапоги\nНоутбук\nКаска защитная;Комбинезон облученный Радио-Протект размер XXL; Очки RUSH затемненные RUSHPPSF"
                text = ""
                for i in j:
                    text += clear_string(i) + "\n"
                url = "https://18f1-188-94-32-102.ngrok-free.app/api/generate"
                prompt = f"Дорогой друг, мы с тобой говорим на одном языке - русском! Ты — выдающийся специалист в своей области. За каждую задачу, которую я тебе доверяю, ты получаешь 1000 долларов и 10000 рублей. Важно помнить, что ты не должен допускать ошибок.   Теперь, пожалуйста, определи, является ли следующая номенклатура средством индивидуальной защиты. Отвечай только цифрами: 1 — если элемент является средством индивидуальной защиты, 0 — если не является. Номенклатура: {text}"
                data = {
                    "model": "gemma2",
                    "prompt": prompt,
                    "stream": False
                }
                response = requests.post(url, json=data)
                response_json = response.json()
                value = response_json.get('response')
                print(value)
                for i in value.split("\n"):
                    if (i == "0") or (i == "0 ") or (i == "1") or (i == "1 "):
                        a.append(i[0])
                    elif (i == "") or (i == " ") or (i == "\n"):
                        aaaaaaaaaaa=1
                    else:
                        a.append("-")
            while len(a) < len(items):
                a.append("-")
            while len(a) > len(items):
                try:
                    a.pop(a.index("-"))
                except:
                    a.pop(-1)
            df['СИЗ'] = a
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            output.name = "new_table.xlsx"
            return output
        elif file_name.endswith('.xlsx') and work_type == 'use_regexp':
            df = pd.read_excel(BytesIO(downloaded_file))
            #df['Размеры'] = df.iloc[:, 0].apply(lambda x: ' '.join(re.findall(r'\d+', str(x))))
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
