from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from typing import Union
import re
import os
import aiohttp
from datetime import datetime

async def delete_last(state : FSMContext):
    data = await state.get_data()
    history = data.get('history', [])
    print(history)
    history.pop()
    await state.update_data(history=history)
    print(history)

async def push_to_history(state : FSMContext, screen_id : str):
    data = await state.get_data()
    history = data.get('history', [])
    history.append(screen_id)
    print("---------DEBAG---------")
    print(history)
    await state.update_data(history=history)

async def get_title_text(state):
    statuses = {
        "title_status_panel_DONE" : "DONE",
        "title_status_panel_DROPPED" : "DROP",
        "title_status_panel_REVISIT" : "RVS",
        "title_status_panel_WATCHING" : "WATCH"
    }
    state_data = await state.get_data()

    name = state_data.get("title_name")
    review = state_data.get("title_review")
    rating = state_data.get("title_rating")
    year_start = state_data.get("title_year_start")
    year_end = state_data.get("title_year_end")
    director = state_data.get("title_director")
    start_watch = state_data.get("title_start_watch")
    end_watch = state_data.get("title_end_watch")
    category = ""
    status = ""

    text = (f"{name}  {year_start} | {category}\n"
            f"rating - {rating}\n\n"
            f"_____________________________________________________\n"
            f"{review}\n"
            f"_____________________________________________________\n\n"
            )

    if "title_director" in state_data:
        text += f"Director - {director}\n"
    if "title_start_watch" in state_data:
        text += f"Start watch - {start_watch}\n"
    if "title_end_watch" in state_data:
        text += f"End watch - {end_watch}\n"
    if "title_year_end" in state_data:
        text += f"End year - {year_end}\n"
    if "title_status" in state_data:
        status = statuses[state_data['title_status']]
        text += f"Status - {status}\n"

    return text


async def get_updated_title(state: FSMContext):

    statuses = {
        "title_status_panel_DONE" : "DONE",
        "title_status_panel_DROPPED" : "DROP",
        "title_status_panel_REVISIT" : "RVS",
        "title_status_panel_WATCHING" : "WATCH"
    }

    updated = {}

    state_data = await state.get_data()

    title_id = state_data.get('title_id')
    title_data = state_data.get('title_data')
    title = title_data['title_data']

    name = state_data.get("title_name", title['name'])
    review = state_data.get("title_review", title['review'])
    rating = state_data.get("title_rating", title['rating'])
    year_start = state_data.get("title_year_start", title['year_start'])
    year_end = state_data.get("title_year_end", title['year_end'])
    category = ""
    status = ""
    if "title_category" in state_data:
        category = state_data["title_category"]
        updated['category'] = category
    else:
        category = title['category']
    if "title_status" in state_data:
        status = statuses[state_data['title_status']]
        updated['status'] = status
    else:
        status = title['status']
    director = state_data.get("title_director", title['director'])
    start_watch = state_data.get("title_start_watch", title['start_watch'])
    end_watch = state_data.get("title_end_watch", title['end_watch'])

    text = (f"{name}  {year_start} | {category}\n"
            f"rating - {rating}\n\n"
            f"_____________________________________________________\n"
            f"{review}\n"
            f"_____________________________________________________\n\n"
            )

    if "title_director" in state_data or title['director']:
        updated['director'] = director
        text += f"Director - {director}\n"
    if "title_start_watch" in state_data or title['start_watch']:
        date = datetime.strptime(str(start_watch), '%d.%m.%Y').date()
        updated['start_watch'] = date.strftime('%Y-%m-%d')
        text += f"Start watch - {start_watch}\n"
    if "title_end_watch" in state_data or title['end_watch']:
        date = datetime.strptime(str(end_watch), '%d.%m.%Y').date()
        updated['end_watch'] = date.strftime('%Y-%m-%d')
        text += f"End watch - {end_watch}\n"
    if "title_year_end" in state_data or title['year_end']:
        updated['year_end'] = year_end
        text += f"End year - {year_end}\n"
    if "title_status" in state_data or title['status']:
        try:
            status = statuses[state_data['title_status']]
        except Exception:
            status = title['status']
        text += f"Status - {status}\n"
    if "title_name" in state_data:
        updated['name'] = name
    if "title_rating" in state_data:
        updated['rating'] = rating
    if "title_year_start" in state_data:
        updated['year_start'] = year_start
    if "title_review" in state_data:
        updated['review'] = review

    result = {
        "text" : str(text),
        "updated" : updated
    }
    return result




