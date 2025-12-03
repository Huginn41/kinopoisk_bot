
from database.core import crud, db, SearchHistory, WatchLater


def add_to_search_history(movies: list) -> None:
    """
    Добавляет фильмы в историю поиска.

    :param movies: Список фильмов для добавления
    :type movies: list
    """
    if not movies:
        return

    data_to_insert = []
    for movie in movies:
        data_to_insert.append({
            'movie_name': movie.get('movie_name'),
            'description': movie.get('description'),
            'rating': movie.get('rating'),
            'year': movie.get('year'),
            'genres': ', '.join(movie.get('genres', [])),
            'age_rating': movie.get('age_rating'),
            'poster_url': movie.get('poster_url')
        })

    crud.create()(db, SearchHistory, data_to_insert)


def add_to_watch_later(movie: dict) -> None:
    """
    Добавляет фильм в список "Буду смотреть".

    :param movie: Фильм для добавления
    :type movie: dict
    """
    data_to_insert = [{
        'movie_name': movie.get('movie_name'),
        'description': movie.get('description'),
        'rating': movie.get('rating'),
        'year': movie.get('year'),
        'genres': ', '.join(movie.get('genres', [])),
        'age_rating': movie.get('age_rating'),
        'poster_url': movie.get('poster_url')
    }]
    crud.create()(db, WatchLater, data_to_insert)
