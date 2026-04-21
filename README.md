# Oddities
### API Documentation -  https://oddities.onrender.com/api/docs/

### Telegram bot - @Oddities_Diary_Bot

### Main project with full readme - https://github.com/BugganeHuman/Oddities

## *Idea*
### *A lightweight version of the Oddities project, designed to run on resource-constrained platforms (Render Free Tier, budget VPS) without the use of Docker.*

### *Unlike the main version, the Lite version combines the web server and bot into a single process to save RAM and bypass the limitations of free plans.*



##  *Difference from the main Oddities*
- **Monolith architecture**: The API and Telegram bot operate in the same process..
- **Database**: PostgreSQL (Neon.tech).
- **Static**: WhiteNoise / Custom Serve.
- **API**: Render
- In this (light) version, redis and celery were cut, therefore, functions related to soft_delete_user were lost.


## *Install*
1. ```git clone https://github.com/BugganeHuman/Oddities-lite```
2. ```cd Oddities-lite```
3. for linux ```source venv/bin/activate```, for windows ```venv\Scripts\activate```
4. pip install -r requirements.txt
5. create secret.env, in example - example.env
6. ```python manage.py migrate```
7. ```python manage.py collectstatic --noinput```
8. ```python manage.py runserver 0.0.0.0:8000```

### Render Deploy

#### Build Command: ```pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput```

#### Start Command: ```gunicorn Oddities.wsgi:application```

#### Set up a cron job every 10 minutes to the /api/ping/ endpoint on cron-job.org