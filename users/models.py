from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    delete_date = models.DateTimeField(blank=True, null=True)
    titles_is_public = models.BooleanField(default=False)
    watchlist_is_public = models.BooleanField(default=False)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    is_king = models.BooleanField(blank=True, null=True, default=False)

"""

Регистрация: Данные (email/пароль) превращаются в строку в таблице users_user (пароль при этом хешируется).

Логин: Юзер шлет почту и пароль → получает JWT-токен («цифровой паспорт»). 'SimpleJWT проверяет: 
«Так, в таблице такой чел есть, пароль совпал». В ответ он кидает юзеру JWT-токен (тот самый access)'

Запрос: Юзер шлет токен в заголовке → Django узнает юзера и кладет его объект в request.user.

Связь (FK): При сохранении контента ты записываешь request.user в поле owner (в БД это ID юзера).

Приватность: Ты отдаешь данные через фильтр .filter(owner=request.user) — так каждый видит только своё.

"""
