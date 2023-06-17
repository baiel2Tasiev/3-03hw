from aiogram import Bot , Dispatcher , types , executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMCpntext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import token
import sqlite3, time, logging



bot = Bot(token)
storage =MemoryStorage
dp = Dispatcher (bot)
logging.basicConfig(level=logging.INFO)

database = sqlite3.connect('user.db')
cursor = database.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INT,
    chat_id INT,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created VARCHAR(100)
    
);
""")
cursor.connection.commit()    

keyboard_buttons = [
    KeyboardButtons('/start'),
    KeyboardButtons('/help'),
    KeyboardButtons('/test'),
    KeyboardButtons('/mailing')
]
Keyboatd_one = ReplayKeyboardMArkup(resize_keybiard=True, one_time_keyboard=True, row_width=30).add(*keyboard_buttons)


@dp. message_handler(commands='start')
async def start(message:types.Message):
    # cursor.execute(f"SELECT *)
    cursor.execute(f"""INSERT INTO users VALUES ({message.from_user.id},
                   {message.chat.id}, '{message.from_user.username}',
                   '{message.from_user.first_name}', 
                   '{message.from_user.last_name}',
                   '{time.ctime()}');
                   """)
    cursor.connection.commit()
    await message.answer(f"Привет {message.from_user.full_name}", replay_markup=keyboard_one)
    
@dp.message_handler(commands='help')
async def help(message:types.Message):
    await message.answer("Чем я могу помочь?")
  
@dp.message_handler(commands="help")
async def help(message:types.Message):
    await message.replay("Приветик")  
    
@dp.message_handler(commands="test")
async def testing(message:types.Message):
    await message.answer_dice()
    await message.answer_location(41, 52)
    await message.answer_photo("https://mimigram.ru/wp-content/uploads/2020/07/%D0%A7%D1%82%D0%BE-%D1%82%D0%B0%D0%BA%D0%BE%D0%B5-%D1%84%D0%BE%D1%82%D0%BE.jpeg")
  
class MAilingState(StatesGroup):
    text = State()

@dp.message_handler(commands='mailing')
async def mailing(message:types.Message):
    if message.from_user.id in [731982105]
        await message.replay("Введите текст для рассылки:")
        await MAilingState.text.set()
    else:
        await message.answer("У вас нет прав")
    
    
@dp.message_handler(state=MailingState.text)
async def send_mailing_text(message:types.Message, state:FSMContext):
    await message.answer("Начинаю рассылку")
    cursor.execute("SELECT chat_id FROM users;")
    chat_id = cursor.fetchall()
    for chat id chats_id:
        bot.send_message(chat[0], message.text)
    await message.answer("Рассылка окончена!")
    await state.finish()

@dp.message_handler()
async def not_found( message:types.Message):
    await message.replay("Я вас не поняд введите /help")  

  
executor.start_polling(dp)