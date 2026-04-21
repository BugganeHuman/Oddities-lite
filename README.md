# Oddities
### API Documentation -  https://oddities.onrender.com/api/docs/

### Telegram bot - @Oddities_Diary_Bot

### Main project with full readme - https://oddities.onrender.com/api/docs/

##  Difference from the main Oddities
- **Monolith architecture**: The API and Telegram bot operate in the same process..
- **Database**: PostgreSQL (Neon.tech).
- **Static**: WhiteNoise / Custom Serve.
- **API**: Render
- In this (light) version, redis and celery were cut, therefore, functions related to soft_delete_user were lost.