import asyncio
import logging
import base64
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import Message
from openai import AsyncOpenAI
from PIL import Image
import io
import os
from dotenv import load_dotenv
from config import Config
from image_processor import optimize_image
from user_manager import UserManager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# Инициализация клиента OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Инициализация менеджера пользователей
user_manager = UserManager()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_manager.add_user(user_id)
    await message.answer("Привет! Отправь мне фото еды, и я подсчитаю калории.")

# Обработчик фотографий
@dp.message(F.photo)
async def process_photo(message: Message):
    user_id = message.from_user.id
    if not user_manager.can_use_service(user_id):
        await message.answer("Вы достигли лимита использования на сегодня. Попробуйте завтра!")
        return

    try:
        # Получаем фото
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Скачиваем фото
        downloaded_file = await bot.download_file(file_path)
        
        # Оптимизируем фото
        optimized_image = optimize_image(Image.open(io.BytesIO(downloaded_file.read())))
        
        # Конвертируем оптимизированное изображение в base64
        buffered = io.BytesIO()
        optimized_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Отправляем запрос в ChatGPT
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Опиши это блюдо и подсчитай примерное количество калорий. Также предложи более здоровую альтернативу, если это возможно."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        # Отправляем ответ пользователю
        await message.reply(response.choices[0].message.content)
        
        # Обновляем статистику использования
        user_manager.increment_usage(user_id)
    
    except Exception as e:
        logging.error(f"Error processing photo: {e}")
        await message.reply("Произошла ошибка при обработке фотографии. Пожалуйста, попробуйте еще раз позже.")

# Обработчик текстовых сообщений
@dp.message()
async def echo(message: Message):
    await message.answer("Пожалуйста, отправьте фото еды.")

# Функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())