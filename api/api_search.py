import requests
from typing import Dict, List
from config_data import config


def pars_film_data(movie_data: List[Dict]) -> List[Dict]:
    """
    Парсит данные о фильмах из ответа API.

    :param movie_data: Список словарей с данными о фильмах из API
    :type movie_data: List[Dict]
    :return: Список обработанных словарей с информацией о фильмах
    :rtype: List[Dict]
    """
    movies = []
    for movie in movie_data:
        movies.append({
            'movie_name': movie.get('name', 'Неизвестно'),
            'description': movie.get('description'),
            'rating': movie.get('rating', {}).get('kp'),
            'year': movie.get('year', 'нет года'),
            'genres': [genre.get('name', '') for genre in movie.get('genres', [])],
            'age_rating': movie.get('ageRating'),
            'poster_url': movie.get('poster', {}).get('url')
        })
    return movies


class SiteApiInterface:
    """
    Интерфейс для взаимодействия с API КиноПоиска.

    Предоставляет статические методы для поиска фильмов по названию
    и по жанру с фильтрацией по рейтингу.
    """
    """
    Интерфейс для взаимодействия с API КиноПоиска.

    Предоставляет статические методы для поиска фильмов по названию
    и по жанру с фильтрацией по рейтингу.
    """
    @staticmethod
    def find_film(query: str, limit: int = 5, page: int = 1) -> List[Dict]:
        """
        Поиск фильма через API КиноПоиска по названию.

        :param query: Поисковый запрос (название фильма)
        :type query: str
        :param limit: Количество результатов на одной странице (макс. 250)
        :type limit: int
        :param page: Номер страницы результатов
        :type page: int
        :return: Список словарей с информацией о фильмах
        :rtype: List[Dict]
        """
        """
        Поиск фильма через API KinoPoisk через /v1.4/movie/search
        """
        url = 'https://api.kinopoisk.dev/v1.4/movie/search'
        headers = {
            "accept": "application/json",
            "X-API-KEY": config.RAPID_API_KEY
        }

        params = {
            'query': query,
            'limit': limit,
            'page': page
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return pars_film_data(data.get('docs', []))
        except Exception as e:
            print(f"Ошибка при поиске фильма '{query}': {e}")
            return []

    @staticmethod
    def rating_search(genre: str, rating: str, limit: int = 10, page: int = 1) -> List[Dict]:
        """
        Поиск фильмов по жанру и рейтингу.

        :param genre: Название жанра (например, 'драма')
        :type genre: str
        :param rating: Рейтинг фильма (число или диапазон, например '7' или '7-10')
        :type rating: str
        :param limit: Количество результатов на одной странице
        :type limit: int
        :param page: Номер страницы результатов
        :type page: int
        :return: Список словарей с информацией о фильмах
        :rtype: List[Dict]
        """
        """
        Поиск фильмов по жанру и рейтингу.
        rating может быть:
        - '7'       → рейтинг == 7
        - '7-10'    → диапазон рейтингов 7–10
        """

        url = "https://api.kinopoisk.dev/v1.4/movie"
        headers = {
            "accept": "application/json",
            "X-API-KEY": config.RAPID_API_KEY
        }

        # Если рейтинг диапазон — оставляем как есть
        # Если одно число — сравнение строго по равенству (rating.kp=7)
        if "-" in rating:
            rating_filter = rating.strip()
        else:
            rating_filter = rating.strip()

        params = {
            "page": page,
            "limit": limit,
            "genres.name": genre,
            "rating.kp": rating_filter
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return pars_film_data(data.get("docs", []))
        except Exception as e:
            print(f"Ошибка при поиске по жанру '{genre}' и рейтингу '{rating}': {e}")
            return []
