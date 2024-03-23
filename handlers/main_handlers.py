from datetime import date

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy import literal
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import (
    start_keyboard,
    reminder_keyboard,
    date_user_keyboard,
    date_edit_keyboard,
    date_user_reminder_keyboard,
    main_menu,
    checker,
    edit_reminder_time
)
from texts import command_text
from database import User, Date_users, session
from utils import delete_current_and_previous_message, send_reminder_message

router = Router()

class FSM_Modifer_Date(StatesGroup):
    add_date = State()
    choose_comment = State()
    delete_date = State()
    edit_date = State()
    show_date = State()
    

@router.message(CommandStart(), StateFilter(default_state))     #Обработка старта
async def start_handler(msg: Message):
    user_id_find = session.query(User).filter(User.tg_id == msg.from_user.id)
    user_exist_check = session.query(literal(True)).filter(user_id_find.exists()).scalar()
    if user_exist_check is None:
        session.add(User(tg_id=msg.from_user.id))
        session.commit()
    text = command_text.get('/start')(msg.from_user.full_name)
    await delete_current_and_previous_message(msg)
    await msg.answer(text, reply_markup=start_keyboard())
  
@router.callback_query(F.data == 'start')       #Старт = главное меню  
async def start_call(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='📌 Главное меню 📌', reply_markup=start_keyboard())
    await state.clear()

