import json

from aiogram import Router, F, types
import secrets
import sqlite3
from aiogram.filters import Command
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from tg_bot.keyboards import (get_start_panel, get_confirm_title_panel,
                        get_home_btn_panel)
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
import os
import asyncio


router = Router()


CONN = sqlite3.connect("tg_bot/bot_db/tg_db.sqlite3", check_same_thread=False)

CURSOR = CONN.cursor()

CURSOR.execute("""CREATE TABLE IF NOT EXISTS users (
               user_id INTEGER,
               password TEXT NOT NULL,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP
               );""")


async def get_start_menu(event):

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text("Welcome to Oddities, bot for help you with content",
                reply_markup=get_start_panel())
    if isinstance(event, types.Message):
        await event.answer("Welcome to Oddities, bot for help you with content", reply_markup=get_start_panel(),
        )

    #await message.answer("Welcome to Oddities, bot for help you with content", reply_markup=get_start_panel(),
        #parse_mode="Markdown")


@router.message(Command("start"))
async def start(message: types.Message):
    url = "http://127.0.0.1:8000/api/users/register/"

    user_password = secrets.token_hex(16)
    user_id = message.from_user.id

    CURSOR.execute("INSERT INTO users (user_id, password) VALUES (?, ?)",
            (user_id, user_password))

    CONN.commit()
    data = {
        "username" : message.from_user.username,
        "telegram_id" : user_id,
        "password" : user_password,
        "email" : f"user_{user_id}@oddities.com"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status in [200, 201]:
                await get_start_menu(message)
            elif response.status in [400, 409]:
                await get_start_menu(message)
            else:
                await message.answer(f"error in register ")

@router.message(Command('backup'))
async def backup(message : types.Message):
    url = 'http://web:8000/api/backup/'
    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(message.from_user.id),
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    json_string = json.dumps(data, indent=4, ensure_ascii=False)
                    json_bytes = json_string.encode('utf-8')
                    file = BufferedInputFile(json_bytes,
                        filename=f'oddities_backup_{message.from_user.username}.json')
                    await message.answer_document(file, caption='Your Backup')
                    await asyncio.sleep(3)
                    await message.answer("Welcome to Oddities, bot for help you with content",
                                            reply_markup=get_start_panel(),)
        except Exception as e:
            print(e)