import re
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

# Настройки бота
BOT_TOKEN = '6013783188:AAHyZpey2HGn4R0uNC9zbdE7dHYGwOqzsIs'

# Настройки SMTP-сервера для отправки почты
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'tasievbajel2@gmail.com'
SMTP_PASSWORD = 'mojakuirmysazusx'
# Параметры подключения к базе данных SQLite
DB_FILE = 'bot.db'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (chat_id INTEGER PRIMARY KEY, email TEXT, format TEXT)''')
conn.commit()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.reply("Привет! Я бот для отправки видео с YouTube на почту. Пожалуйста, укажи свою почту.")


@dp.message_handler(regexp=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
async def email_handler(message: types.Message):
    email = message.text

    cursor.execute('SELECT * FROM users WHERE chat_id=?', (message.chat.id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('UPDATE users SET email=? WHERE chat_id=?', (email, message.chat.id))
    else:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (message.chat.id, email, None))

    conn.commit()

    await message.reply("Отлично! Теперь укажи формат, в котором хочешь получить видео (mp3 или mp4).")


@dp.message_handler(regexp=r'^(mp3|mp4)$')
async def format_handler(message: types.Message):
    chosen_format = message.text

    cursor.execute('UPDATE users SET format=? WHERE chat_id=?', (chosen_format, message.chat.id))
    conn.commit()

    await message.reply("Хорошо! Теперь отправь мне ссылку на видео с YouTube.")


@dp.message_handler(regexp=r'^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+')
async def youtube_link_handler(message: types.Message):
    video_url = message.text

    video_id = re.search(r'(?:\?v=|\/embed\/|\.be\/)([^&\n?#]+)', video_url)
    if video_id:
        video_id = video_id.group(1)
    else:
        await message.reply("Не удалось извлечь идентификатор видео. Пожалуйста, убедитесь, что ссылка является корректной.")
        return

    cursor.execute('SELECT * FROM users WHERE chat_id=?', (message.chat.id,))
    user = cursor.fetchone()

    if not user or not user[1] or not user[2]:
        await message.reply("Пожалуйста, сначала укажите свою почту и формат.")
        return

    email = user[1]
    chosen_format = user[2]

    try:
        smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_server.starttls()
        smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = 'YouTube Video'

        video_attachment = MIMEBase('application', chosen_format)
        video_attachment.set_payload(video_url)
        encoders.encode_base64(video_attachment)
        video_attachment.add_header('Content-Disposition', f'attachment; filename="{video_id}.{chosen_format}"')
        msg.attach(video_attachment)

        smtp_server.send_message(msg)
        smtp_server.quit()

        await message.reply(f"Видео успешно отправлено на почту {email} в формате {chosen_format}.")
    except smtplib.SMTPException as e:
        await message.reply("Произошла ошибка при отправке письма. Пожалуйста, попробуйте еще раз позже.")
        print(str(e))


if __name__ == '__main__':
    executor.start_polling(dp)