@router.callback_query(F.data == 'about')       #Справка
async def about_call(call: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    await call.message.edit_text(command_text.get('/about'), reply_markup=main_menu)
    await state.clear()
    apscheduler.print_jobs()
    print(apscheduler.get_jobs())
  
@router.callback_query(F.data == 'view_today')      #События (даты) на сегодня  
async def view_today_call(call: CallbackQuery, state: FSMContext):
    today = date.today().strftime('%d %m').split()
    user_id = session.query(User).filter(User.tg_id == call.from_user.id).first()
    date_user_check = session.query(Date_users).filter(Date_users.user_id == user_id.id,
                                                       Date_users.day == today[0],
                                                       Date_users.month == today[1])
    
    if date_user_check.first() is None:
        await call.message.edit_text(command_text['/view_today'].get('not_exist'), reply_markup=main_menu)
    else:
        await call.message.edit_text(command_text['/view_today'].get('exist') + '\n' + '\n'.join(
                                    [date_user.comment for date_user in date_user_check]
                                    ), reply_markup=main_menu)
    await state.clear()

@router.callback_query(F.data == 'add_date')        #Добавить событие (дату)
async def add_date_call(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(command_text['/add_date'].get('day'), reply_markup=reminder_keyboard('day'))
    await state.set_state(FSM_Modifer_Date.add_date)
    
@router.callback_query(FSM_Modifer_Date.add_date, F.data.startswith('day_'))        #Указываем день для добавления
async def add_day_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(user_id = session.query(User).filter(User.tg_id == call.from_user.id).first(),
                            day_ins = call.data.split('_')[1]
                            )
    await call.message.edit_text(command_text['/add_date'].get('month'), reply_markup=reminder_keyboard('month'))

@router.callback_query(FSM_Modifer_Date.add_date, F.data.startswith('month_'))      #Указываем месяц для добавления
async def add_month_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(month_ins = call.data.split('_')[1])
    await call.message.edit_text(command_text['/add_date'].get('comment'))
    await state.set_state(FSM_Modifer_Date.choose_comment)
    
@router.message(FSM_Modifer_Date.choose_comment)        #Получаем название события(даты)
async def add_comment_message(msg: Message, state: FSMContext):
    await state.update_data(comment_ins = msg.text)
    await delete_current_and_previous_message(msg)
    await msg.answer(command_text['/add_date'].get('reminder'), reply_markup=checker)
    await state.set_state(FSM_Modifer_Date.add_date)

@router.callback_query(FSM_Modifer_Date.add_date, F.data.startswith('checker_'))        #Проверка на уведомление для добавления
async def add_reminder_call(call: CallbackQuery, state: FSMContext):
    if call.data.split('_')[1] == 'yes':
        await state.update_data(rem_ins = True)
        await call.message.edit_text(command_text['/add_date'].get('hour'), reply_markup=reminder_keyboard('hour'))
    else:
        await call.message.edit_text(command_text['/add_date'].get('success'), reply_markup=main_menu)        
        user_data = await state.get_data()
        ins = Date_users(day = user_data['day_ins'], 
                        month = user_data['month_ins'],
                        comment = user_data['comment_ins'],
                        check_rem = False,
                        user_id = user_data['user_id'].id)
        session.add(ins)
        session.commit()
        await state.clear()
        
@router.callback_query(FSM_Modifer_Date.add_date, F.data.startswith('hour_'))       #Указываем часы для добавления
async def add_hour_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(hour_ins = call.data.split('_')[1])
    await call.message.edit_text(command_text['/add_date'].get('minute'), reply_markup=reminder_keyboard('minute'))
    
@router.callback_query(FSM_Modifer_Date.add_date, F.data.startswith('minute_'))     #Указываем минуты для добавления
async def add_minute_call(call: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    await state.update_data(minute_ins = call.data.split('_')[1])
    await call.message.edit_text(command_text['/add_date'].get('success'), reply_markup=main_menu)
    user_data = await state.get_data()
    ins = Date_users(day = user_data['day_ins'],
                    month = user_data['month_ins'],
                    comment = user_data['comment_ins'],
                    check_rem = user_data['rem_ins'],
                    hour_rem = user_data['hour_ins'],
                    minute_rem = user_data['minute_ins'],
                    user_id = user_data['user_id'].id)
    session.add(ins)
    session.commit()
    id_schedule = session.query(Date_users).filter(Date_users.day == user_data['day_ins'],
                    Date_users.month == user_data['month_ins'],
                    Date_users.comment == user_data['comment_ins'],
                    Date_users.check_rem == user_data['rem_ins'],
                    Date_users.hour_rem == user_data['hour_ins'],
                    Date_users.minute_rem == user_data['minute_ins'],
                    Date_users.user_id == user_data['user_id'].id).first()

    apscheduler.add_job(send_reminder_message,          #Создаем джоб на отправку уведомления о событии (дате)
                        id = str(id_schedule.id),
                        trigger='cron',
                        jobstore='redis',
                        day = user_data['day_ins'],
                        month = user_data['month_ins'],
                        hour = user_data['hour_ins'],
                        minute = user_data['minute_ins'],
                        year = '*',
                        kwargs={
                            'chat_id': call.message.chat.id,
                            'day': user_data['day_ins'],
                            'month': user_data['month_ins'],
                            'comment': user_data['comment_ins']
                        })
    await state.clear()    

@router.callback_query(F.data == 'view_date')       #Просмотр всех событий(дат)
async def view_date_call(call: CallbackQuery, state: FSMContext):
    user_id = session.query(User).filter(User.tg_id == call.from_user.id).first()
    date_user = session.query(Date_users).filter(Date_users.user_id == user_id.id)
    
    if date_user.first() is None:
        await call.message.edit_text(command_text['/view_date'].get('not_exist'), reply_markup=main_menu)
    else:
        await call.message.edit_text(command_text['/view_date'].get('exist'), reply_markup=date_user_keyboard(date_user))
        await state.set_state(FSM_Modifer_Date.show_date)
        await state.update_data(d_user = date_user)

@router.callback_query(FSM_Modifer_Date.show_date)      #Просмотр уведомлений(вкл/выкл) по конкретному событию(дате)
async def show_date_call(call: CallbackQuery, state: FSMContext):
    date_user_state = await state.get_data()
    date_user = date_user_state['d_user'].filter(Date_users.id == call.data.split('_')[3])
    await call.message.edit_text(text='🔔 Напоминание:', reply_markup=date_user_reminder_keyboard(date_user))
    await state.clear()   

@router.callback_query(F.data.startswith('modify_date_'))       #Редактирование событий(дат)
async def modify_date_check_call(call: CallbackQuery, state: FSMContext):
    user_id = session.query(User).filter(User.tg_id == call.from_user.id).first()
    date_user = session.query(Date_users).filter(Date_users.user_id == user_id.id)
    
    if date_user.first() is None:
        await call.message.edit_text(command_text['/view_date'].get('not_exist'), reply_markup=main_menu)
    elif call.data.split('_')[2] == 'delete':        
        await call.message.edit_text(command_text['/delete_date'].get('choose'), reply_markup=date_user_keyboard(date_user))
        await state.set_state(FSM_Modifer_Date.delete_date)
    else:
        await call.message.edit_text(command_text['/edit_date'].get('choose'), reply_markup=date_user_keyboard(date_user))
        await state.set_state(FSM_Modifer_Date.edit_date)

@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('date_user_id_'))
async def edit_date_choose_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(edit_id = call.data.split('_')[3])
    await call.message.edit_text(text='Какие данные необходимо изменить?', reply_markup=date_edit_keyboard())
    
@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('edit_'))
async def edit_date_call(call: CallbackQuery):
    call_data = call.data.split('_')[1]
    match call_data:
        case 'date':
            await call.message.edit_text(command_text['/add_date'].get('day'), reply_markup=reminder_keyboard('day'))
        case 'comment':
            await call.message.edit_text(text='Введите новое название события:')
        case 'reminder':
            await call.message.edit_text(text='Включить напоминание?', reply_markup=checker)
        case 'time':
            await call.message.edit_text(command_text['/add_date'].get('hour'), reply_markup=reminder_keyboard('hour'))
        case _:
            print('Match_case edit no understand')
            
@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('day_'))       #Редактируем день
async def edit_day_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(day_ins = call.data.split('_')[1])
    await call.message.edit_text(command_text['/add_date'].get('month'), reply_markup=reminder_keyboard('month'))
    
