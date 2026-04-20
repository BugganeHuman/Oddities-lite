import os
import asyncio
import aiohttp
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from tg_bot.keyboards import (get_base_add_panel, get_category_panel,
                        get_watchlist_confirm_panel, get_item_update_panel)
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from tg_bot.utils import push_to_history, delete_last, is_url_for_db, get_updated_item
from datetime import datetime
from tg_bot.handlers.start import get_start_menu

router = Router()

class WatchlistState(StatesGroup):
    waiting_for_name = State()
    waiting_for_year_start = State()
    waiting_for_year_end = State()
    waiting_for_link = State()
    waiting_for_director = State()
    waiting_for_note = State()
    waiting_for_synopsis = State()
    waiting_for_runtime = State()
    waiting_for_episodes = State()
    waiting_for_seasons = State()

@router.callback_query(F.data == "add_watchlist_item")
async def add_watchlist_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await state.update_data(is_update=False)
    await push_to_history(state, "START_MENU")
    await callback.message.edit_text("Chose the item's category", reply_markup=get_category_panel('watchlist'))

@router.callback_query(F.data.contains('watchlist_category_'))
async def choose_item_category(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    categories = {
        "watchlist_category_movie" : "MV",
        "watchlist_category_series" : "SR",
        "watchlist_category_anime" : "ANM",
        "watchlist_category_cartoon" : "CRT",
        "watchlist_category_video" : "VD",
        "watchlist_category_legal_case" : "LG",
        "watchlist_category_written_content" : "READ",
        "watchlist_category_other" : "OTHER"
    }
    chosen_category = categories.get(callback.data, "OTHER")
    await state.update_data(item_category=chosen_category)
    data = await state.get_data()
    is_update = data.get('is_update', False)
    if is_update:
        await callback.message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await callback.message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return

    else:
        await push_to_history(state, 'WATCHLIST_PANEL_ADD_CATEGORY')
        await state.set_state(WatchlistState.waiting_for_name)
        await callback.message.answer("Write the item's name",
            reply_markup=get_base_add_panel())

@router.message(WatchlistState.waiting_for_name)
async def add_item_name(message : types.Message, state : FSMContext):
    item_name = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    await state.update_data(item_name=item_name)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        await push_to_history(state, 'WATCHLIST_STATE_WAITING_FOR_NAME')
        await message.answer("Write the start year of item",
                reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_year_start)

@router.message(WatchlistState.waiting_for_year_start)
async def add_item_year_start(message : types.Message, state : FSMContext):
    year_start = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        Decimal(year_start)
    except Exception:
        await message.answer('Write the correct year for example 1997', reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_year_start)
        return
    await state.update_data(item_year_start=year_start)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        await push_to_history(state, 'WATCHLIST_STATE_WAITING_FOR_YEAR_START')
        await message.answer('confirm panel', reply_markup=get_watchlist_confirm_panel())

@router.callback_query(F.data == "watchlist_confirm_panel_link")
async def run_add_item_link(callback : types.CallbackQuery,  state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'WATCHLIST_CONFIRM_PANEL')
    await callback.message.answer("Write the item's link", reply_markup=get_base_add_panel())
    await state.set_state(WatchlistState.waiting_for_link)

@router.message(WatchlistState.waiting_for_link)
async def add_item_link(message : types.Message, state : FSMContext):
    link = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    is_link_correct = is_url_for_db(link)
    if not is_link_correct:
        await message.answer('Write the correct link, for example'
            ' https://www.imdb.com/title/tt0246578/?ref_=rt_t_2',
            reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_link)
        return
    else:
        await state.update_data(item_link=link)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        await push_to_history(state, 'WATCHLIST_STATE_WAITING_FOR_LINK')
        await message.answer("confirm panel", reply_markup=get_watchlist_confirm_panel())

@router.callback_query(F.data == "watchlist_confirm_panel_note")
async def run_add_item_note(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'WATCHLIST_CONFIRM_PANEL')
    await callback.message.answer("Write your note", reply_markup=get_base_add_panel())
    await state.set_state(WatchlistState.waiting_for_note)

@router.message(WatchlistState.waiting_for_note)
async def add_item_note(message :  types.Message, state : FSMContext):
    note = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    if len(note) > 500:
        await message.answer("Write your note, max length = 500",
                reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_note)
        return
    else:
        await state.update_data(item_note=note)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        await push_to_history(state, "WATCHLIST_STATE_WAITING_FOR_NOTE")
        await message.answer("confirm panel", reply_markup=get_watchlist_confirm_panel())

@router.callback_query(F.data == "watchlist_confirm_panel_year_end")
async def run_add_item_year_end(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "WATCHLIST_CONFIRM_PANEL")
    await callback.message.answer("Write the item's end year",
                reply_markup=get_base_add_panel())
    await state.set_state(WatchlistState.waiting_for_year_end)

@router.message(WatchlistState.waiting_for_year_end)
async def add_item_year_end(message : types.Message, state : FSMContext):
    year_end = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        Decimal(year_end)
    except Exception:
        await message.answer("Write the correct end year for example 2005",
                                reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_year_end)
        return
    await state.update_data(item_year_end=year_end)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        await push_to_history(state, 'WATCHLIST_STATE_WAITING_FOR_YEAR_END')
        await message.answer("confirm panel", reply_markup=get_watchlist_confirm_panel())

@router.callback_query(F.data == "watchlist_confirm_panel_director")
async def run_add_item_director(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, 'WATCHLIST_CONFIRM_PANEL')
    await callback.message.answer("Write the item's Director", reply_markup=get_base_add_panel())
    await state.set_state(WatchlistState.waiting_for_director)

@router.message(WatchlistState.waiting_for_director)
async def add_item_director(message : types.Message, state : FSMContext):
    director = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    if len(director) > 150:
        await message.answer("Write the item's Director, max length = 150",
                            reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_director)
        return
    await state.update_data(item_director=director)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        await push_to_history(state, "WATCHLIST_STATE_WAITING_FOR_DIRECTOR")
        await message.answer("confirm panel", reply_markup=get_watchlist_confirm_panel())

@router.message(WatchlistState.waiting_for_synopsis)
async def add_item_synopsis(message : types.Message, state : FSMContext):
    synopsis = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    if len(synopsis) > 2000:
        await message.answer("Write the item's Synopsis, max length = 2000",
                            reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_synopsis)
        return
    await state.update_data(item_synopsis=synopsis)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        pass

@router.message(WatchlistState.waiting_for_runtime)
async def add_item_runtime(message : types.Message, state : FSMContext):
    runtime = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        if int(runtime) % 1 != 0:
            await message.answer("Write the item's runtime for example 90 ",
                                reply_markup=get_base_add_panel())
            await state.set_state(WatchlistState.waiting_for_runtime)
            return
    except Exception:
        await message.answer("Write the item's runtime for example 90 ",
                             reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_runtime)
        return
    await state.update_data(item_runtime=int(runtime))
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        pass


@router.message(WatchlistState.waiting_for_episodes)
async def add_title_episodes(message : types.Message, state : FSMContext):
    episodes = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        if int(episodes) % 1 != 0:
            await message.answer("Write the item's amount of episodes for example 10 ",
                                reply_markup=get_base_add_panel())
            await state.set_state(WatchlistState.waiting_for_episodes)
            return
    except Exception:
        await message.answer("Write the item's amount of episodes for example 10 ",
                            reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_episodes)
        return
    await state.update_data(item_episodes=int(episodes))
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        pass

@router.message(WatchlistState.waiting_for_seasons)
async def add_title_seasons(message : types.Message, state : FSMContext):
    seasons = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        if int(seasons) % 1 != 0:
            await message.answer("Write the item's amount of seasons for example 7 ",
                                reply_markup=get_base_add_panel())
            await state.set_state(WatchlistState.waiting_for_seasons)
            return
    except Exception:
        await message.answer("Write the item's amount of seasons for example 7 ",
                             reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_seasons)
        return
    await state.update_data(item_seasons=int(seasons))
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        item_data = await get_updated_item(state)
        await message.answer(item_data['text'], reply_markup=get_item_update_panel())
        return
    else:
        pass

@router.callback_query(F.data == "confirm_watchlist_panel_save")
async def save_item(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    state_data = await state.get_data()
    category = state_data.get('item_category')
    name = state_data.get('item_name')
    year_start = state_data.get('item_year_start')
    note = ""
    link = ""
    year_end = ""
    director = ""

    post_data = {
        'name' : name,
        'category' : category,
        'year_start' : year_start
    }

    if 'item_note' in state_data:
        note = state_data.get('item_note')
        post_data['note'] = note
    if 'item_link' in state_data:
        link = state_data.get('item_link')
        post_data['link'] = link
    if 'item_year_end' in state_data:
        year_end = state_data.get('item_year_end')
        post_data['year_end'] = year_end
    if 'item_director' in state_data:
        director = state_data.get('item_director')
        post_data['director'] = director

    url = "https://oddities.onrender.com/api/watchlist/item/"

    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(callback.from_user.id),
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=post_data) as response:
                if response.status in [200, 201]:
                    await state.clear()
                    await callback.message.edit_text("Item Saved")
                    await asyncio.sleep(1)
                    await get_start_menu(callback)
                else:
                    await callback.message.answer(f"error {response.status}")
        except Exception as e:
            print("======DEBUG========")
            print(e)