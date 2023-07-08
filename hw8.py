import asyncio
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aioschedule import run_pending
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from config import token

logging.basicConfig(level=logging.INFO)

bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_tasks = {}


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я ToDo List Bot. Я помогу тебе организовать список дел. "
                        "Чтобы добавить задачу, используй команду /addtask.")


@dp.message_handler(commands=['addtask'])
async def add_task_command(message: types.Message):
    await message.reply("Чтобы добавить задачу, отправь мне заголовок и время выполнения в формате:\n"
                        "Название_задачи / Время_выполнения (например, Убрать комнату / 15:00).")


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text(message: types.Message):

    text = message.text.split('/')
    if len(text) != 2:
        await message.reply("Неверный формат. Попробуйте еще раз.")
        return

    title = text[0].strip()
    time = text[1].strip()

    user_id = message.from_user.id


    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, time) VALUES (?, ?, ?)", (user_id, title, time))
    conn.commit()
    conn.close()

    if user_id not in user_tasks:
        user_tasks[user_id] = []

    user_tasks[user_id].append({'title': title, 'time': time})
    await message.reply(f"Задача '{title}' добавлена успешно!",
                        reply_markup=create_inline_keyboard(user_id))


@dp.message_handler(commands=['list'])
async def list_command(message: types.Message):
    user_id = message.from_user.id
    tasks = user_tasks.get(user_id)

    if not tasks:
        await message.reply("У вас нет задач.")
        return

    response = "Ваши задачи:\n"
    for index, task in enumerate(tasks):
        response += f"{index + 1}. {task['title']} ({task['time']})\n"

    await message.reply(response, reply_markup=create_inline_keyboard(user_id))


@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def handle_inline_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    task_index = int(callback_query.data.split('_')[1])

    if user_id in user_tasks:
        tasks = user_tasks[user_id]
        if 0 <= task_index < len(tasks):
            tasks.pop(task_index)


            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE user_id = ? AND rowid = ?", (user_id, task_index + 1))
            conn.commit()
            conn.close()

    await bot.answer_callback_query(callback_query.id, text="Задача удалена")
    await bot.edit_message_text("Задача удалена", user_id, callback_query.message.message_id,
                                reply_markup=create_inline_keyboard(user_id))


def create_inline_keyboard(user_id):
    tasks = user_tasks.get(user_id, [])
    keyboard = InlineKeyboardMarkup()
    for index, task in enumerate(tasks):
        button = InlineKeyboardButton(text=f"Удалить {index + 1}", callback_data=f"delete_{index}")
        keyboard.add(button)
    return keyboard


async def send_reminders():
    current_time = datetime.now().strftime("%H:%M")
    for user_id, tasks in user_tasks.items():
        for task in tasks:
            if task['time'] == current_time:
                await bot.send_message(user_id, f"Напоминание: '{task['title']}' ({task['time']})")


async def scheduler():
    while True:
        run_pending()
        await send_reminders()
        await asyncio.sleep(1)

executor.start_polling(dp)