@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('month_'))     #Редактируем месяц
async def edit_month_call(call: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    await state.update_data(month_ins = call.data.split('_')[1])
    await call.message.edit_text(command_text['/edit_date'].get('success'), reply_markup=main_menu)        
    user_data = await state.get_data()
    ins = session.query(Date_users).get(user_data['edit_id'])
    ins.day = user_data['day_ins']
    ins.month = user_data['month_ins']
    session.add(ins)
    session.commit()
    
    if ins.check_rem:       #Если включены уведомления, переписываем их джобу        
        schedule_data = session.query(Date_users).filter(Date_users.id == user_data['edit_id']).first()
        apscheduler.remove_job(job_id=user_data['edit_id'])
        apscheduler.add_job(send_reminder_message,
                        id = user_data['edit_id'],
                        trigger='cron',
                        jobstore='redis',
                        day = user_data['day_ins'],
                        month = user_data['month_ins'],
                        hour = schedule_data.hour_rem,
                        minute = schedule_data.minute_rem,
                        year = '*',
                        kwargs={
                            'chat_id': call.message.chat.id,
                            'day': user_data['day_ins'],
                            'month': user_data['month_ins'],
                            'comment': schedule_data.comment
                        })                                          
    await state.clear()

@router.message(FSM_Modifer_Date.edit_date)     #Редактируем название события(даты)
async def edit_comment_message(msg: Message, state: FSMContext, apscheduler: AsyncIOScheduler):
    await state.update_data(comment_ins = msg.text)
    await delete_current_and_previous_message(msg)
    await msg.answer(command_text['/edit_date'].get('success'), reply_markup=main_menu)
    user_data = await state.get_data()
    ins = session.query(Date_users).get(user_data['edit_id'])
    ins.comment = user_data['comment_ins']
    session.add(ins)
    session.commit()
    
    if ins.check_rem:       #Если включены уведомления, переписываем их джобу             
        schedule_data = session.query(Date_users).filter(Date_users.id == user_data['edit_id']).first()
        apscheduler.remove_job(job_id=user_data['edit_id'])
        apscheduler.add_job(send_reminder_message,
                        id = user_data['edit_id'],
                        trigger='cron',
                        jobstore='redis',
                        day = schedule_data.day,
                        month = schedule_data.month,
                        hour = schedule_data.hour_rem,
                        minute = schedule_data.minute_rem,
                        year = '*',
                        kwargs={
                            'chat_id': msg.chat.id,
                            'day': schedule_data.day,
                            'month': schedule_data.month,
                            'comment': user_data['comment_ins']
                        })
    await state.clear()  

@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('checker_'))       #Редактируем уведомления
async def edit_reminder_call(call: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    user_data = await state.get_data()
    edit_id_check_rem = session.query(Date_users).filter(Date_users.id == user_data['edit_id']).first()
    answer_checker = call.data.split('_')[1]
    
    if edit_id_check_rem.check_rem and answer_checker == 'yes':
        await call.message.edit_text(text='Напоминание уже включено', reply_markup=edit_reminder_time)
    elif not edit_id_check_rem.check_rem and answer_checker == 'no':
        await call.message.edit_text(text='Напоминание уже отключено', reply_markup=main_menu)
        await state.clear() 
    elif edit_id_check_rem.check_rem and answer_checker == 'no':
        ins = session.query(Date_users).get(user_data['edit_id'])
        apscheduler.remove_job(user_data['edit_id'])
        ins.check_rem = False
        await call.message.edit_text(text='Напоминание отключено', reply_markup=main_menu)
        session.add(ins)
        session.commit()
        await state.clear() 
    else:
        await call.message.edit_text(command_text['/add_date'].get('hour'), reply_markup=reminder_keyboard('hour'))

@router.callback_query(F.data == 'ed_rem_time')     #Редактируем время уведомления
async def edit_reminder_time_call(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(command_text['/add_date'].get('hour'), reply_markup=reminder_keyboard('hour'))
    

@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('hour_'))      #Редактируем часы
async def edit_hour_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(hour_ins = call.data.split('_')[1])
    await call.message.edit_text(command_text['/add_date'].get('minute'), reply_markup=reminder_keyboard('minute'))
    
@router.callback_query(FSM_Modifer_Date.edit_date, F.data.startswith('minute_'))        #Редактируем минуты
async def edit_minute_call(call: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    await state.update_data(minute_ins = call.data.split('_')[1])
    await call.message.edit_text(text='Напоминание включено!', reply_markup=main_menu)
    user_data = await state.get_data()
    ins = session.query(Date_users).get(user_data['edit_id'])
    schedule_data = session.query(Date_users).filter(Date_users.id == user_data['edit_id']).first()
    ins.hour_rem = user_data['hour_ins']
    ins.minute_rem = user_data['minute_ins']
    session.add(ins)
    session.commit()    
    if ins.check_rem:       #Если были включены уведомления, удаляем джобу        
        apscheduler.remove_job(job_id=user_data['edit_id'])
    ins.check_rem = True
    apscheduler.add_job(send_reminder_message,      #Создаем джобу
                    id = user_data['edit_id'],
                    trigger='cron',
                    jobstore='redis',
                    day = schedule_data.day,
                    month = schedule_data.month,
                    hour = user_data['hour_ins'],
                    minute = user_data['minute_ins'],
                    year = '*',
                    kwargs={
                        'chat_id': call.message.chat.id,
                        'day': schedule_data.day,
                        'month': schedule_data.month,
                        'comment': schedule_data.comment
                    })
    await state.clear()    
    
    

@router.callback_query(FSM_Modifer_Date.delete_date, F.data.startswith('date_user_id_'))        #Удаляем событие(дату) (первый запрос с получением id даты)
async def delete_date_approve_call(call: CallbackQuery, state: FSMContext):
    await state.update_data(del_id = call.data.split('_')[3])
    await call.message.edit_text(text='Вы уверены?', reply_markup=checker)

@router.callback_query(FSM_Modifer_Date.delete_date, F.data.startswith('checker_'))         #Удаляем событие(дату), подтверждение
async def delete_date_call(call: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    if call.data.split('_')[1] == 'yes':
        date_id = await state.get_data()
        del_date_id = session.query(Date_users).filter(Date_users.id == date_id['del_id']).one()
        if del_date_id.check_rem:
            apscheduler.remove_job(str(del_date_id.id))
        await call.message.edit_text(command_text['/delete_date'].get('success'), reply_markup=main_menu)
        session.delete(del_date_id)
        session.commit()  
    else:
        await call.message.edit_text(text='Событие не удалялось', reply_markup=main_menu)
    await state.clear()  