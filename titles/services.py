import requests
import os

TOKEN = os.getenv('TMDB_READ_ACCESS_TOKEN')
BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

def get_id(title_name, year=None):
    url = f"{BASE_URL}/search/multi"

    params = {
        "query" : title_name,
        "language" : "en-US"
    }
    if year:
        params["primary_release_year"] = year

    response = requests.get(url, headers=headers, params=params)
    results = response.json().get('results')

    if results:
        for title in results:
            date = title.get('release_date') or title.get('first_air_date')
            if date and date.startswith(str(year)):
                title_base_data = requests.get(f"{BASE_URL}/{title['media_type']}/{title['id']}",
                                                headers=headers).json()
                results = {
                    "title_id" : title['id'],
                    "media_type" : title['media_type'],
                    "title_base_data" : title_base_data
                }
                # возможно стоит так же возвращать джейсон /{data['media_type']}/{data['title_id']}
                # и реюзать в некоторых функциях
                return results

    return None

def get_cover(data):
    print("executing get_cover")

    result = data['title_base_data'].get("poster_path")

    if result:
            cover = f"https://image.tmdb.org/t/p/w500{result}"
            print(cover)
            return cover
    print("in get_cover None")
    return None

def get_director(data):
    print("executing get_director")

    if data["media_type"] == 'movie':
        url = f"{BASE_URL}/movie/{data['title_id']}/credits"
        response = requests.get(url, headers=headers).json()
        for person in response.get('crew', []):
            if person.get("job") == 'Director':
                return person.get("name")

    if data["media_type"] == 'tv':
        url = f"{BASE_URL}/tv/{data['title_id']}"
        response = requests.get(url, headers=headers).json()
        creators = response.get('created_by', [])
        if creators:
            print(creators[0]['name'])
            return creators[0]['name']

    return 'Unknown'

def get_year_end(data):
    if data['media_type'] == 'tv':
        year_end = data['title_base_data'].get('last_air_date')
        if year_end:
            return year_end[:4]

    return None

def get_overview(data):
    overview = data['title_base_data'].get('overview')

    if overview:
        return overview

    return None

def get_runtime(data):
    if data['media_type'] == 'movie':
        run_time = data['title_base_data'].get('runtime')

        if run_time:
            return run_time

    return None

def get_seasons_and_episodes(data):
    print("executing get_seasons_and_episodes")
    seasons = data['title_base_data'].get('number_of_seasons')
    episodes = data['title_base_data'].get('number_of_episodes')

    if seasons and episodes:
        volume = {
            'seasons' : seasons,
            'episodes' : episodes
        }
        print(volume)
        return volume

    return None