from aiogram import Router, F, types
import os
import asyncio
import aiohttp
from aiogram.fsm.context import FSMContext
from tg_bot.keyboards import (get_base_add_panel, get_category_panel,
                       get_confirm_title_panel, get_title_fix_panel,
                       get_title_status_panel, get_watch_titles_panel,
                       get_open_title_panel, get_title_update_panel,
                       get_confirm_delete_panel)
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from tg_bot.utils import (push_to_history, delete_last, get_updated_title,
                          send_smart_message)
from datetime import datetime
from tg_bot.handlers.start import get_start_menu
from tg_bot.handlers.titles.add_titles import add_title_review
from typing import Union
from tg_bot.handlers.titles.add_titles import TitleState

router = Router()

all_titles = {}

async def get_all_titles(callback : types.CallbackQuery):
    url = "https://oddities.onrender.com/api/titles/title/"
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    titles = {}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                for item in data:
                    titles[str(item['id'])] = {
                        'name': f"{item['name']}",
                        'rating': f"{item['rating']}"
                    }
        except Exception as e:
            print(e)
    return dict(reversed(list(titles.items())))

async def get_title(event : Union[types.Message, types.CallbackQuery], title_id):
    url= f"https://oddities.onrender.com/api/titles/title/{title_id}/"
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(event.from_user.id),
        "Content-Type": "application/json"
    }
    title = {}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                title = await response.json()
        except Exception as e:
            print(e)

    text = (f"{title['name']}  {title['year_start']} | {title['category']}\n"
            f"rating - {title['rating']}\n\n"
            f"_____________________________________________________\n"
            f"{title['review']}\n"
            f"_____________________________________________________\n\n"
            )
    if title['director']:
        text += f"Director - {title['director']}\n"
    if title['start_watch']:
        text += f"Start watch - {title['start_watch']}\n"
    if title['end_watch']:
        text += f"End watch - {title['end_watch']}\n"
    if title['year_end']:
        text += f"End year - {title['year_end']}\n"
    if title['status']:
        text += f"Status - {title['status']}\n"

    data = {
        'title_data' : title,
        'title_text' : text,
    }
    return data

@router.callback_query(F.data == "open_titles")
async def watch_titles(callback : types.CallbackQuery, state : FSMContext ):
    await callback.answer()
    await push_to_history(state, 'TITLES_WATCH_MENU_PAGE_0')

    # https://unconsecutively-polyprotic-fay.ngrok-free.dev

    titles = await get_all_titles(callback)
    await state.update_data(titles_data=titles)
    #all_titles = titles
    await callback.message.edit_text("Watch Your Titles",
                                        reply_markup=get_watch_titles_panel(titles),
                                        parse_mode="HTML",
                                        disable_web_page_preview=True
                                        )


@router.callback_query(F.data.contains("open_titles_page_"))
async def response_next_titles_page(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[3])

    await push_to_history(state, f'TITLES_WATCH_MENU_PAGE_{page}')
    data = await state.get_data()
    titles = data.get('titles_data')

    await callback.message.edit_text(
        f"Page {page + 1}",
        reply_markup=get_watch_titles_panel(titles, page=page)
    )

@router.callback_query(F.data.contains('open_title_'))
async def watch_title(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    title_id = int(callback.data.split("_")[2])
    await state.update_data(title_id=title_id)
    page = int(callback.data.split("_")[4])
    await push_to_history(state, f'TITLES_WATCH_MENU_PAGE_{page}')
    title = await get_title(callback, title_id)
    data = await state.get_data()
    await state.update_data(title_data=title)
    await send_smart_message(callback.message, title['title_text'], get_open_title_panel(title_id))

@router.callback_query(F.data.contains('confirm_delete_title_'))
async def run_confirm_delete(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    title_id = int(callback.data.split('_')[3])
    await push_to_history(state, F"OPEN_TITLE_{title_id}")
    await callback.message.edit_text('Are You Sure?',
        reply_markup=get_confirm_delete_panel(title_id, 'title'))

@router.callback_query(F.data.contains('delete_title_'))
async def delete_title(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    title_id = int(callback.data.split('_')[2])
    url= f"https://oddities.onrender.com/api/titles/title/{title_id}/"
    data = await state.get_data()
    # это что бы удалить последний элемент из history и можно было делать back
    pages = [key for key in data['history'] if key.startswith('TITLES_WATCH_MENU_PAGE_')]
    page = int(pages[-1].split('_')[4])
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(url, headers=headers) as response:
                if response.status == 204:
                    await callback.message.edit_text('Title Have Deleted')
                    await asyncio.sleep(2)
                    await callback.message.edit_text(
                    f"Page {page}",
                        reply_markup=get_watch_titles_panel(await get_all_titles(callback), page=page)
                        )
                else:
                    print("status - ", response.status)
                    await callback.message.edit_text('delete error')
                    await asyncio.sleep(3)
                    await callback.message.edit_text(
                    f"Page {page}",
                        reply_markup=get_watch_titles_panel(await get_all_titles(callback), page=page)
                        )
        except Exception as e:
            print(e)

@router.callback_query(F.data.contains('panel_update_title_'))
async def run_update(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await state.update_data(is_update=True)
    title_id = int(callback.data.split('_')[3])
    await push_to_history(state, F"OPEN_TITLE_{title_id}")
    title_data = await get_updated_title(state)
    await send_smart_message(callback.message, title_data['text'], get_title_update_panel())

@router.callback_query(F.data.contains("update_title_"))
async def update_title(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    data = await state.get_data()
    history = data.get('history', [])
    history_item = f"TITLE_UPDATE_PANEL_{data['title_id']}"
    if not history[-1] == history_item:
        await push_to_history(state, history_item)

    updating = callback.data.split("_", 2)[2]
    if updating not in ['category', 'status']:
        await callback.message.answer(f'Write new {updating} for Title', reply_markup=get_base_add_panel())
        title_state = f'TitleState.waiting_for_{updating}'
        await state.set_state(eval(title_state))
    if updating == 'category':
        await callback.message.answer(f'Chose new category for Title', reply_markup=get_category_panel('title'))
    if updating == 'status':
        await callback.message.answer(f'Chose new status for Title', reply_markup=get_title_status_panel())

@router.callback_query(F.data == "save_updated_title")
async def save_updated_title (callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    data = await state.get_data()
    title_id = data.get('title_id')
    url = f"https://oddities.onrender.com/api/titles/title/{title_id}/"
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    title_data = await get_updated_title(state)
    updated = title_data['updated']

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(url, headers=headers, json=updated) as response:
                    if response.status in [200, 204]:
                        await callback.message.answer("updated")
                        await asyncio.sleep(0.5)
                        await delete_last(state)
                        title = await get_updated_title(state)
                        await send_smart_message(callback.message, title['text'], get_open_title_panel(title_id))
                    else:
                        await callback.message.answer(f"error {response.status}" )
                        #await callback.message.answer(f"{await response.json()}")
        except Exception as e:
            print(e)
