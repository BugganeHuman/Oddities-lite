from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder



def get_start_panel():
    builder = InlineKeyboardBuilder()
    """
    builder.row(
        types.InlineKeyboardButton(text="📝 Add Title", callback_data="add_title"),
        types.InlineKeyboardButton(text="🗂️ Open Titles", callback_data="open_titles")
    )
    builder.row(
        types.InlineKeyboardButton(text="📌 Add Watchlist Item", callback_data="add_watchlist_item"),
        types.InlineKeyboardButton(text="🗒️ Open Watchlist", callback_data="open_watchlist")
    )
    builder.row (
        types.InlineKeyboardButton(text="⚙️ Account Actions", callback_data="account_actions")
    )
    """
    builder.row(
        types.InlineKeyboardButton(text="📝 Add Title", callback_data="add_title")
    )
    builder.row(
        types.InlineKeyboardButton(text="🗂️ Open Titles", callback_data="open_titles")
    )
    builder.row(
        types.InlineKeyboardButton(text="📌 Add Watchlist Item", callback_data="add_watchlist_item")
    )
    builder.row(
        types.InlineKeyboardButton(text="🗒️ Open Watchlist", callback_data="open_watchlist")
    )
    builder.row (
        types.InlineKeyboardButton(text="⚙️ Account Actions", callback_data="account_actions")
    )

    return builder.as_markup()

def get_base_add_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )

    return builder.as_markup()

def get_category_panel(kind):
    builder = InlineKeyboardBuilder()
    if kind == "title":
        kind = "title"
    elif kind == "watchlist":
        kind = "watchlist"
    else:
        raise ValueError (f"type - {kind} not for get_category_panel")

    builder.row(
        types.InlineKeyboardButton(text= "🎬 Movie", callback_data=f"{kind}_category_movie")
    )
    builder.row(
        types.InlineKeyboardButton(text="📺 TV-Series", callback_data=f"{kind}_category_series")
    )
    builder.row(
        types.InlineKeyboardButton(text="⛩️ Anime", callback_data=f"{kind}_category_anime")
    )
    builder.row(
        types.InlineKeyboardButton(text="🎨 Cartoon", callback_data=f"{kind}_category_cartoon")
    )
    builder.row(
        types.InlineKeyboardButton(text="🔴 Video",
                callback_data=f"{kind}_category_video")
    )
    builder.row(
        types.InlineKeyboardButton(text="⚖️ Legal case", callback_data=f"{kind}_category_legal_case")
    )
    builder.row(
        types.InlineKeyboardButton(text="📝 Written content", callback_data=f"{kind}_category_written_content")
    )
    builder.row(
        types.InlineKeyboardButton(text="🌀 Other", callback_data=f"{kind}_category_other")
    )

    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_confirm_title_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="🚩 Status", callback_data="title_confirm_panel_status")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏁 Start Watch", callback_data="title_confirm_panel_start_watch"),
        types.InlineKeyboardButton(text="🏆 End Watch", callback_data="title_confirm_panel_end_watch")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="🛠 Fix", callback_data="title_confirm_panel_fix"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    builder.row(
        types.InlineKeyboardButton(text="💾 Save", callback_data="confirm_title_panel_save")
    )

    return builder.as_markup()

def get_title_fix_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="🎥 Director", callback_data="title_fix_panel_director"),
        types.InlineKeyboardButton(text="📆 End Year", callback_data="title_fix_panel_year_end")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_title_status_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="✅ DONE", callback_data="title_status_panel_DONE")
    )
    builder.row(
        types.InlineKeyboardButton(text="🗑 DROPPED", callback_data="title_status_panel_DROPPED")
    )
    builder.row(
        types.InlineKeyboardButton(text="⏳ REVISIT or will FINISH", callback_data="title_status_panel_REVISIT")
    )
    builder.row(
        types.InlineKeyboardButton(text="🍿 WATCHING", callback_data="title_status_panel_WATCHING")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_watch_titles_panel(titles_dict, page: int = 0):
    builder = InlineKeyboardBuilder()
    ITEMS_PER_PAGE = 9
    items = list(titles_dict.items())
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    # Берем только нужную пачку (например, с 0 по 10)
    current_page_items = items[start_index:end_index]

    # Кнопки с названиями фильмов
    for item_id, data in current_page_items:
        builder.row(types.InlineKeyboardButton(
            text=f"{data['name']} |  {data['rating']}",
            callback_data=f"open_title_{item_id}_page_{page}"
        ))

    # Кнопки навигации (Вперед/Назад)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text="⬅️ back",
                callback_data=f"open_titles_page_{page - 1}"))

    if end_index < len(items):
        nav_buttons.append(types.InlineKeyboardButton(text="next➡️",
                callback_data=f"open_titles_page_{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu")
    )

    return builder.as_markup()

