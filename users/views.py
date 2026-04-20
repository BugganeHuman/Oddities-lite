from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .models import User
from django.utils import timezone
from datetime import timedelta
from titles.models import Title
from titles.serializers import TitleSerializer
from watchlist.models import WatchlistItem
from watchlist.serializers import WatchlistItemSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
import users.authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class CorrectTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    #authentication_classes = [JWTAuthentication, users.authentication.BotAuthentication]



@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):

    return Response ({'status' : 'ok'})

@api_view(['GET'])
@authentication_classes([JWTAuthentication, users.authentication.BotAuthentication])
@permission_classes([IsAuthenticated])
def backup(request):
    user = request.user
    titles = list(Title.objects.filter(owner=user).values())
    watchlist = list(WatchlistItem.objects.filter(owner=user).values())
    now = datetime.now()
    time = now.strftime('%d.%m.%Y')
    data = {
        'username' : request.user.username,
        'titles' : titles,
        'watchlist' : watchlist,
        'timestamp' : time
    }
    return Response(data, status=200)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, users.authentication.BotAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
    try:
        user = request.user
        user.delete()
        user.save()
    except Exception as e:
        print(e)
    return Response({'status' : 'done'})

@api_view(['GET'])
@authentication_classes([JWTAuthentication, users.authentication.BotAuthentication])
@permission_classes([IsAuthenticated])
def get_user_visibility(request):
    titles_visibility = request.user.titles_is_public
    watchlist_visibility = request.user.watchlist_is_public
    return Response({
        'titles_is_public' : titles_visibility,
        'watchlist_is_public' : watchlist_visibility
    })

@api_view(['PUT'])
@authentication_classes([JWTAuthentication, users.authentication.BotAuthentication])
@permission_classes([IsAuthenticated])
def toggle_visibility(request):
    #password = request.data.get("password")
    titles_visibility = request.data.get("titles_visibility")
    watchlist_visibility = request.data.get("watchlist_visibility")
    user = request.user
    #print('-------WEB DEBAG-----')
    #if request.user.check_password(password):
    if titles_visibility == 'public' and not user.titles_is_public:
        user.titles_is_public = True
        user.save()
    elif titles_visibility == 'private' and user.titles_is_public:
        user.titles_is_public = False
        user.save()

    if watchlist_visibility == 'public' and not user.watchlist_is_public:
        user.watchlist_is_public = True
        user.save()
    elif watchlist_visibility == 'private' and user.watchlist_is_public:
        user.watchlist_is_public = False
        user.save()

    return Response({"status" : "done"})

    #return Response({"status": "error"})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_records(request):
    request_username = request.query_params.get('username')
    try:
        founded_username = User.objects.get(username=request_username)
    except Exception:
        return Response ({"status" : "nothing"})

    user_titles = {}
    if founded_username.titles_is_public:
        user_titles = TitleSerializer(Title.objects.filter(
            owner=founded_username.id), many=True).data

    user_watchlist = {}
    if founded_username.watchlist_is_public:
        user_watchlist = WatchlistItemSerializer(WatchlistItem.objects.filter(
            owner=founded_username.id), many=True).data

    result = {
        "titles" : user_titles,
        "watchlist" : user_watchlist
    }

    return Response(result)

@api_view(['GET'])
@authentication_classes([JWTAuthentication, users.authentication.BotAuthentication])
@permission_classes([IsAuthenticated])
def get_me(request):
    user = request.user

    username = user.username
    date_joined = user.date_joined
    user_id = user.id
    email = user.email


    def get_privacy_email(email_full):
        email_name = ""
        for chapter in email_full:
            if chapter == "@":
                break
            email_name += chapter
        result = (email_name[:len(email_name) // 2] +
            "*" * (len(email_full) - len(email_name[:len(email_name) // 2])))
        return result


    results = {
        "username" : username,
        "email" : get_privacy_email(email),
        "date_joined" : date_joined,
        "id" : user_id
    }

    return Response(results)



"""
Middleware → URL → Authentication → Permissions → View → Serializer → Database.
"""