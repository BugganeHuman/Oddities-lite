from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WatchlistItem(models.Model):

    class WatchlistItemCategory(models.TextChoices):
        MOVIE = "MV", "Movie"
        SERIES = "SR", "Series"
        ANIME = "ANM", "Anime"
        CARTOON = "CRT", "Cartoon"
        LEGAL = "LG", "Legal case"
        VIDEO = "VD", "Youtube video ot other"
        READING = "READ", "Written content"

    name = models.CharField(max_length=250)
    link = models.URLField(null=True, blank=True)
    note = models.TextField(null=True, blank=True, max_length=500)
    year_start = models.PositiveIntegerField()
    year_end = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=7,choices=WatchlistItemCategory.choices,
        default=WatchlistItemCategory.SERIES)
    director = models.CharField(max_length=150, null=True, blank=True)
    synopsis = models.TextField(max_length=2000, null=True, blank=True)
    runtime = models.PositiveIntegerField(help_text="run time in minutes for movie",
        null=True, blank=True)
    episodes = models.PositiveIntegerField(help_text="number of episodes for series",
        null=True, blank=True)
    seasons = models.PositiveIntegerField(help_text="number of seasons for series",
        null=True, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")