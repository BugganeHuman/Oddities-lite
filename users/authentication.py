from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class BotAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        bot_key = request.META.get('HTTP_X_BOT_KEY')
        tg_id = request.META.get('HTTP_X_TELEGRAM_ID')

        if not bot_key or bot_key != settings.BOT_MASTER_KEY:
            return None

        try:
            user = User.objects.get(telegram_id=int(tg_id))
            return (user, None)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')