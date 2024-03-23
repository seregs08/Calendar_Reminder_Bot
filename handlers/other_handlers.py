from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards import start_keyboard
from utils import delete_current_and_previous_message as dm


router = Router()

@router.message()
async def other_message(msg: Message):
    await msg.answer(text='Извините, я вас не понимаю! Пожалуйста, выберите пункт в меню.', reply_markup=start_keyboard())
    await dm(msg)