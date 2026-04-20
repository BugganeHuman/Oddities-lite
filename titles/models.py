from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

User = get_user_model()


def rating_validator(value):
    if value % Decimal("0.5") != 0:
        raise ValidationError ("the rating must be a multiple of 0.5, for example 6 or 6.5")



class Title(models.Model):

    class TitleCategory(models.TextChoices):
        MOVIE = "MV", "Movie"
        SERIES = "SR", "Series"
        ANIME = "ANM", "Anime"
        CARTOON = "CRT", "Cartoon"
        LEGAL = "LG", "Legal case"
        VIDEO = "VD", "Youtube video ot other"
        READING = "READ", "Written content"
        OTHER = "OTHER", "Other"

    class TitleStatus(models.TextChoices):
        DONE = "DONE", "Done"
        DROPPED = "DROP", "Dropped"
        REVISIT = "RVS", "Revisit or Finish"
        WATCHING = "WATCH", "Watching"

    name = models.CharField(max_length=300)
    year_start = models.IntegerField()
    year_end = models.IntegerField(null=True, blank=True)
    director = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=7, choices=TitleCategory.choices,
        default=TitleCategory.MOVIE)
    cover = models.URLField(null=True, blank=True)
    start_watch = models.DateField(null=True, blank=True)
    end_watch = models.DateField(default=date.today)
    status = models.CharField(max_length=5, choices=TitleStatus.choices, default=TitleStatus.DONE)
    review = models.TextField(null=True, blank=True, max_length=100000)
    rating = models.DecimalField(max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10), rating_validator])

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="titles")
