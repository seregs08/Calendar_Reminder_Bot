import logging
from logging.handlers import RotatingFileHandler
import asyncio

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from config.config_reader import config
from handlers import main_handlers, other_handlers
from middlewares import SchedulerMiddleware


async def bot_starting():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('logs/bot.log', maxBytes=5000000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    
    REDIS = {
    'host': '127.0.0.1',
    'port': '6379',
    'db': 0
    }

    job_stores = {
        'redis': RedisJobStore(**REDIS)
    }
    
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.configure(jobstores=job_stores)
    scheduler.start()
    
    dp.include_router(main_handlers.router)
    dp.include_router(other_handlers.router)
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    asyncio.run(bot_starting())