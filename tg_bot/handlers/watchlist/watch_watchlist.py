from aiogram import Router, F, types
import os
import asyncio
import aiohttp
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from tg_bot.keyboards import (get_base_add_panel, get_category_panel,
                        get_watchlist_confirm_panel,get_watch_watchlist_panel,
                        get_open_item_panel, get_confirm_delete_panel,
                        get_item_update_panel)
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from tg_bot.utils import push_to_history, delete_last, is_url_for_db, get_updated_item
from datetime import datetime
from tg_bot.handlers.start import get_start_menu
from typing import Union
from tg_bot.handlers.titles.add_titles import TitleState
from tg_bot.handlers.watchlist.add_watchlist import WatchlistState

router = Router()

async def get_all_items(callback : types.CallbackQuery):
    url = "http://127.0.0.1:8000/api/watchlist/item/"
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    items = {}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                for item in data:
                    items[str(item['id'])] = {
                        'name': f"{item['name']}",
                        'year_start': f"{item['year_start']}"
                    }
        except Exception as e:
            print(e)
    return dict(reversed(list(items.items())))

async def get_item(event : Union[types.Message, types.CallbackQuery], item_id):
    url = f"http://127.0.0.1:8000/api/watchlist/item/{item_id}/"
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(event.from_user.id),
        "Content-Type": "application/json"
    }
    item = {}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                item = await response.json()
        except Exception as e:
            print(e)


    text = f"{item['name']} |  {item.get('year_start')}  |  {item.get('category')}\n\n"

    if item['synopsis']:
        text += f"{item['synopsis']}\n\n"
    if item['director']:
        text += f"Director - {item['director']}\n"
    if item['year_end']:
        text += f"End Year - {item['year_end']}\n"
    if item['runtime']:
        text += f"Runtime - {item['runtime']}\n"
    if item['seasons']:
        text += f"Seasons - {item['director']}\n"
    if item['episodes']:
        text += f"Episodes - {item['episodes']}\n\n"
    if item['note']:
        text += f"Note - {item['note']}\n"
    if item['link']:
        text += f"Link - {item['link']}\n"

    # тут наверно надо сделать тему что в text вставялется доп инфа только если она есть
    # а если нет и не вставляется
    data = {
        'text' : text,
        'data' : item
    }
    return data


@router.callback_query(F.data == "open_watchlist")
async def watch_watchlist(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'WATCHLIST_WATCH_MENU_PAGE_0')

    items = await get_all_items(callback)
    await state.update_data(watchlist_data=items)
    # all_titles = titles
    await callback.message.edit_text("Watch Your Watchlist",
                                     reply_markup=get_watch_watchlist_panel(items),
                                     parse_mode="HTML",
                                     disable_web_page_preview=True
                                     )

@router.callback_query(F.data.contains("open_watchlist_page_"))
async def response_next_watchlist_page(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[3])

    await push_to_history(state, f'WATCHLIST_WATCH_MENU_PAGE_{page}')
    data = await state.get_data()
    items = data.get('watchlist_data')

    await callback.message.edit_text(
        f"Page {page + 1}",
        reply_markup=get_watch_watchlist_panel(items, page=page)
    )

@router.callback_query(F.data.contains("open_item_"))
async def open_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    item_id = int(callback.data.split("_")[2])
    await state.update_data(item_id=item_id)
    page = int(callback.data.split("_")[4])
    await push_to_history(state, f"WATCHLIST_WATCH_MENU_PAGE_{page}")
    item = await get_item(callback, item_id)
    await state.update_data(item_data=item)
    await callback.message.edit_text(item['text'], reply_markup=get_open_item_panel(item_id))

@router.callback_query(F.data.contains("confirm_delete_item_"))
async def confirm_delete_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    item_id = int(callback.data.split("_")[3])
    await push_to_history(state, f"OPEN_ITEM_{item_id}")
    await callback.message.edit_text('Are You Sure?',
        reply_markup=get_confirm_delete_panel(item_id, 'item'))

@router.callback_query(F.data.contains('delete_item_'))
async def delete_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    item_id = int(callback.data.split('_')[2])
    url= f"http://127.0.0.1:8000/api/watchlist/item/{item_id}/"
    data = await state.get_data()
    # это что бы удалить последний элемент из history и можно было делать back
    pages = [key for key in data['history'] if key.startswith('WATCHLIST_WATCH_MENU_PAGE_')]
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
                    await callback.message.edit_text('Item Have Deleted')
                    await asyncio.sleep(2)
                    await callback.message.edit_text(
                    f"Page {page}",
                        reply_markup=get_watch_watchlist_panel(await get_all_items(callback), page=page)
                        )
                else:
                    print("status - ", response.status)
                    await callback.message.edit_text('delete error')
                    await asyncio.sleep(2)
                    await callback.message.edit_text(
                    f"Page {page}",
                        reply_markup=get_watch_watchlist_panel(await get_all_items(callback), page=page)
                        )
        except Exception as e:
            print(e)

@router.callback_query(F.data.contains("panel_update_item_"))
async def run_update_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await state.update_data(is_update=True)
    item_id = int(callback.data.split("_")[3])
    await push_to_history(state, f"OPEN_ITEM_{item_id}")
    item = await get_updated_item(state)
    await callback.message.edit_text(item['text'], reply_markup=get_item_update_panel())

@router.callback_query(F.data.contains('rate_item_'))
async def rate_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    item_id = int(callback.data.split('_')[2])
    await state.update_data(is_update=False)
    await state.update_data(is_was_item=True)
    item = await get_updated_item(state)
    item_data = item['data']
    await state.update_data(title_category=item_data['category'])
    await state.update_data(title_name=item_data['name'])
    await state.update_data(title_year_start=item_data['year_start'])
    await callback.message.answer("Write the review for title", reply_markup=get_base_add_panel())
    await state.set_state(TitleState.waiting_for_review)

@router.callback_query(F.data.contains('update_item_'))
async def update_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    data = await state.get_data()
    history = data.get('history', [])
    history_item = f"ITEM_UPDATE_PANEL_{data['item_id']}"
    print('CHECK')
    if not history[-1] == history_item:
        print(history_item)
        print('GOOD')
        await push_to_history(state, history_item)
    print('FINISH')
    updating = callback.data.split("_", 2)[2]
    if updating != 'category':
        await callback.message.answer(f'Write new {updating} for Item', reply_markup=get_base_add_panel())
        watchlist_state = f'WatchlistState.waiting_for_{updating}'
        await state.set_state(eval(watchlist_state))
    if updating == 'category':
        await callback.message.answer(f'Chose new category for Item', reply_markup=get_category_panel('watchlist'))

@router.callback_query(F.data == 'save_updated_item')
async def save_updated_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    data = await state.get_data()
    item_id = data.get('item_id')
    url = f"http://127.0.0.1:8000/api/watchlist/item/{item_id}/"
    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    item_data = await get_updated_item(state)
    updated = item_data['updated']

    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(url, headers=headers, json=updated) as response:
                    if response.status in [200, 204]:
                        await callback.message.answer("updated")
                        await asyncio.sleep(0.5)
                        await delete_last(state)
                        item = await get_updated_item(state)
                        await callback.message.answer(item['text'], reply_markup=get_open_item_panel(item_id))
                    else:
                        await callback.message.answer(f"error {response.status}" )
                        #await callback.message.answer(f"{await response.json()}")
        except Exception as e:
            print(e)