async def get_updated_item(state: FSMContext):
    updated = {}
    state_data = await state.get_data()
    item_data = state_data['item_data']
    item = item_data['data']

    name = state_data.get('item_name', item['name'])
    category = state_data.get('item_category', item['category'])
    year_start = state_data.get('item_year_start', item['year_start'])
    year_end = state_data.get('item_year_end', item['year_end'])
    link = state_data.get('item_link', item['link'])
    director = state_data.get('item_director', item['director'])
    note = state_data.get('item_note', item['note'])
    synopsis = state_data.get('item_synopsis', item['synopsis'])
    runtime = state_data.get('item_runtime', item['runtime'])
    episodes = state_data.get('item_episodes', item['episodes'])
    seasons = state_data.get('item_seasons', item['seasons'])

    text = f"{name} |  {year_start}  |  {category}\n\n"

    if synopsis:
        text += f"{synopsis}\n\n"
    if director:
        text += f"Director - {director}\n"
    if year_end:
        text += f"End Year - {year_end}\n"
    if runtime:
        text += f"Runtime - {runtime}\n"
    if seasons:
        text += f"Seasons - {seasons}\n"
    if episodes:
        text += f"Episodes - {episodes}\n\n"
    if note:
        text += f"Note - {note}\n"
    if link:
        text += f"Link - {link}\n"

    if "item_name" in state_data:
        updated['name'] = name
    if "item_director" in state_data:
        updated['director'] = director
    if "item_year_start" in state_data:
        updated['year_start'] = year_start
    if "item_year_end" in state_data:
        updated['year_end'] = year_end
    if "item_link" in state_data:
        updated['link'] = link
    if "item_note" in state_data:
        updated['note'] = note
    if "item_category" in state_data:
        updated['category'] = category
    if "item_synopsis" in state_data:
        updated['synopsis'] = synopsis
    if "item_runtime" in state_data:
        updated['runtime'] = runtime
    if "item_episodes" in state_data:
        updated['episodes'] = episodes
    if "item_seasons" in state_data:
        updated['seasons'] = seasons

    data = {
        'name' : name,
        'year_start' : year_start,
        'category' : category,
        'year_end' : year_end,
        'link' : link,
        'note' : note,
        'synopsis' : synopsis,
        'director' : director,
        'seasons' : seasons,
        'episodes' : episodes,
        'runtime' : runtime
    }

    result = {
        'data' : data,
        'text' : str(text),
        'updated' : updated
    }
    return result


def is_url_for_db(text: str) -> bool:
    if not text.startswith(('http://', 'https://')):
        return False
    url_pattern = re.compile(
        r'^https?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' 
        r'localhost|'  
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'  
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(text))

async def delete_rated_item(callback : types.CallbackQuery, state : FSMContext):
    data = await state.get_data()

    is_was_item = data.get('is_was_item', False)
    item_id = data.get('item_id')
    url = f"http://web:8000/api/watchlist/item/{item_id}/"

    headers = {
        "X-Bot-Key": str(os.getenv("BOT_MASTER_KEY")),
        "X-Telegram-Id": str(callback.from_user.id),
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(url, headers=headers) as response:
                pass
        except Exception as e:
            print(e)

async def send_smart_message(message, text, reply_markup=None):
    if len(text) <= 4090:
        return await message.answer(text, reply_markup=reply_markup)

    chunks = [text[i:i + 4090] for i in range(0, len(text), 4090)]
    for chunk in chunks[:-1]:
        await message.answer(chunk)

    return await message.answer(chunks[-1], reply_markup=reply_markup)