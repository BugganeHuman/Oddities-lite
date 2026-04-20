import os
import asyncio
import aiohttp
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from tg_bot.keyboards import (get_base_add_panel, get_category_panel,
                        get_watchlist_confirm_panel, get_item_update_panel,
                        get_account_actions_panel, get_toggle_visibility_panel,
                        get_confirm_delete_user_panel)
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from tg_bot.utils import push_to_history, delete_last, is_url_for_db, get_updated_item
from datetime import datetime
from tg_bot.handlers.start import get_start_menu
import sqlite3


router = Router()

@router.callback_query(F.data == "account_actions")
async def show_account_actions(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "START_MENU")
    await callback.message.edit_text('Account actions', reply_markup=get_account_actions_panel())

@router.callback_query(F.data == "user_me")
async def show_user_info(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'SHOW_ACCOUNT_ACTIONS')

    url = "https://oddities.onrender.com/api/users/me/"

    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(callback.from_user.id),
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    date_var = datetime.fromisoformat(data['date_joined'].replace('Z', '+00:00'))
                    date = date_var.strftime('%d.%m.%Y')
                    text = (f"ID - {data['id']}\n\n"
                            f"Username - {data['username']}\n\n"
                            f"Date joined - {date}")
                    await callback.message.edit_text(str(text), reply_markup=get_base_add_panel())
        except Exception as e:
            print(e)

@router.callback_query(F.data == "user_show_password")
async def show_password(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'SHOW_ACCOUNT_ACTIONS')
    user_id = callback.from_user.id
    CONN = sqlite3.connect("tg_bot/bot_db/tg_db.sqlite3")
    CURSOR = CONN.cursor()
    CURSOR.execute("SELECT password FROM users WHERE user_id = ?;", (user_id, ))
    data = CURSOR.fetchone()
    password = data[0]
    await callback.message.edit_text(f"<tg-spoiler><code>{password}</code></tg-spoiler>",
                                        parse_mode='HTML', reply_markup=get_base_add_panel())

@router.callback_query(F.data == 'user_toggle_visibility')
async def show_toggle_visibility(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'SHOW_ACCOUNT_ACTIONS')
    url = 'https://oddities.onrender.com/api/users/get_user_visibility/'
    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    text = (f"Titles is public - {data['titles_is_public']}\n\n"
                            f"Watchlist is public - {data['watchlist_is_public']}")
                    await callback.message.edit_text(text, reply_markup=get_toggle_visibility_panel() )
        except Exception as e:
            print(e)

@router.callback_query(F.data.contains('toggle_visibility_'))
async def toggle_visibility(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    kind = callback.data.split('_')[2]
    visibility = callback.data.split('_')[3]
    if kind == 'titles':
        await state.update_data(titles_visibility=visibility)
    elif kind == 'watchlist':
        await state.update_data(watchlist_visibility=visibility)
    await callback.message.answer(f'Changed {kind} = {visibility}')

@router.callback_query(F.data == "save_updated_visibility")
async def save_toggle_visibility(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    url = 'https://oddities.onrender.com/api/users/toggle_visibility/'
    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    data = await state.get_data()
    titles_visibility = data.get('titles_visibility', '')
    watchlist_visibility = data.get('watchlist_visibility', '')

    put_data = {
    }
    if titles_visibility:
        print(titles_visibility)
        put_data['titles_visibility'] = titles_visibility
    if watchlist_visibility:
        put_data['watchlist_visibility'] = watchlist_visibility

    async with aiohttp.ClientSession() as session:
        try:
            async with session.put(url, headers=headers, json=put_data) as response:
                if response.status in [200, 204, 201]:
                    await callback.message.answer('Done', reply_markup=get_base_add_panel())
        except Exception as e:
            print(e)

@router.callback_query(F.data == 'user_delete_account')
async def show_confirm_delete_account(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'SHOW_ACCOUNT_ACTIONS')
    await callback.message.edit_text('Are you sure to delete you account?',
                                reply_markup=get_confirm_delete_user_panel())

@router.callback_query(F.data == 'delete_user')
async def delete_account(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    url = 'https://oddities.onrender.com/api/users/hard_delete_user/'
    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(url, headers=headers) as response:
                await callback.message.answer('Your fucking account was deleted, fuck u and never come again')
                await state.clear()
        except Exception as e:
            print(e)