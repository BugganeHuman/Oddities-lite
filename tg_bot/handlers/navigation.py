from aiogram import Router, F, types
from aiogram.filters import Command
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from tg_bot.keyboards import (get_start_panel, get_confirm_title_panel,
                       get_title_status_panel, get_title_update_panel,
                       get_item_update_panel)
from aiogram.fsm.state import StatesGroup, State
from tg_bot.handlers.start import get_start_menu
from tg_bot.handlers.titles.add_titles import add_title
from tg_bot.handlers.titles.add_titles import TitleState
from tg_bot.handlers.titles.watch_titles import get_all_titles, get_title
from tg_bot.keyboards import (get_base_add_panel, get_category_panel,
                       get_confirm_title_panel, get_title_fix_panel,
                       get_watch_titles_panel, get_open_title_panel,
                       get_watchlist_confirm_panel,get_watch_watchlist_panel,
                       get_open_item_panel, get_account_actions_panel)
from tg_bot.utils import (push_to_history, get_updated_title, get_updated_item,
                          send_smart_message)
from tg_bot.handlers.watchlist.add_watchlist import WatchlistState
from tg_bot.handlers.watchlist.watch_watchlist import get_all_items

router = Router()

@router.callback_query(F.data == "to_start_menu")
async def to_start_menu(callback : types.CallbackQuery, state : FSMContext):
    await callback.answer()
    await get_start_menu(callback)
    await state.clear()

@router.callback_query(F.data == "to_back")
async def to_back(callback : types.CallbackQuery, state : FSMContext):

    await callback.answer()
    data = await state.get_data()
    history = data.get('history')

    if not history:
        await to_start_menu(callback, state)
        return

    last_panel = history.pop()
    await state.update_data(history=history)

    if last_panel == "CONFIRM_TITLE_PANEL":
        await callback.message.edit_text("check", reply_markup=get_confirm_title_panel())
    elif last_panel == "TITLE_STATE_WAITING_FOR_RATING":
        await callback.message.answer("write the rating for title", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_rating)
    elif last_panel == "TITLE_STATE_WAITING_FOR_REVIEW":
        await callback.message.answer("Write the review for title", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_review)
    elif last_panel == "TITLE_STATE_WAITING_FOR_YEAR_START":
        await callback.message.answer("Write title's start year", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_year_start)
    elif last_panel == "TITLE_STATE_WAITING_FOR_NAME":
        await state.set_state(TitleState.waiting_for_name)
        await callback.message.answer("Write the title's name",
                reply_markup=get_base_add_panel())
    elif last_panel == "TITLE_PANEL_ADD_CATEGORY":
        await callback.message.edit_text("Chose the title category",
                reply_markup=get_category_panel('title'))
    elif last_panel == "START_MENU":
        await to_start_menu(callback, state)
        await state.clear()
    elif last_panel == "TITLE_STATUS_PANEL":
        await callback.message.edit_text("status panel", reply_markup=get_title_status_panel())
    elif last_panel == "TITLE_STATE_WAITING_FOR_START_WATCH":
        await callback.message.answer("write date of start watch (for example 21.01.2026)",
                                      reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_start_watch)
    elif last_panel == "TITLE_STATE_WAITING_FOR_END_WATCH":
        await callback.message.answer("write date of end watch (for example 03.02.2026)",
                                      reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_end_watch)
    elif last_panel == "TITLE_STATE_WAITING_FOR_DIRECTOR":
        await callback.message.answer("Write the name of Director", reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_director)
    elif last_panel == "TITLE_CONFIRM_PANEL_FIX":
        await callback.message.edit_text("fix panel", reply_markup=get_title_fix_panel())
    elif last_panel == "TITLE_STATE_WAITING_FOR_YEAR_END":
        await callback.message.edit_text("Write the title's end year",
                                         reply_markup=get_base_add_panel())
        await state.set_state(TitleState.waiting_for_year_end)
    elif last_panel == "TITLE_CONFIRM_PANEL":
        await callback.message.edit_text("check", reply_markup=get_confirm_title_panel())
    elif last_panel.startswith("TITLES_WATCH_MENU_PAGE_"):
        titles = await get_all_titles(callback)
        page = int(last_panel.split('_')[4])
        await callback.message.edit_text(
            f"Titles Page {page}",
            reply_markup=get_watch_titles_panel(titles, page=page))
    elif last_panel.startswith("OPEN_TITLE_"):
        title_id = int(last_panel.split('_')[2])
        data = await state.get_data()
        title = await get_updated_title(state)
        await send_smart_message(callback.message, title['text'],
                        get_open_title_panel(title_id))
    elif last_panel.startswith("TITLE_UPDATE_PANEL_"):
        title_id = int(last_panel.split('_')[3])
        title = await get_updated_title(state)
        await send_smart_message(callback.message, title['text'], get_title_update_panel())
    elif last_panel == "WATCHLIST_PANEL_ADD_CATEGORY":
        await callback.message.edit_text("Chose the item's category",
                reply_markup=get_category_panel('watchlist'))
    elif last_panel == "WATCHLIST_STATE_WAITING_FOR_NAME":
        await callback.message.answer("Write the item's name",
                                      reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_name)
    elif last_panel == "WATCHLIST_STATE_WAITING_FOR_YEAR_START":
        await callback.message.answer("Write the start year of item",
                                        reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_year_start)
    elif last_panel == "WATCHLIST_CONFIRM_PANEL":
        await callback.message.edit_text('confirm panel', reply_markup=get_watchlist_confirm_panel())
    elif last_panel == "WATCHLIST_STATE_WAITING_FOR_LINK":
        await callback.message.answer("Write the item's link", reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_link)
    elif last_panel == "WATCHLIST_STATE_WAITING_FOR_NOTE":
        await callback.message.answer("Write your note", reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_note)
    elif last_panel == "WATCHLIST_STATE_WAITING_FOR_YEAR_END":
        await callback.message.answer("Write the item's end year",
                                      reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_year_end)
    elif last_panel == "WATCHLIST_STATE_WAITING_FOR_DIRECTOR":
        await callback.message.answer("Write the item's Director", reply_markup=get_base_add_panel())
        await state.set_state(WatchlistState.waiting_for_director)
    elif last_panel.startswith("WATCHLIST_WATCH_MENU_PAGE_"):
        items = await get_all_items(callback)
        page = int(last_panel.split('_')[4])
        await callback.message.edit_text(
            f"Watchlist Page {page}",
            reply_markup=get_watch_watchlist_panel(items, page=page))
    elif last_panel.startswith("OPEN_ITEM_"):
        item_id = int(last_panel.split('_')[2])
        data = await state.get_data()
        item = await get_updated_item(state)
        await callback.message.edit_text(item['text'], reply_markup=get_open_item_panel(item_id))
    elif last_panel.startswith("ITEM_UPDATE_PANEL_"):
        item_id = int(last_panel.split('_')[3])
        item = await get_updated_item(state)
        print('elif last_panel == "ITEM_UPDATE_PANEL_"')
        await callback.message.edit_text(item['text'],
                reply_markup=get_item_update_panel())
    elif last_panel == 'SHOW_ACCOUNT_ACTIONS':
        await callback.message.edit_text('Account actions', reply_markup=get_account_actions_panel())
