from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_keyboard():
    btn_0 = InlineKeyboardButton(text='📋 Просмотреть события на сегодня', callback_data='view_today')
    btn_1 = InlineKeyboardButton(text='➕ Добавить дату', callback_data='add_date')
    btn_2 = InlineKeyboardButton(text='🔎 Просмотреть мои даты', callback_data='view_date')
    btn_3 = InlineKeyboardButton(text='✏️ Редактировать даты (изменить, вкл/выкл уведомления)', callback_data='modify_date_edit')
    btn_4 = InlineKeyboardButton(text='✖️ Удалить дату', callback_data='modify_date_delete')
    btn_5 = InlineKeyboardButton(text='❓ Справка', callback_data='about')
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_0],
            [btn_1],
            [btn_2],
            [btn_3],
            [btn_4],
            [btn_5]
        ]
    )
    return keyboard

def reminder_keyboard(param: str):
    rng = {
        'day': range(1, 32),
        'month': range(1, 13),
        'hour': range(24),
        'minute': range(60)
    }
    
    btn = [
        InlineKeyboardButton(text=str(txt).rjust(2, '0'), callback_data=param + '_' + str(txt).rjust(2, '0'))
        for txt in rng[param]
    ]
    btn.append(InlineKeyboardButton(text='📌 Главное меню 📌', callback_data='start'))
    
    return InlineKeyboardBuilder().row(*btn, width=5).as_markup()

def date_user_keyboard(date_user):
    btn = [
        InlineKeyboardButton(text=f"📆 Дата: {d_u.day}.{d_u.month}  📋Событие: {d_u.comment}",
                             callback_data='date_user_id_' + str(d_u.id))
        for d_u in date_user
    ]
    btn.append(InlineKeyboardButton(text='📌 Главное меню 📌', callback_data='start'))
    
    return InlineKeyboardBuilder().row(*btn, width=1).as_markup()
        
def date_edit_keyboard():
    btn_0 = InlineKeyboardButton(text='📆 Дата', callback_data='edit_date')
    btn_2 = InlineKeyboardButton(text='📋 Событие', callback_data='edit_comment')
    btn_1 = InlineKeyboardButton(text='🔔 Напоминание', callback_data='edit_reminder')
    btn_3 = InlineKeyboardButton(text='🕓 Время напоминания', callback_data='edit_time')
    btn_4 = InlineKeyboardButton(text='📌 Главное меню 📌', callback_data='start')
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_0],
            [btn_1],
            [btn_2],
            [btn_3],
            [btn_4]
        ]
    )
    return keyboard
    
def date_user_reminder_keyboard(date_user):
    btn = [
        InlineKeyboardButton(text=f"{['❌ Отключено', '✅'][d_u.check_rem]} {['', f'🕓Время: {d_u.hour_rem}:{d_u.minute_rem}'][d_u.check_rem]}",
                             callback_data='date_user_id_' + str(d_u.id))
        for d_u in date_user
    ]
    btn.append(InlineKeyboardButton(text='📌 Главное меню 📌', callback_data='start'))
    return InlineKeyboardBuilder().row(*btn, width=1).as_markup()

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📌 Главное меню 📌', callback_data='start')]
    ]
)

checker = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✅ Да', callback_data='checker_yes')],
        [InlineKeyboardButton(text='✖️ Нет', callback_data='checker_no')]
    ]
)

edit_reminder_time = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✏️ Изменить время уведомления', callback_data='ed_rem_time')],
        [InlineKeyboardButton(text='📌 Главное меню 📌', callback_data='start')]
    ]
)
