import os
import asyncio
import aiohttp
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from tg_bot.keyboards import (get_base_add_panel, get_category_panel,
                       get_confirm_title_panel, get_title_fix_panel,
                       get_title_status_panel, get_title_update_panel)
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from tg_bot.utils import (push_to_history, get_updated_title, delete_last,
                   delete_rated_item, get_title_text)
from datetime import datetime
from tg_bot.handlers.start import get_start_menu


router = Router()

class TitleState(StatesGroup):
    waiting_for_name = State()
    waiting_for_year_start = State()
    waiting_for_year_end = State()
    waiting_for_review = State()
    waiting_for_director = State()
    waiting_for_start_watch = State()
    waiting_for_end_watch = State()
    waiting_for_rating = State()


@router.callback_query(F.data == "add_title")
async def add_title(callback: types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await state.update_data(is_update=False)
    await state.update_data(is_was_item=False)
    await push_to_history(state, "START_MENU")
    await callback.message.edit_text("Chose the title category",
        reply_markup=get_category_panel('title'))

@router.callback_query(F.data.contains("title_category_"))
async def choose_title_category(callback: types.CallbackQuery, state : FSMContext):

    categories = {
        "title_category_movie" : "MV",
        "title_category_series" : "SR",
        "title_category_anime" : "ANM",
        "title_category_cartoon" : "CRT",
        "title_category_video" : "VD",
        "title_category_legal_case" : "LG",
        "title_category_written_content" : "READ",
        "title_category_other" : "OTHER"
    }

    await callback.answer()
    chosen_category = categories[f'{callback.data}']
    data = await state.get_data()
    is_update = data.get('is_update', False)
    await state.update_data(title_category=chosen_category)
    if is_update:
        await callback.message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await callback.message.answer(title_data['text'],reply_markup=get_title_update_panel())
        return
    await push_to_history(state, "TITLE_PANEL_ADD_CATEGORY")
    await state.set_state(TitleState.waiting_for_name)
    await callback.message.answer("Write the title's name",
        reply_markup=get_base_add_panel())

@router.message(TitleState.waiting_for_name)
async def add_title_name(message : types.Message, state : FSMContext):
    title_name = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    await state.update_data(title_name=title_name)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await message.answer(title_data['text'],reply_markup=get_title_update_panel())
        return
    else:
        await push_to_history(state, "TITLE_STATE_WAITING_FOR_NAME")
        await message.answer("Write title's start year", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_year_start)

@router.message(TitleState.waiting_for_year_start)
async def add_title_year_start(message : types.Message, state : FSMContext):
    title_year_start = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        Decimal(title_year_start)
    except Exception:
        await message.answer("write the correct year for example 1997", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_year_start)
        return
    await state.update_data(title_year_start=title_year_start)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await message.answer(title_data['text'], reply_markup=get_title_update_panel())
        return
    else:
        await push_to_history(state, "TITLE_STATE_WAITING_FOR_YEAR_START")
        await message.answer("Write the review for title", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_review)

@router.message(TitleState.waiting_for_review)
async def add_title_review(message : types.Message, state : FSMContext):
    data = await state.get_data()
    old_review = data.get('title_review', '')
    full_review = old_review + message.text
    await state.update_data(title_review=full_review)
    await asyncio.sleep(2)
    new_data = await state.get_data()
    if new_data.get('title_review') != full_review:
        return

    is_update = new_data.get('is_update', False)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await message.answer(title_data['text'], reply_markup=get_title_update_panel())
        return
    else:
        await push_to_history(state, "TITLE_STATE_WAITING_FOR_REVIEW")
        await message.answer("write the rating for title", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_rating)

@router.message(TitleState.waiting_for_rating)
async def add_title_rating(message : types.Message, state : FSMContext):
    title_rating = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        rating = Decimal(title_rating.replace(",", "."))
        min_rating = Decimal("0.5")
        max_rating = Decimal("10")
        if rating % Decimal("0.5") == 0 and rating >= min_rating and rating <= max_rating:
            pass
        else:
            raise
    except Exception:
        await message.answer("write the correct rating from 0.5 to 10, for example 7 or 7.5",
                            reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_rating)
        return

    await state.update_data(title_rating=title_rating)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await message.answer(title_data['text'], reply_markup=get_title_update_panel())
        return
    else:
        await push_to_history(state, "TITLE_STATE_WAITING_FOR_RATING")

        await message.answer("check", reply_markup=get_confirm_title_panel())

@router.callback_query(F.data == "title_confirm_panel_fix")
async def run_title_fix_panel(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "CONFIRM_TITLE_PANEL")
    await callback.message.edit_text("fix panel", reply_markup=get_title_fix_panel())

@router.callback_query(F.data == "title_confirm_panel_status")
async def show_title_status_panel(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "CONFIRM_TITLE_PANEL")
    await callback.message.edit_text("status panel", reply_markup=get_title_status_panel())

@router.callback_query(F.data.contains("title_status_panel_"))
async def choose_title_status(callback: types.CallbackQuery, state : FSMContext):
    chosen_status = callback.data
    await callback.answer()
    data = await state.get_data()
    is_update = data.get('is_update', False)
    await state.update_data(title_status=chosen_status)
    if is_update:
        await callback.message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await callback.message.answer(title_data['text'], reply_markup=get_title_update_panel())
        return
    else:
        await push_to_history(state, "TITLE_STATUS_PANEL")
        await callback.message.edit_text("check", reply_markup=get_confirm_title_panel())

@router.callback_query(F.data == "title_confirm_panel_start_watch")
async def run_add_title_start_watch(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "CONFIRM_TITLE_PANEL")
    await callback.message.answer("write date of start watch (for example 21.01.2026)",
                    reply_markup=get_base_add_panel())
    await state.set_state(TitleState.waiting_for_start_watch)

@router.message(TitleState.waiting_for_start_watch)
async def add_title_start_watch(message : types.Message, state : FSMContext):
    start_watch_date = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        correct_date = datetime.strptime(start_watch_date, "%d.%m.%Y").date()
        iso_date = correct_date.strftime("%Y-%m-%d")
        await state.update_data(title_start_watch=iso_date)
        if is_update:
            await message.answer("Save")
            await asyncio.sleep(0.5)
            await delete_last(state)
            title_data = await get_updated_title(state)
            await message.answer(title_data['text'], reply_markup=get_title_update_panel())
            return
        else:
            await push_to_history(state, "TITLE_STATE_WAITING_FOR_START_WATCH")
            await message.answer("check", reply_markup=get_confirm_title_panel())

    except Exception:
        await message.answer("write correct date dd.mm.yyyy for example 21.01.2026",
                    reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_start_watch)

@router.callback_query(F.data == "title_confirm_panel_end_watch")
async def run_add_title_end_watch(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "CONFIRM_TITLE_PANEL")
    await callback.message.answer("write date of end watch (for example 03.02.2026)",
                    reply_markup=get_base_add_panel())
    await state.set_state(TitleState.waiting_for_end_watch)

@router.message(TitleState.waiting_for_end_watch)
async def add_title_end_watch(message : types.Message, state : FSMContext):
    end_watch_date = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        correct_date = datetime.strptime(end_watch_date, "%d.%m.%Y").date()
        iso_date = correct_date.strftime("%Y-%m-%d")
        await state.update_data(title_end_watch=iso_date)
        if is_update:
            await message.answer("Save")
            await asyncio.sleep(0.5)
            await delete_last(state)
            title_data = await get_updated_title(state)
            await message.answer(title_data['text'], reply_markup=get_title_update_panel())
            return
        else:
            await push_to_history(state, "TITLE_STATE_WAITING_FOR_END_WATCH")

            await message.answer('check', reply_markup=get_confirm_title_panel())

    except Exception as e:
        print(e)
        await message.answer("write correct date dd.mm.yyyy for example 11.04.2026",
                    reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_end_watch)

@router.callback_query(F.data == "title_fix_panel_director")
async def run_add_title_director (callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "TITLE_CONFIRM_PANEL_FIX")
    await callback.message.edit_text("Write the name of Director", reply_markup=get_base_add_panel())
    await state.set_state(TitleState.waiting_for_director)

@router.message(TitleState.waiting_for_director)
async def add_title_director(message : types.Message, state : FSMContext):
    director = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    await state.update_data(title_director=director)
    if is_update:
        await message.answer("Save")
        await asyncio.sleep(0.5)
        await delete_last(state)
        title_data = await get_updated_title(state)
        await message.answer(title_data['text'], reply_markup=get_title_update_panel())
        return
    else:
        await push_to_history(state, "TITLE_CONFIRM_PANEL")
        await message.answer("fix panel", reply_markup=get_title_fix_panel())

@router.callback_query(F.data == "title_fix_panel_year_end")
async def run_add_title_year_end(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await push_to_history(state, "TITLE_CONFIRM_PANEL_FIX")
    await callback.message.edit_text("Write the title's end year",
                reply_markup=get_base_add_panel())
    await state.set_state(TitleState.waiting_for_year_end)

@router.message(TitleState.waiting_for_year_end)
async def add_title_year_end(message : types.Message, state : FSMContext):
    year_end = message.text
    data = await state.get_data()
    is_update = data.get('is_update', False)
    try:
        Decimal(year_end)
        await state.update_data(title_year_end=year_end)
        if is_update:
            await message.answer("Save")
            await asyncio.sleep(0.5)
            await delete_last(state)
            title_data = await get_updated_title(state)
            await message.answer(title_data['text'], reply_markup=get_title_update_panel())
            return
        else:
            await push_to_history(state, "TITLE_CONFIRM_PANEL")
            await message.answer("fix panel", reply_markup=get_title_fix_panel())
    except Exception:
        await message.answer("Write the correct title's end year for example 1997",
                                         reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_year_end)

@router.callback_query(F.data == "confirm_title_panel_save")
async def save_title(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()

    statuses = {
        "title_status_panel_DONE" : "DONE",
        "title_status_panel_DROPPED" : "DROP",
        "title_status_panel_REVISIT" : "RVS",
        "title_status_panel_WATCHING" : "WATCH"
    }

    state_data = await state.get_data()
    is_was_item = state_data.get('is_was_item', False)

    category = state_data['title_category']
    name = state_data['title_name']
    year_start = state_data['title_year_start']
    review = state_data['title_review']
    rating = state_data['title_rating']
    status = ""
    start_watch = ""
    end_watch = ""
    director = ""
    year_end = ""


    post_data = {
        "name": name,
        "year_start": int(year_start),
        #"year_end": year_end,
        "category": category,
        "review": review,
        "rating": rating
    }

    if 'title_status' in state_data:
        status = statuses[state_data['title_status']]
        post_data['status'] = status
    if 'title_start_watch' in state_data:
        date = datetime.strptime(str(state_data['title_start_watch']), '%d.%m.%Y').date()
        start_watch = date.strftime('%Y-%m-%d')
        post_data['start_watch'] = start_watch
    if 'title_end_watch' in state_data:
        date = datetime.strptime(str(state_data['title_end_watch']), '%d.%m.%Y').date()
        end_watch = date.strftime('%Y-%m-%d')
        post_data['end_watch'] = end_watch
    if 'title_director' in state_data:
        director = state_data['title_director']
        post_data['director'] = director
    if 'title_year_end' in state_data:
        year_end = int(state_data['title_year_end'])
        post_data['year_end'] = year_end

    url = "https://oddities.onrender.com/api/titles/title/"

    headers = {
        "X-Bot-Key" : str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id" : str(callback.from_user.id),
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=post_data) as response:
                if response.status in [200, 201]:
                    if is_was_item:
                        await delete_rated_item(callback, state)
                    await state.clear()
                    await callback.message.edit_text("Title Saved")
                    await asyncio.sleep(2)
                    await get_start_menu(callback)
                else:
                    await callback.message.answer(f"error {await response.json()}")
        except Exception:
            await callback.message.answer("error", reply_markup=get_confirm_title_panel())