def get_open_title_panel(title_id):
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="❌ Delete", callback_data=f"confirm_delete_title_{title_id}"),
        types.InlineKeyboardButton(text="✏️ Update", callback_data=f"panel_update_title_{title_id}")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_title_update_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text='⭐ Rating', callback_data='update_title_rating'),
        types.InlineKeyboardButton(text='💬 Review', callback_data='update_title_review')
    )
    builder.row(
        types.InlineKeyboardButton(text='🏁 Start Watch', callback_data="update_title_start_watch"),
        types.InlineKeyboardButton(text='🏆 End Watch', callback_data="update_title_end_watch")
    )
    builder.row(
        types.InlineKeyboardButton(text='📂 Category', callback_data="update_title_category"),
        types.InlineKeyboardButton(text="🚩 Status", callback_data="update_title_status")
    )
    builder.row(
        types.InlineKeyboardButton(text='🎥 Director', callback_data="update_title_director"),
        types.InlineKeyboardButton(text='🏷️ Name', callback_data='update_title_name')
    )
    builder.row(
        types.InlineKeyboardButton(text="📅 Start Year", callback_data="update_title_year_start"),
        types.InlineKeyboardButton(text='🗓️ End Year', callback_data="update_title_year_end")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    builder.row(
        types.InlineKeyboardButton(text="💾 Save", callback_data="save_updated_title")
    )
    return builder.as_markup()

def get_confirm_delete_panel(element_id, kind):
    if kind == 'title':
        pass
    elif kind == 'item':
        pass
    else:
        raise ValueError (f"kind='{kind}', kind may be only 'title' or 'item'")

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text=f'💀 Yes I want delete this {kind}',
                callback_data=f'delete_{kind}_{element_id}'),
        types.InlineKeyboardButton(text="🛡️ No I don't want delete ", callback_data='to_back')
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_watchlist_confirm_panel():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔗 Link", callback_data="watchlist_confirm_panel_link"),
        types.InlineKeyboardButton(text="🗒 Note", callback_data="watchlist_confirm_panel_note")
    )
    builder.row(
        types.InlineKeyboardButton(text="🗓️ End Year", callback_data="watchlist_confirm_panel_year_end"),
        types.InlineKeyboardButton(text="🎥 Director", callback_data="watchlist_confirm_panel_director")
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    builder.row(
        types.InlineKeyboardButton(text="💾 Save", callback_data="confirm_watchlist_panel_save")
    )
    return builder.as_markup()

def get_watch_watchlist_panel(items_dict, page: int = 0):
    builder = InlineKeyboardBuilder()
    ITEMS_PER_PAGE = 9
    items = list(items_dict.items())
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    # Берем только нужную пачку (например, с 0 по 10)
    current_page_items = items[start_index:end_index]

    # Кнопки с названиями фильмов
    for item_id, data in current_page_items:
        builder.row(types.InlineKeyboardButton(
            text=f"{data['name']} |  {data['year_start']}",
            callback_data=f"open_item_{item_id}_page_{page}"
        ))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text="⬅️ back",
                callback_data=f"open_watchlist_page_{page - 1}"))

    if end_index < len(items):
        nav_buttons.append(types.InlineKeyboardButton(text="next➡️",
                callback_data=f"open_watchlist_page_{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu")
    )

    return builder.as_markup()

def get_open_item_panel(item_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="❌ Delete", callback_data=f"confirm_delete_item_{item_id}"),
        types.InlineKeyboardButton(text="✏️ Update", callback_data=f"panel_update_item_{item_id}"),
        types.InlineKeyboardButton(text="✅ Rate", callback_data=f'rate_item_{item_id}')
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_item_update_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text='📂 Category', callback_data='update_item_category'),
        types.InlineKeyboardButton(text='🏷️ Name', callback_data='update_item_name')
    )
    builder.row(
        types.InlineKeyboardButton(text='🔗 Link', callback_data='update_item_link'),
        types.InlineKeyboardButton(text='🗒 Note', callback_data='update_item_note')
    )
    builder.row(
        types.InlineKeyboardButton(text='📜 Synopsis', callback_data='update_item_synopsis'),
        types.InlineKeyboardButton(text='🎥 Director', callback_data='update_item_director')
    )
    builder.row(
        types.InlineKeyboardButton(text='📅 Start Year', callback_data='update_item_year_start'),
        types.InlineKeyboardButton(text='🗓️ End Year', callback_data='update_item_year_end')
    )
    builder.row(
        types.InlineKeyboardButton(text='📀 Seasons', callback_data='update_item_seasons'),
        types.InlineKeyboardButton(text='🎞 Episodes', callback_data='update_item_episodes'),
        types.InlineKeyboardButton(text='⏱ Runtime', callback_data='update_item_runtime')
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    builder.row(
        types.InlineKeyboardButton(text="💾 Save", callback_data="save_updated_item")
    )
    
    return builder.as_markup()

def get_account_actions_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text='👤 User Info', callback_data='user_me')
    )
    builder.row(
        types.InlineKeyboardButton(text='🔑 Show Password', callback_data='user_show_password')
    )
    builder.row(
        types.InlineKeyboardButton(text='👁‍ Toggle Visibility', callback_data='user_toggle_visibility')
    )
    builder.row(
        types.InlineKeyboardButton(text='⚰️ Delete Account', callback_data='user_delete_account')
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu")
    )
    return builder.as_markup()

def get_toggle_visibility_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text='🌐 Do Titles is PUBLIC',
                callback_data='toggle_visibility_titles_public'),
        types.InlineKeyboardButton(text='🚫 Do Titles is PRIVATE',
                callback_data='toggle_visibility_titles_private')
    )
    builder.row(
        types.InlineKeyboardButton(text='🔓 Do Watchlist is PUBLIC',
                callback_data='toggle_visibility_watchlist_public'),
        types.InlineKeyboardButton(text='🔒 Do Watchlist is PRIVATE',
                callback_data='toggle_visibility_watchlist_private')
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    builder.row(
        types.InlineKeyboardButton(text="💾 Save", callback_data="save_updated_visibility")
    )

    return builder.as_markup()

def get_confirm_delete_user_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text=f'💀 Yes, delete this account',
                callback_data='delete_user'),
        types.InlineKeyboardButton(text="🛡️ No, back off", callback_data='to_back')
    )
    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu"),
        types.InlineKeyboardButton(text="⬅️ back", callback_data="to_back")
    )
    return builder.as_markup()

def get_home_btn_panel():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(text="🏠 Start Menu", callback_data="to_start_menu")
    )
    return builder.as_markup()