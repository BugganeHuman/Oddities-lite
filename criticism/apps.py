import threading
import os
from django.apps import AppConfig


class CriticismConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'criticism'

    def ready(self):
        # Проверка RUN_MAIN обязательна, чтобы бот не запустился дважды
        # во время авто-перезагрузки сервера (авторелоада)
        if not os.environ.get('RUN_MAIN') == 'false':
            # Импортируем внутри метода, чтобы избежать круговых импортов
            # Если файл с ботом лежит в корне папки criticism, то пишем так:
            from tg_bot.bot_main import start_bot_thread

            # Создаем и запускаем отдельный поток для бота
            thread = threading.Thread(target=start_bot_thread, daemon=True)
            thread.start()
            print("--- Telegram Bot has been launched inside the Django process ---")