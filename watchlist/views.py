from django.template.defaultfilters import upper
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import WatchlistItemSerializer
from .models import WatchlistItem
from titles.services import (get_id, get_director, get_year_end, get_overview,
                            get_runtime, get_seasons_and_episodes)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
import users.authentication


class WatchlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistItemSerializer
    queryset = WatchlistItem.objects.all()
    authentication_classes = [JWTAuthentication, users.authentication.BotAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return WatchlistItem.objects.filter(owner= self.request.user)

    def perform_create(self, serializer):
        item_name = self.request.data.get('name')
        year_start = self.request.data.get('year_start')
        year_end = self.request.data.get('year_end')
        director = self.request.data.get('director')
        synopsis = self.request.data.get('synopsis')
        runtime = self.request.data.get('runtime')
        seasons =  self.request.data.get('seasons')
        episodes = self.request.data.get('episodes')
        category = self.request.data.get('category')

        data = get_id(item_name, year_start)

        if category in ['VD', 'LG', 'READ', 'OTHER']:
            serializer.save(owner = self.request.user, year_end = year_end,
                        director = director, synopsis=synopsis, runtime=runtime,
                        seasons=seasons, episodes=episodes)
            return

        try:
            if not year_end:
                year_end = get_year_end(data)
        except Exception:
                pass

        try:
            if not director:
                director = get_director(data)
        except Exception:
            pass

        try:
            if not synopsis:
                synopsis = get_overview(data)
        except Exception:
            pass

        try:
            if data['media_type'] == 'movie' and not runtime:
                runtime = get_runtime(data)
        except Exception:
                pass

        try:
            if data['media_type'] == 'tv' and not seasons or episodes:
                if not seasons:
                    seasons = get_seasons_and_episodes(data)['seasons']
                if not episodes:
                    episodes = get_seasons_and_episodes(data)['episodes']
        except Exception:
                pass

        serializer.save(owner = self.request.user, year_end = year_end,
                        director = director, synopsis=synopsis, runtime=runtime,
                        seasons=seasons, episodes=episodes)


@api_view(['GET'])
def order_by(request):
    order = request.query_params.get('ordering')
    results = None
    if order == 'runtime':

        movies = WatchlistItem.objects.order_by('runtime')
        tv = WatchlistItem.objects.order_by('episodes')
        results = WatchlistItemSerializer(movies, many=True).data + WatchlistItemSerializer(tv, many=True).data

    if order == '-runtime':

        movies = WatchlistItem.objects.order_by('-runtime')
        tv = WatchlistItem.objects.order_by('-episodes')
        results = WatchlistItemSerializer(tv, many=True).data + WatchlistItemSerializer(movies, many=True).data

    if order in ['year_start', '-year_start']:
        results = WatchlistItem.objects.order_by(order)

    if order in ['SR', 'MV']:
        results = WatchlistItem.objects.filter(category=upper(order))



    if results:
        return Response(WatchlistItemSerializer(results, many=True).data)
    else:
        return Response({'status' : 'nothing to return'})
