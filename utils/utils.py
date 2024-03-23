from aiogram import Bot

from config.config_reader import config
from keyboards import start_keyboard


bot = Bot(token=config.bot_token.get_secret_value())

async def delete_current_and_previous_message(msg):
    try:
        await msg.delete()
        await bot.delete_message(
            chat_id=msg.chat.id, message_id=msg.message_id-1
            )
    except Exception as ex:
        print('Exc:', ex)
        pass
    
async def send_reminder_message(chat_id: int, day: str, month: str, comment: list[str]):
        msg = await bot.send_message(chat_id, f'Напоминание!\nСегодня {day}.{month} в твоем календаре есть важное событие:\n{comment}', reply_markup=start_keyboard())
        await bot.delete_message(chat_id, message_id=msg.message_id - 1)